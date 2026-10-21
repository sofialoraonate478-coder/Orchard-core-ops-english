from flask import Blueprint, render_template, session, redirect, url_for
from models import Ticket, db
import json

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol') not in ('admin', 'tecnico'):
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@reports_bp.route('/')
@login_required
@admin_required
def index():
    rol = session.get('rol')
    tickets = Ticket.query.order_by(Ticket.created_at).all()
    total = len(tickets)

    # Evolución por fecha
    fechas = {}
    for t in tickets:
        if not t.created_at:
            continue
        fecha = t.created_at.strftime('%Y-%m-%d')
        fechas[fecha] = fechas.get(fecha, 0) + 1
    fechas_ordenadas = dict(sorted(fechas.items()))
    evolution_labels = list(fechas_ordenadas.keys())
    evolution_data   = list(fechas_ordenadas.values())

    # Distribución por estado
    estados_counter = {}
    for t in tickets:
        st = {'abierto': 'Open', 'en_proceso': 'In Progress', 'cerrado': 'Closed'}.get(t.estado, t.estado.capitalize())
        estados_counter[st] = estados_counter.get(st, 0) + 1
    estado_labels = list(estados_counter.keys())
    estado_data   = list(estados_counter.values())

    # Stats por empresa — solo admin ve el detalle por empresa
    empresa_stats = []
    empresa_labels = []
    empresa_data   = []
    if rol == 'admin':
        empresas = ['SPARK', 'BISSNISS', 'HALO MK.', 'CUSTOMER HUB']
        for emp in empresas:
            emp_tickets = [t for t in tickets if t.empresa == emp]
            total_emp = len(emp_tickets)
            cerrados_emp = len([t for t in emp_tickets if t.estado == 'cerrado'])
            eficiencia = round((cerrados_emp / total_emp * 100), 1) if total_emp > 0 else 0
            empresa_stats.append({
                'nombre': emp,
                'total': total_emp,
                'abiertos': len([t for t in emp_tickets if t.estado == 'abierto']),
                'en_proceso': len([t for t in emp_tickets if t.estado == 'en_proceso']),
                'cerrados': cerrados_emp,
                'eficiencia': eficiencia,
            })
        empresa_labels = [e['nombre'] for e in empresa_stats]
        empresa_data   = [e['total'] for e in empresa_stats]

    # Stats generales
    abiertos   = len([t for t in tickets if t.estado == 'abierto'])
    en_proceso = len([t for t in tickets if t.estado == 'en_proceso'])
    cerrados   = len([t for t in tickets if t.estado == 'cerrado'])
    eficiencia_global = round((cerrados / total * 100), 1) if total > 0 else 0

    return render_template(
        'reports/index.html',
        evolution_labels=json.dumps(evolution_labels),
        evolution_data=json.dumps(evolution_data),
        estado_labels=json.dumps(estado_labels),
        estado_data=json.dumps(estado_data),
        empresa_labels=json.dumps(empresa_labels),
        empresa_data=json.dumps(empresa_data),
        empresa_stats=empresa_stats,
        total=total,
        abiertos=abiertos,
        en_proceso=en_proceso,
        cerrados=cerrados,
        eficiencia_global=eficiencia_global,
        es_admin=(rol == 'admin'),
    )
