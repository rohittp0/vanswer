#!/bin/sh

# Run server using manage.py in debug mode or using gunicorn in production
if [ "$DEBUG" = "true" ]; then
  python3 manage.py runserver 0.0.0.0:8000
else
  python3 manage.py collectstatic --noinput

  # Run migrations
  python3 manage.py migrate

  # Create superuser
  python3 manage.py createsuperuser --noinput

  gunicorn vanswer.wsgi:application --bind 0.0.0.0:8000
fi
