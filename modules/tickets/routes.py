from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Ticket, Response, User
from functools import wraps

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_staff():
    """Admin o técnico — tienen acceso amplio"""
    return session.get('rol') in ('admin', 'tecnico')

@tickets_bp.route('/')
@login_required
def list_tickets():
    user_id  = session['user_id']
    rol      = session.get('rol')
    empresa  = session.get('empresa')

    estado_filter    = request.args.get('estado')
    prioridad_filter = request.args.get('prioridad')
    empresa_filter   = request.args.get('empresa')

    query = Ticket.query

    if rol == 'agente':
        # Agente solo ve tickets de su empresa
        query = query.filter_by(empresa=empresa)
    # Tecnico y admin ven todos

    if estado_filter:
        query = query.filter_by(estado=estado_filter)
    if prioridad_filter:
        query = query.filter_by(prioridad=prioridad_filter)
    if empresa_filter and is_staff():
        query = query.filter_by(empresa=empresa_filter)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets/list.html', tickets=tickets,
                           current_estado=estado_filter,
                           current_prioridad=prioridad_filter,
                           current_empresa=empresa_filter)

@tickets_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        new_ticket = Ticket(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            categoria=request.form['categoria'],
            prioridad=request.form['prioridad'],
            empresa=request.form['empresa'],
            call_status=request.form.get('call_status'),
            usuario_id=session['user_id']
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash('Ticket created successfully', 'success')
        return redirect(url_for('tickets.list_tickets'))
    return render_template('tickets/create.html')

@tickets_bp.route('/ver/<int:id>', methods=['GET', 'POST'])
@login_required
def view_ticket(id):
    ticket = Ticket.query.get_or_404(id)

    if request.method == 'POST':
        if request.form.get('action') == 'cambiar_estado' and is_staff():
            ticket.estado = request.form.get('estado')
            db.session.commit()
            flash('Status updated', 'success')
            return redirect(url_for('dashboard.index'))

        elif request.form.get('action') == 'responder':
            contenido = request.form.get('contenido', '').strip()
            if contenido:
                resp = Response(
                    ticket_id=id,
                    usuario_id=session['user_id'],
                    contenido=contenido
                )
                db.session.add(resp)
                db.session.commit()
                flash('Reply sent', 'success')

    return render_template('tickets/view.html', ticket=ticket)

@tickets_bp.route('/status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    if not is_staff():
        flash('You do not have permission to change the status', 'danger')
        return redirect(url_for('tickets.list_tickets'))

    ticket = Ticket.query.get_or_404(id)
    ticket.estado = request.form.get('estado')
    db.session.commit()
    flash('Status updated', 'success')
    return redirect(url_for('tickets.list_tickets'))

@tickets_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def delete_ticket(id):
    if not is_staff():
        flash('You do not have permission to delete tickets', 'danger')
        return redirect(url_for('tickets.list_tickets'))

    ticket = Ticket.query.get_or_404(id)
    Response.query.filter_by(ticket_id=id).delete()
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted successfully', 'success')
    return redirect(url_for('tickets.list_tickets'))
