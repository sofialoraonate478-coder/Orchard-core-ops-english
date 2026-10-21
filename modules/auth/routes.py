from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('rol') != 'admin':
        flash('Only administrators can create new accounts', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        rol      = request.form['rol']
        empresa  = request.form.get('empresa') if rol == 'agente' else None

        if rol not in ('tecnico', 'agente'):
            flash('Invalid role', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('That email is already registered', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('That username is already registered', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, rol=rol, empresa=empresa)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'{rol.capitalize()} account created successfully', 'success')
        return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id']  = user.id
            session['username'] = user.username
            session['rol']      = user.rol
            session['empresa']  = user.empresa
            flash('Welcome', 'success')
            return redirect(url_for('dashboard.index'))

        flash('Invalid credentials', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))
