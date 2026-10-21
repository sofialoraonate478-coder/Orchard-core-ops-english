from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, TransactionReport, Ticket
from functools import wraps
from modules.kpi_utils import (
    TODAS_LAS_EMPRESAS, EMPRESAS_CON_CONR, kpis_for_empresa, compute_company_kpis,
)

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_staff():
    return session.get('rol') in ('admin', 'tecnico')

TIPOS = {
    'cus_s':   'Cus. S. Transaction',
    'tech_s':  'Tech S. Transaction',
    'mark':    'Mark. Transaction',
    'finance': 'F&Accou. Transaction',
}

# Qué empresas pertenecen a cada campaña (tipo de transacción)
TIPO_EMPRESAS = {
    'cus_s':   ['SPARK', 'BISSNISS', 'HALO MK.', 'CUSTOMER HUB'],  # todas
    'tech_s':  ['BISSNISS', 'SPARK'],
    'mark':    ['HALO MK.'],
    'finance': ['CUSTOMER HUB'],
}

KPIS = {
    'cus_s':   [
        {'key': 'CSAT',  'target': '≥ 90%',       'label': 'Customer Satisfaction (CSAT)'},
        {'key': 'AHT',   'target': '≤ 5 minutes',  'label': 'Average Handling Time (AHT)'},
        {'key': 'FCR',   'target': '≥ 70%',        'label': 'First Contact Resolution (FCR)'},
    ],
    'tech_s':  [
        {'key': 'FCR',           'target': '≥ 70%',         'label': 'First Contact Resolution (FCR)'},
        {'key': 'AHT',           'target': '≤ 5 minutes',   'label': 'Average Handling Time (AHT)'},
        {'key': 'CSAT',          'target': '≥ 85%',         'label': 'Customer Satisfaction (CSAT)'},
        {'key': 'SLA Compliance','target': '≤ 30 min',      'label': 'SLA Compliance'},
    ],
    'mark':    [
        {'key': 'CTR',             'target': '≥ 3%',   'label': 'Click Through Rate (CTR)'},
        {'key': 'Conversion Rate', 'target': '≥ 5%',   'label': 'Conversion Rate'},
        {'key': 'Engagement Rate', 'target': '≥ 10%',  'label': 'Engagement Rate'},
    ],
    'finance': [
        {'key': 'Accuracy Rate', 'target': '≥ 98%',              'label': 'Accuracy Rate'},
        {'key': 'TAT',           'target': '≤ 48 hours',         'label': 'Turnaround Time (TAT)'},
        {'key': 'SLA Compliance','target': 'Meet deadlines',      'label': 'SLA Compliance'},
    ],
}

@transactions_bp.route('/', methods=['GET'])
@login_required
def index():
    tipo = request.args.get('tipo', 'cus_s')
    empresa_filter = request.args.get('empresa', '')
    rol = session.get('rol')
    empresa_sesion = session.get('empresa', '')

    query = TransactionReport.query.filter_by(tipo=tipo)
    if rol == 'agente':
        query = query.filter_by(empresa=empresa_sesion)
    elif empresa_filter:
        query = query.filter_by(empresa=empresa_filter)

    reportes = query.order_by(TransactionReport.created_at.desc()).all()
    kpis = KPIS.get(tipo, [])

    # DATA ANALYTICS interactivo: se calcula en vivo con los reportes
    # (tickets/casos) ya registrados de la(s) empresa(s) visibles.
    if rol == 'agente':
        empresas_para_analytics = [empresa_sesion] if empresa_sesion else []
    elif empresa_filter:
        empresas_para_analytics = [empresa_filter]
    else:
        empresas_para_analytics = TIPO_EMPRESAS.get(tipo, [])

    data_analytics = [compute_company_kpis(emp, tipo=tipo) for emp in empresas_para_analytics]

    return render_template('transactions/index.html',
        tipo=tipo, tipos=TIPOS, reportes=reportes,
        kpis=kpis, empresa_filter=empresa_filter,
        empresas_disponibles=TIPO_EMPRESAS.get(tipo, []),
        data_analytics=data_analytics)

@transactions_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    tipo = request.args.get('tipo', request.form.get('tipo', 'cus_s'))
    if request.method == 'POST':
        tipo = request.form.get('tipo', 'cus_s')
        empresa = request.form.get('empresa') or session.get('empresa', 'SPARK')
        r = TransactionReport(
            empresa=empresa,
            tipo=tipo,
            customer_name=request.form.get('customer_name'),
            account_id=request.form.get('account_id'),
            contact_channel=request.form.get('contact_channel'),
            issue_type=request.form.get('issue_type'),
            resolution_status=request.form.get('resolution_status'),
            agent_name=request.form.get('agent_name'),
            kpi_check=request.form.get('kpi_check'),
            case_description=request.form.get('case_description'),
            campaign_name=request.form.get('campaign_name'),
            audience_segment=request.form.get('audience_segment'),
            channel=request.form.get('channel'),
            objective=request.form.get('objective'),
            transaction_type=request.form.get('transaction_type'),
            amount=request.form.get('amount'),
            currency=request.form.get('currency'),
            compliance_req=request.form.get('compliance_req'),
            call_status=request.form.get('call_status'),
            csat_response=request.form.get('csat_response') or None,
            nps_response=request.form.get('nps_response') or None,
            handle_time=request.form.get('handle_time') or None,
            offer_success=request.form.get('offer_success') or None,
            usuario_id=session['user_id'],
        )
        db.session.add(r)
        db.session.commit()
        flash('Transaction report saved', 'success')
        return redirect(url_for('transactions.index', tipo=tipo))

    return render_template('transactions/nuevo.html',
        tipo=tipo, tipos=TIPOS, kpis=KPIS.get(tipo, []),
        empresas_disponibles=TIPO_EMPRESAS.get(tipo, []),
        empresas_con_conr=EMPRESAS_CON_CONR)

@transactions_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if not is_staff():
        flash('No permission', 'danger')
        return redirect(url_for('transactions.index'))
    r = TransactionReport.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    flash('Report deleted', 'success')
    return redirect(url_for('transactions.index', tipo=r.tipo))

@transactions_bp.route('/kpis_dashboard')
@login_required
def kpis_dashboard():
    """Datos de KPIs (DATA ANALYTICS interactivo) por empresa — devuelve dict"""
    result = {}
    for emp in TODAS_LAS_EMPRESAS:
        reps = TransactionReport.query.filter_by(empresa=emp).all()
        total = len(reps)
        resueltos = len([r for r in reps if r.resolution_status and 'resolved' in r.resolution_status.lower()])
        analytics = compute_company_kpis(emp)
        result[emp] = {
            'total_reportes': total,
            'resueltos': resueltos,
            'tasa_resolucion': round(resueltos/total*100,1) if total else 0,
            'por_tipo': {t: len([r for r in reps if r.tipo==t]) for t in TIPOS},
            'data_analytics': analytics,
        }
    return result
