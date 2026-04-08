FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY ./code/requirements.txt /code/
RUN pip install -r requirements.txt

COPY ./code /code/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn simple_lms.wsgi:application --bind 0.0.0.0:8000"]