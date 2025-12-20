# UMIS-Pay

UMIS-Pay is a **Django-based payment and serial generation system** built for the University Management Information System (UMIS). It includes modules for serial code generation, bank reporting, and secure management of sensitive information.  


---

## Features

- **Serial Generator** (`serialgenerator`)
  - Generate unique serial codes
  - Encrypt serials with a secure encryption key
- **Bank Reports** (`bankreports`)
  - Generate and view financial reports
  - Store reports securely
- **Secure Settings**
  - Environment variables managed via `.env`
  - Sensitive information like `SECRET_KEY` and database credentials kept local

---

## Getting Started

### Prerequisites

- Python 3.11+
- Django 5.2+
- Virtual environment (recommended)
- Git

---

### Installation

1. Clone the repository:

```bash
git clone https://github.com/sedegah/UMIS-Pay.git
cd UMIS-Pay
````

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root of the project (same level as `manage.py`) with your local settings:

```env
DEBUG=True
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
SERIAL_ENCRYPTION_KEY=your_fernet_key
```

> Make sure `.env` is **not pushed** to GitHub.

---

### Run the Project

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Access the development server at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Project Structure

```
UMIS-Pay/
├── umis_pay/               # Django settings & core files
├── serialgenerator/        # Serial code generator app
├── bankreports/            # Bank reporting app
├── static/                 # Project static files
├── assets/                 # Additional static assets
├── manage.py               # Django management script
├── .env                    # Environment variables (local only)
├── .gitignore              # Git ignore rules
```

---

## Notes

* **Do not push sensitive files** like `.env` or `settings.py`.
* Migrations are ignored for local development; generate them locally using `python manage.py makemigrations`.
* Designed for **development purposes**. For production, configure proper WSGI/ASGI servers and secure settings.

---

## License

This project is **MIT Licensed**. See `LICENSE` for more details.

```



