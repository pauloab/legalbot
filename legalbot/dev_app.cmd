
cd app
start cmd TITLE Worker /c "..\..\env\Scripts\python.exe ..\..\env\Scripts\celery.exe -A config.celery worker -l info  -P gevent & pause"
TIMEOUT 2
start cmd TITLE app /c "..\..\env\Scripts\python.exe manage.py runserver & pause"