FROM python:3.8
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install gettext python3-cffi libcairo2 libpango-1.0-0 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y

RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages
CMD uwsgi --module=astroedu.wsgi --http=0.0.0.0:80
