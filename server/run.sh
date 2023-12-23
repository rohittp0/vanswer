# Run migrations
python3 manage.py migrate

# Run server using manage.py in debug mode or using gunicorn in production
if [ "$DEBUG" = "True" ]; then
    python3 manage.py runserver
else
    gunicorn server.wsgi:application --bind 0.0.0.0:8000
fi
