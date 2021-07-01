from siwi import app

application = app = app.app

# gunicorn --bind :5000 wsgi --workers 1 --threads 1 --timeout 60
