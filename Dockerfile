FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY ./code/requirements.txt /code/
RUN pip install -r requirements.txt

# WORKDIR /var/www/html
# RUN apt-get update && \
# apt-get install -y libpng-dev && \
# docker-php-ext-install pdo pdo_mysql gd \
# RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli
# RUN pecl install redis docker-php-ext-enable redis
# EXPOSE 80
# CMD ["apache2-foreground"]

