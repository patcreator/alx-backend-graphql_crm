# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'django_crontab',  
    'django_celery_beat',  
    'crm', 
]

# Add cron jobs configuration
CRONJOBS = [
     ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),  # Run every 12 hou
]
CRONTAB_COMMAND_SUFFIX = '2>&1'
# Optional: Set timezone for cron jobs
CRONTAB_COMMAND_PREFIX = 'LANG=en_US.UTF-8'