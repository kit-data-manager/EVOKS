# EVOKS repository
![tests](https://github.com/kit-data-manager/EVOKS/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/kit-data-manager/EVOKS/graph/badge.svg?token=qXx2sFQPxW)](https://codecov.io/gh/kit-data-manager/EVOKS)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

EVOKS (Editor for Vocabularies to Know Semantics) is a software for creating and publishing SKOS vocabularies and thesauri. 
It allows you to:
- create a SKOS vocabulary from scratch
- import SKOS vocabularies in RDF/XML or Turtle format
- edit SKOS vocabularies without using its textual representation
- work collaborativley
- publish the vocabulary with a single click in the vocabulary browser [SKOSMOS](https://www.skosmos.org)

# Note
**Caution**
This software is only for internal vocabulary development purposes. It is *not ready* for production and shall not be available for public access when installed. 

# Installation


The main way to install EVOKS and its depending services is to build and run the docker images locally using docker compose. 
## Prerequisites
* Unix-based system (e.g. Linux, MacOS, Windows using WSL (untested))
* Installation of 
    * [git](https://git-scm.com/) 
    * [Docker](https://www.docker.com/) 

## Installation procedure:

1. Clone this repository: 

    ```
    user@localhost:/home/user/$ git clone https://github.com/kit-data-manager/EVOKS.git
    Clone to 'EVOKS'
    [...]
    user@localhost:/home/user/$ cd EVOKS
    user@localhost:/home/user/EVOKS$
    ```
2. (until further notice) checkout development branch
    ```
    git checkout development
    ```
2. Copy .example.env and rename to .env
3. Open .env and change the variables if desired, see
[Overview of variables](##Variables).

    **Caution** Change of Fuseki and Postgres credentials is strongly recommended, especially if not installed and used only on a local computer without access from other people

4. Run `docker compose build`
5. Run `docker compose up`
7. Open the file within the repo: `evoks/evoks/settings.py` and update the SKOSMOS URIs:
    ```
    SKOSMOS_DEV_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/"
    SKOSMOS_LIVE_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/"
    ```
    e.g. 
    ```
    SKOSMOS_DEV_URI = "http://evoks.mydomain.edu:8001/"
    SKOSMOS_LIVE_URI = "http://evoks.mydomain.edu:8002/"
    ```
    or
    ```
    SKOSMOS_DEV_URI = "localhost:8001/"
    SKOSMOS_LIVE_URI = "localhost:8002/"
    ```
9. within `settings.py` adjust the allowed hosts to your needs (usually it should match the serverURL), e.g.
    ```
    ALLOWED_HOSTS: list[str] = ['.mydomain.edu','localhost']
    ```
6. Open `<yourserverURL>:${EVOKS_PORT}` which was set in `.env` file (default: `8000`), e.g. localhost:8000 in your browser
10. Very likely, a bug will occur since there are problems with fuseki folder access rights (creating vocabs will fail). Run `sudo chmod 777 -R fuseki-dev/ fuseki-live/` then (see issue #<tobefilled>)
11. To stop the services, run `docker compose down` and to restart `docker compose up`

## Variables

| VAR NAME          | Default value      | Description                                                                                                                | Change mandatory |   |
|-------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------|------------------|---|
| INSTANCE_NAME     | defaultinstance    | Prefix of docker container names                                                                                           | no               |   |
| EVOKS_PORT        | 8000               | Port of EVOKS                                                                                                              | no               |   |
| SKOSMOS_DEV_PORT  | 8001               | Port of Skosmos for vocabulary development                                                                                 | no               |   |
| SKOSMOS_LIVE_PORT | 8002               | Port of Skosmos for published vocabularies                                                                                 | no               |   |
| EVOKS_MAIL        | example@example.de | Mailaddress for automatically sending notifications to the instance admin (typically the person who installed the service) | no               |   |
| FUSEKI_USER       | admin              | Default fuseki username, change especially if not used locally                                                             | yes              |   |
| FUSEKI_PASSWORD   | fuseki_password    | Default fuseki password, change especially if not used locally                                                             | yes              |   |
| POSTGRES_USER     | postgres           | Default postgres username, change especially if not used locally                                                           | yes              |   |
| POSTGRES_PASSWORD | changeme           | Default postgres password, change especially if not used locally                                                           | yes              |   |
| POSTGRES_PORT     | 8005               | Port of Postgres DB, only needed for code developers                                                                       | no               |   |
| FUSEKI_DEV_PORT   | 8003               | Port of Fuseki Triple Store, only needed for code developers                                                               | no               |   |
| FUSEKI_LIVE_PORT  | 8004               | Port of Fuseki Triple Store (of published vocabularies), only needed for code developers                                   | no               |   |

## Create an administrator
You need to create an administrator account for EVOKS by performing the following steps:

1. Run `docker ps`, look for `<container_prefix>_web` (or `...web_1`) container
2. Run `docker exec -it <container_prefix>_web bash` (or `...web1` accordingly)
3. Now you are within the container. Run: `python evoks/manage.py createsuperuser`
4. Follow instructions to create a superuser. You can choose whatever username, password and (arbitary) mailaddress you like
5. Log into EVOKS using the email as username and the chosen password

# Further settings (not needed for initial setup)
## Configure Mail Server
1. Edit .env file
2. Fill out 
    ```
    EMAIL_HOST_USER=your-email
    EMAIL_HOST_PASSWORD=your-password
    ``` 
    in this file. **Caution**: Be aware that the password is stored as plain text!
3. Open `evoks/evoks/settings.py` and configure the SMTP server. E.g. for gmail
    ```
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = TRUE
    ```

Most of the email providers (e.g. Gmail) do not accept Less Secure Apps by default, so you have to accept Less Secure Apps in the settings of the email you are using.

## HTTPs + Domains

1. Stop containers
2. See Caddy.md for Caddy setup
3. Run containers again

# For Developers

## Execution of Tests (only for developers needed)
Run the unittests:

1. `docker ps`, look for <container_prefix>_web_1 container
2. `docker exec -it <container_prefix>_web_1 bash`
3. Within the container: `cd evoks`
4. run `coverage run --source='.' --omit='*/migrations/*.py','guardian/*','theme/*','evoks/__init__.py','evoks/asgi.py','evoks/wsgi.py','manage.py','tests/*' manage.py test tests/model/ tests/migration/ tests/skosmos/ tests/fuseki/ tests/views/ tests/evoks && coverage html` aus.
5. Open index.html from folder htmlcov with a browser.

**License**

EVOKS is licensed under the Apache License, Version 2.0. 
License owner: Karlsruhe Institute of Technology (KIT)
