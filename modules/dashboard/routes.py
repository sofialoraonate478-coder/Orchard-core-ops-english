from flask import Blueprint, render_template, session, redirect, url_for
from models import db, Ticket, TransactionReport
from modules.kpi_utils import compute_company_kpis

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

KPIS_INFO = {
    'cus_s':   [
        {'key': 'CSAT',  'target': '≥ 90%',      'label': 'CSAT'},
        {'key': 'AHT',   'target': '≤ 5 min',    'label': 'AHT'},
        {'key': 'FCR',   'target': '≥ 70%',       'label': 'FCR'},
    ],
    'tech_s':  [
        {'key': 'FCR',            'target': '≥ 70%',    'label': 'FCR'},
        {'key': 'AHT',            'target': '≤ 5 min',  'label': 'AHT'},
        {'key': 'CSAT',           'target': '≥ 85%',    'label': 'CSAT'},
        {'key': 'SLA Compliance', 'target': '≤ 30 min', 'label': 'SLA'},
    ],
    'mark':    [
        {'key': 'CTR',             'target': '≥ 3%',  'label': 'CTR'},
        {'key': 'Conversion Rate', 'target': '≥ 5%',  'label': 'Conversion'},
        {'key': 'Engagement Rate', 'target': '≥ 10%', 'label': 'Engagement'},
    ],
    'finance': [
        {'key': 'Accuracy Rate', 'target': '≥ 98%',         'label': 'Accuracy'},
        {'key': 'TAT',           'target': '≤ 48 h',        'label': 'TAT'},
        {'key': 'SLA Compliance','target': 'Meet deadlines', 'label': 'SLA'},
    ],
}

EMPRESA_TIPO = {
    'SPARK':        'tech_s',
    'BISSNISS':     'tech_s',
    'HALO MK.':     'mark',
    'CUSTOMER HUB': 'finance',
}

@dashboard_bp.route('/dashboard')
@login_required
def index():
    from sqlalchemy import func
    user_id = session['user_id']
    rol     = session.get('rol', 'agente')
    empresa = session.get('empresa', '')

    base = db.session.query(func.count(Ticket.id))
    if rol == 'agente':
        base = base.filter(Ticket.empresa == empresa)

    stats = {
        'abiertos':   base.filter(Ticket.estado == 'abierto').scalar(),
        'pendientes': base.filter(Ticket.estado.in_(['en_proceso','en proceso'])).scalar(),
        'cerrados':   base.filter(Ticket.estado == 'cerrado').scalar(),
        'urgencias':  base.filter(Ticket.prioridad == 'alta', Ticket.estado.in_(['abierto','en_proceso'])).scalar(),
    }

    # KPIs por empresa (solo admin ve todas; agente ve la suya)
    empresa_kpis = []
    if rol == 'admin':
        empresas = ['SPARK','BISSNISS','HALO MK.','CUSTOMER HUB']
    elif rol in ('tecnico',):
        empresas = ['SPARK','BISSNISS','HALO MK.','CUSTOMER HUB']
    else:
        empresas = [empresa] if empresa else []

    for emp in empresas:
        tipo = EMPRESA_TIPO.get(emp, 'cus_s')
        reps = TransactionReport.query.filter_by(empresa=emp).all()
        total_reps = len(reps)
        resueltos  = len([r for r in reps if r.resolution_status and 'resolved' in r.resolution_status.lower()])
        tasa = round(resueltos/total_reps*100, 1) if total_reps else 0
        empresa_kpis.append({
            'empresa':    emp,
            'tipo':       tipo,
            'kpis':       KPIS_INFO.get(tipo, []),
            'total_reps': total_reps,
            'resueltos':  resueltos,
            'tasa':       tasa,
            # DATA ANALYTICS interactivo: CSAT, NPS, FCR, AHT, CVOL (+CONR si aplica)
            'analytics':  compute_company_kpis(emp),
        })

    return render_template('dashboard/dashboard.html', stats=stats, empresa_kpis=empresa_kpis)
