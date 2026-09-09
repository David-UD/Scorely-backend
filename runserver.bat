call .\.venv\Scripts\activate
rem python manage.py makemigrations --settings=config.settings.development
rem python manage.py migrate --settings=config.settings.development
python manage.py runserver 0.0.0.0:8001 --settings=config.settings.development