FROM python:3.9.2-slim-buster

WORKDIR /code

RUN apt-get update \
    && apt-get install -y build-essential curl git \
    && curl -sL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs --no-install-recommends \
    && apt-get install -y gettext-base \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

COPY requirements*.txt ./
COPY skosmos-dev/config-template.ttl ./skosmos-dev/config.ttl
COPY skosmos-live/config-template.ttl ./skosmos-live/config.ttl

RUN pip install -r requirements.txt

ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" 

COPY . .
RUN cd evoks/theme/static_src && npm install
RUN cd /code
RUN SECRET_KEY=nothing python ./evoks/manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python ./evoks/manage.py tailwind build --no-input;
RUN SECRET_KEY=nothing python ./evoks/manage.py collectstatic --no-input;

CMD ["python", "manage.py", "runserver"]
