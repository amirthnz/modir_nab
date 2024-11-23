FROM python:3.9-alpine3.13
LABEL maintainer="thnzcorp.ir"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY . /app


ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps


ENV PATH="/py/bin:$PATH"

RUN adduser --disabled-password --no-create-home django-user

# Assign ownership of the entire /app directory to django-user
RUN chown -R django-user:django-user /app

USER django-user

WORKDIR /app
EXPOSE 8000

# run entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
