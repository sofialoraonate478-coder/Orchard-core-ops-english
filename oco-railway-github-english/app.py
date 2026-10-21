from flask import Flask
import os
import sys

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from models import db, User, TransactionReport

def create_app():
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'),
                static_folder=os.path.join(BASE_DIR, 'static'))
    app.config.from_object(Config)

    db.init_app(app)

    from modules.auth.routes import auth_bp
    from modules.tickets.routes import tickets_bp
    from modules.dashboard.routes import dashboard_bp
    from modules.reports.routes import reports_bp
    from modules.transactions.routes import transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(transactions_bp)

    # Display filters: stored values stay in Spanish, shown in English
    CATEGORIAS = {'Técnico': 'Technical', 'Facturación': 'Billing', 'Cuenta': 'Account', 'Otro': 'Other'}
    ROLES = {'admin': 'Admin', 'tecnico': 'Technician', 'agente': 'Agent'}

    @app.template_filter('categoria_label')
    def categoria_label(v):
        return CATEGORIAS.get(v, v)

    @app.template_filter('role_label')
    def role_label(v):
        return ROLES.get(v, (v or '').capitalize())

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    with app.app_context():
        db.create_all()
        from sqlalchemy import text

        # Migración automática: columna empresa en tickets
        with db.engine.connect() as conn:
            cols = [row[1] for row in conn.execute(text("PRAGMA table_info(tickets)")).fetchall()]
            if 'empresa' not in cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN empresa VARCHAR(50) NOT NULL DEFAULT 'SPARK'"))
                conn.commit()
                print('✅ Columna empresa agregada a tickets.')

            # Migración automática: columna call_status (transferida/finalizada) en tickets
            if 'call_status' not in cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN call_status VARCHAR(20)"))
                conn.commit()
                print('✅ Columna call_status agregada a tickets.')

            # Migración automática: columna empresa en users
            cols_users = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
            if 'empresa' not in cols_users:
                conn.execute(text("ALTER TABLE users ADD COLUMN empresa VARCHAR(50)"))
                conn.commit()
                print('✅ Columna empresa agregada a users.')

            # Migración automática: columnas de DATA ANALYTICS / llamada transferida
            # en transaction_reports (CSAT, NPS, AHT, CONR, transferida/finalizada)
            cols_tx = [row[1] for row in conn.execute(text("PRAGMA table_info(transaction_reports)")).fetchall()]
            tx_new_columns = {
                'call_status':    "VARCHAR(20)",
                'csat_response':  "INTEGER",
                'nps_response':   "INTEGER",
                'handle_time':    "INTEGER",
                'offer_success':  "VARCHAR(10)",
            }
            for col_name, col_type in tx_new_columns.items():
                if col_name not in cols_tx:
                    conn.execute(text(f"ALTER TABLE transaction_reports ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f'✅ Columna {col_name} agregada a transaction_reports.')

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@helpdesk.com', rol='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Usuario admin creado: admin / admin123')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
