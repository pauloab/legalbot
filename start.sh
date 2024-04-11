<strong>#!/bin/bash</strong>
source /venv/bin/activate
cd /app

echo "----- Collect static files ------ " 
python manage.py collectstatic --noinput

echo "-----------Apply migration--------- "
python manage.py makemigrations 
python manage.py migrate

echo "-----------Run gunicorn--------- "
gunicorn -b :5000 config.wsgi:application


# specify the number of workers with a positive integer. Generally, 4*(num cores) defaults to  1
gunicorn -b :5000 --workers INT config.wsgi:application

# Outputs the access log to a file named logfile. Use - to output to stdout
gunicorn -b :5000 --access-logfile logfile config.wsgi:application

# specify log level default is info. Options for LEVEL: debug, info, warning, error, critical
gunicorn -b :5000 --log-level LEVEL config.wsgi:application

