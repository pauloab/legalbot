
cd app
start cmd TITLE Worker /c "..\..\env\Scripts\celery.exe -A config.celery worker -l info --pool=solo & pause"
TIMEOUT 2
start cmd TITLE app /c "..\..\env\Scripts\python.exe manage.py runserver & pause"