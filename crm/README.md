# CRM GraphQL API Project

A Django-based CRM system with GraphQL API, Celery for async tasks, and
cron jobs for scheduled operations.

## Features

-   GraphQL API with graphene-django
-   Async task processing with Celery
-   Scheduled tasks with Celery Beat
-   Cron jobs for periodic maintenance
-   SQLite database (configurable for production)

## Prerequisites

-   Python 3.8+
-   Redis Server (for Celery)
-   pip (Python package manager)
-   virtualenv (recommended)

## Installation Steps

### Clone the Repository

``` bash
git clone <your-repository-url>
cd <project-directory>
```

### Create and Activate Virtual Environment

``` bash
python -m venv venv
```

**Windows:**

``` bash
venv\Scripts\activate
```

**macOS/Linux:**

``` bash
source venv/bin/activate
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist:

    Django>=4.2.0
    graphene-django>=3.0.0
    django-filter>=23.0
    django-crontab>=0.7.1
    celery>=5.3.0
    redis>=5.0.0
    django-celery-beat>=2.5.0
    python-dotenv>=1.0.0

## Environment Configuration

Create a `.env` file in the project root:

    SECRET_KEY=your-secret-key-here-change-in-production
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    REDIS_URL=redis://localhost:6379/0

## Database Setup

``` bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # optional
```

## Running the Services

### Start Celery Worker

``` bash
celery -A crm worker --loglevel=info
```

### Start Celery Beat

``` bash
celery -A crm beat --loglevel=info
```

Or combined (development only):

``` bash
celery -A crm worker --beat --loglevel=info
```

### Start Django Server

``` bash
python manage.py runserver
```

Access: - http://localhost:8000 - http://localhost:8000/graphql

## Example GraphQL Query

``` graphql
{
  __schema {
    types {
      name
    }
  }
}
```

## Useful Commands

Clear Celery tasks:

``` bash
celery -A crm purge
```

Flush database:

``` bash
python manage.py flush
```

Create DB backup:

``` bash
python manage.py dumpdata > db_backup.json
```

Load DB backup:

``` bash
python manage.py loaddata db_backup.json
```

## Production Notes

Set:

    DEBUG = False
    ALLOWED_HOSTS = ['your-domain.com']

Use PostgreSQL for production.

Enable security settings:

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

------------------------------------------------------------------------