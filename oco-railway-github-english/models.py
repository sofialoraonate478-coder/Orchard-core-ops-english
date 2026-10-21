from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol          = db.Column(db.String(20), default='agente')
    empresa      = db.Column(db.String(50), nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id          = db.Column(db.Integer, primary_key=True)
    titulo      = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria   = db.Column(db.String(80), nullable=False)
    prioridad   = db.Column(db.String(20), nullable=False)
    empresa     = db.Column(db.String(50), nullable=False, default='SPARK')
    estado      = db.Column(db.String(20), default='abierto')
    # Disposición de la llamada asociada al ticket: 'Transferida' o 'Finalizada'
    call_status = db.Column(db.String(20))
    usuario_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responses   = db.relationship('Response', backref='ticket', lazy=True)

class Response(db.Model):
    __tablename__ = 'responses'
    id         = db.Column(db.Integer, primary_key=True)
    ticket_id  = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contenido  = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship('User', backref='responses')

class TransactionReport(db.Model):
    __tablename__ = 'transaction_reports'
    id              = db.Column(db.Integer, primary_key=True)
    empresa         = db.Column(db.String(50), nullable=False)
    tipo            = db.Column(db.String(50), nullable=False)  # cus_s, tech_s, mark, finance
    customer_name   = db.Column(db.String(120))
    account_id      = db.Column(db.String(80))
    contact_channel = db.Column(db.String(80))
    issue_type      = db.Column(db.String(120))
    resolution_status = db.Column(db.String(50))
    agent_name      = db.Column(db.String(120))
    kpi_check       = db.Column(db.String(200))
    case_description= db.Column(db.Text)
    # Disposición de la llamada: 'Transferida' o 'Finalizada'
    call_status     = db.Column(db.String(20))
    # ENCUESTA DE SATISFACCIÓN — respuestas crudas del cliente; de aquí se
    # derivan los KPIs de CSAT y NPS (no se capturan como porcentaje directo)
    csat_response   = db.Column(db.Integer)   # 1 a 5 (satisfacción)
    nps_response    = db.Column(db.Integer)   # 0 a 10 (probabilidad de recomendar)
    handle_time     = db.Column(db.Integer)   # minutos invertidos en el caso (AHT)
    offer_success   = db.Column(db.String(10))# 'Si' / 'No' — oferta de producto/servicio (CONR)
    # Marketing extras
    campaign_name   = db.Column(db.String(120))
    audience_segment= db.Column(db.String(120))
    channel         = db.Column(db.String(120))
    objective       = db.Column(db.String(120))
    # Finance extras
    transaction_type= db.Column(db.String(120))
    amount          = db.Column(db.String(80))
    currency        = db.Column(db.String(30))
    compliance_req  = db.Column(db.String(120))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
