FROM python:3.9.2-slim-buster

WORKDIR /code

RUN apt-get update \
    && apt-get install -y build-essential curl \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get install -y nodejs --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean


COPY requirements*.txt ./

RUN pip install -r requirements.txt

ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" 

COPY . .

RUN SECRET_KEY=nothing python ./evoks/manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python ./evoks/manage.py tailwind build --no-input;
RUN SECRET_KEY=nothing python ./evoks/manage.py collectstatic --no-input;

CMD ["python", "manage.py", "runserver"]
