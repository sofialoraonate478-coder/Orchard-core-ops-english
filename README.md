# Orchard Core Ops — Sistema de Soporte con Estética Orchard

Proyecto de gestión de tickets con la estética visual de **Orchard Core Ops** (fondo oscuro, verde, plata, glassmorphism).

## Estructura

```
ollama_nuevo/
├── backend/
│   ├── app.py              # App principal Flask
│   ├── config.py           # Configuración (DB, secreto)
│   ├── models.py           # Modelos User, Ticket, Response
│   ├── requirements.txt
│   └── modules/
│       ├── auth/routes.py
│       ├── tickets/routes.py
│       ├── dashboard/routes.py
│       └── reports/routes.py
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── auth/register.html
│   ├── dashboard/dashboard.html
│   ├── tickets/list.html
│   ├── tickets/create.html
│   ├── tickets/view.html
│   └── reports/index.html
├── static/
│   ├── css/styles.css      # Estilos BPO completos
│   ├── js/script.js        # Navbar scroll + hamburger
│   └── img/logo.png        # Logo Orchard
└── instance/
    └── helpdesk.db         # Base de datos SQLite (vacía, se crea al iniciar)
```

## Iniciar el proyecto

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Acceder a: http://localhost:5000

## Credenciales por defecto

- **Usuario:** admin
- **Contraseña:** admin123
- **Rol:** admin

La base de datos se crea **vacía** y automáticamente al ejecutar el proyecto.
Se crea únicamente el usuario admin por defecto.

## Paleta de colores

| Variable       | Valor     | Uso                  |
|----------------|-----------|----------------------|
| `--black`      | `#0d0d0d` | Fondo principal      |
| `--green`      | `#14532d` | Verde oscuro base    |
| `--green-glow` | `#22c55e` | Verde brillante/CTA  |
| `--silver`     | `#c0c0c0` | Texto secundario     |
| `--white`      | `#ffffff` | Texto principal      |
