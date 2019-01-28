FROM python:3.6-alpine

RUN adduser -D admin

WORKDIR /home/admin

RUN apk update && apk upgrade
RUN apk add --no-cache curl python pkgconfig python-dev openssl-dev libffi-dev musl-dev make gcc

RUN apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
RUN apk --update --upgrade add musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R admin:admin ./
USER admin

EXPOSE 2000
ENTRYPOINT ["./boot.sh"]
