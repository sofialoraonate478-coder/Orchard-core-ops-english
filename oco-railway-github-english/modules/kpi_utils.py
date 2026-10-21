"""
KPI_UTILS
=========
Lógica centralizada de "DATA ANALYTICS": definiciones de KPIs, umbrales de
calificación y cálculo en vivo a partir de los reportes (TransactionReport)
que los agentes van registrando. Esto es lo que hace que los KPIs sean
INTERACTIVOS: entre más tickets/reportes se llenen, los porcentajes se
recalculan automáticamente.
"""
from models import TransactionReport

# Empresas que además de DATA ANALYTICS tienen el KPI extra CONR
EMPRESAS_CON_CONR = ['HALO MK.', 'CUSTOMER HUB']

TODAS_LAS_EMPRESAS = ['SPARK', 'BISSNISS', 'HALO MK.', 'CUSTOMER HUB']

# Definición base — aplica a TODAS las empresas
DATA_ANALYTICS_KPIS = [
    {
        'key': 'CSAT',
        'label': 'Customer Satisfaction',
        'desc': 'Survey results',
        'unit': '%',
    },
    {
        'key': 'NPS',
        'label': 'Net Promoter Score',
        'desc': 'Survey results',
        'unit': '',
    },
    {
        'key': 'FCR',
        'label': 'First Contact Resolution',
        'desc': 'Case closed at first contact',
        'unit': '%',
    },
    {
        'key': 'AHT',
        'label': 'Average Handling Time',
        'desc': 'Established time to answer a case',
        'unit': ' min',
    },
    {
        'key': 'CVOL',
        'label': 'Case Volume',
        'desc': 'Total amount during a certain period. BRIEF',
        'unit': '',
    },
]

CONR_KPI = {
    'key': 'CONR',
    'label': 'Conversion Rate',
    'desc': 'Succeeded product or service offer',
    'unit': '%',
}


def kpis_for_empresa(empresa):
    """Devuelve la lista de KPIs (DATA ANALYTICS + CONR si aplica) para una empresa."""
    kpis = list(DATA_ANALYTICS_KPIS)
    if empresa in EMPRESAS_CON_CONR:
        kpis = kpis + [CONR_KPI]
    return kpis


def _avg(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def rate_csat(value):
    if value is None:
        return None, '--'
    if value < 70:
        return 'low', 'NEEDS IMPROVEMENT'
    if value <= 85:
        return 'strong', 'STRONG'
    return 'excellent', 'EXCELLENT'


def rate_nps(value):
    if value is None:
        return None, '--'
    if value <= 0:
        return 'low', 'NEEDS IMPROVEMENT'
    if value <= 20:
        return 'good', 'GOOD'
    if value <= 60:
        return 'favorable', 'FAVORABLE'
    if value <= 80:
        return 'excellent', 'EXCELLENT'
    return 'world-class', 'WORLD CLASS'


def rate_fcr(value):
    if value is None:
        return None, '--'
    if value < 70:
        return 'low', 'BELOW TARGET'
    if value <= 79:
        return 'strong', 'ON TARGET'
    return 'excellent', 'EXCELLENT'


def rate_aht(value):
    if value is None:
        return None, '--'
    if value <= 5:
        return 'strong', 'ON TARGET'
    return 'low', 'ABOVE TARGET'


def rate_conr(value):
    if value is None:
        return None, '--'
    if value < 50:
        return 'low', 'NEEDS IMPROVEMENT'
    if value < 70:
        return 'good', 'GOOD'
    return 'excellent', 'EXCELLENT'


def compute_company_kpis(empresa, tipo=None):
    """
    Calcula, en vivo, los valores de DATA ANALYTICS (y CONR si aplica)
    a partir de los TransactionReport registrados para `empresa`.
    CSAT y NPS se derivan de las respuestas de la Encuesta de Satisfacción
    (csat_response 1-5, nps_response 0-10), no de un porcentaje ingresado
    directamente por el agente.
    Si se pasa `tipo`, filtra solo los reportes de ese tipo de transacción.
    """
    query = TransactionReport.query.filter_by(empresa=empresa)
    if tipo:
        query = query.filter_by(tipo=tipo)
    reportes = query.all()

    total = len(reportes)

    # --- CSAT: % de encuestados "satisfechos" (respuesta 4 o 5 sobre 5) ---
    csat_respuestas = [r.csat_response for r in reportes if r.csat_response is not None]
    if csat_respuestas:
        satisfechos = len([v for v in csat_respuestas if v >= 4])
        csat_val = round(satisfechos / len(csat_respuestas) * 100, 1)
    else:
        csat_val = None

    # --- NPS: % Promotores (9-10) - % Detractores (0-6), escala -100 a 100 ---
    nps_respuestas = [r.nps_response for r in reportes if r.nps_response is not None]
    if nps_respuestas:
        promotores = len([v for v in nps_respuestas if v >= 9])
        detractores = len([v for v in nps_respuestas if v <= 6])
        n = len(nps_respuestas)
        nps_val = round((promotores / n - detractores / n) * 100, 1)
    else:
        nps_val = None

    aht_val = _avg([r.handle_time for r in reportes])

    resueltos_primer_contacto = [
        r for r in reportes
        if r.resolution_status and 'resolved' in r.resolution_status.lower()
        and (r.call_status or 'Finalizada') != 'Transferida'
    ]
    fcr_val = round(len(resueltos_primer_contacto) / total * 100, 1) if total else None

    cvol_val = total

    ofertas = [r for r in reportes if r.offer_success in ('Si', 'No')]
    exitosas = [r for r in ofertas if r.offer_success == 'Si']
    conr_val = round(len(exitosas) / len(ofertas) * 100, 1) if ofertas else None

    csat_class, csat_label = rate_csat(csat_val)
    nps_class, nps_label = rate_nps(nps_val)
    fcr_class, fcr_label = rate_fcr(fcr_val)
    aht_class, aht_label = rate_aht(aht_val)
    conr_class, conr_label = rate_conr(conr_val)

    data = {
        'CSAT': {'value': csat_val, 'display': f'{csat_val}%' if csat_val is not None else '--', 'css': csat_class, 'rating': csat_label},
        'NPS':  {'value': nps_val,  'display': f'{nps_val}' if nps_val is not None else '--',     'css': nps_class,  'rating': nps_label},
        'FCR':  {'value': fcr_val,  'display': f'{fcr_val}%' if fcr_val is not None else '--',     'css': fcr_class,  'rating': fcr_label},
        'AHT':  {'value': aht_val,  'display': f'{aht_val} min' if aht_val is not None else '--',  'css': aht_class,  'rating': aht_label},
        'CVOL': {'value': cvol_val, 'display': str(cvol_val), 'css': None, 'rating': ''},
    }
    if empresa in EMPRESAS_CON_CONR:
        data['CONR'] = {'value': conr_val, 'display': f'{conr_val}%' if conr_val is not None else '--', 'css': conr_class, 'rating': conr_label}

    return {
        'empresa': empresa,
        'total_reportes': total,
        'kpis': kpis_for_empresa(empresa),
        'data': data,
    }
