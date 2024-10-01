import os
from celery import Celery

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shipkz.settings')

app = Celery('your_project_name')

# Загрузите настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически найдите задачи в ваших приложениях
app.autodiscover_tasks()