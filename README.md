# CRM Celery Weekly Report Setup

This project configures **Celery** with **Celery Beat** to automatically
generate a weekly CRM report using GraphQL.

The report summarizes: - Total number of customers - Total number of
orders - Total revenue

The report is logged to:

/tmp/crm_report_log.txt

Format:

YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue

------------------------------------------------------------------------

## Install Requirements

Make sure Redis is installed and running.

### Install Redis (Ubuntu)

``` bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

Verify Redis is running:

``` bash
redis-cli ping
```

Expected output:

    PONG

------------------------------------------------------------------------

### Install Python Dependencies

From the project root directory:

``` bash
pip install -r requirements.txt
```

Make sure the following packages are included in `requirements.txt`:

    celery
    django-celery-beat
    redis

------------------------------------------------------------------------

## Apply Database Migrations

Run:

``` bash
python manage.py migrate
```

------------------------------------------------------------------------

## Start Celery Worker

``` bash
celery -A crm worker -l info
```

------------------------------------------------------------------------

## Start Celery Beat Scheduler

In a new terminal window:

``` bash
celery -A crm beat -l info
```

Celery Beat will trigger the task every Monday at 6:00 AM.

------------------------------------------------------------------------

## Verify the Report Log

``` bash
cat /tmp/crm_report_log.txt
```

Example output:

    2026-02-15 06:00:00 - Report: 120 customers, 350 orders, 54000 revenue

------------------------------------------------------------------------

## Optional: Manually Trigger the Task

``` bash
python manage.py shell
```

``` python
from crm.tasks import generate_crm_report
generate_crm_report.delay()
```

Then check:

``` bash
cat /tmp/crm_report_log.txt
```

------------------------------------------------------------------------

## How It Works

-   Celery connects to Redis as the message broker.
-   Celery Beat schedules the weekly task.
-   The task executes a GraphQL query internally.
-   Results are written to `/tmp/crm_report_log.txt`.

------------------------------------------------------------------------

## Summary

You have successfully configured:

-   Celery
-   Redis broker
-   Celery Beat scheduler
-   Weekly CRM report generation
-   Automated logging