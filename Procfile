web: gunicorn omr.wsgi --workers=1 --threads=5 --log-file -
release: python manage.py migrate --noinput
