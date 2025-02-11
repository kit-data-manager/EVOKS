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
Use of this software in a production environment or with external access is at your own risk. No warranties, guarantees, or liabilities are provided, and the software is offered as-is.

# Know issues
- See github issues of this repo for all known issues.

# Installation

The main way to install EVOKS and its depending services is to build and run the docker images locally using docker compose. 
## Prerequisites
* Unix-based system (e.g. Linux, MacOS, Windows using WSL (untested))
* Installation of most recent versions of
    * [git](https://git-scm.com/) 
    * [Docker](https://www.docker.com/) (at least docker compose version v2.27.1 needed)

## Installation procedure:

1. Clone this repository: 

    ```
    user@localhost:/home/user/$ git clone https://github.com/kit-data-manager/EVOKS.git
    Clone to 'EVOKS'
    [...]
    user@localhost:/home/user/$ cd EVOKS
    user@localhost:/home/user/EVOKS$
    ```
2. Copy .example.env and rename to .env
3. Open .env and change the variables if desired, see
[Overview of variables](##Variables).

    **Caution** Change of Fuseki and Postgres credentials is strongly recommended, especially if it will be accessible from outside

4. Open evoks/evoks/settings.py and change the SECRET_KEY. Use of a key generator like https://djecrety.ir/ is strongly recommended.
4. Run `docker compose build`
5. Run `docker compose up`
6. Open PUBLICURL:PROXYPORT/EVOKS_URL (as set in .env), with default values http://localhost:9000/ in your browser (opening in Firefox not working currently)
7. To open the vocabulary browser Skosmos, open PUBLICURL:PROXYPORT/skosmos-dev or PUBLICURL:PROXYPORT/skosmos-live
11. To stop the services, run `docker compose down` and to restart `docker compose up`

## Variables

| VAR NAME          | Default value      | Description                                                                                                                | Change recommended |   |
|-------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------|---|
| INSTANCE_NAME     | defaultinstance    | Prefix of docker container names                                                                                           | no                 |   |
| PROXY_PORT        | 9000               | Port where the proxy is located                                                                                            | no                 |   |
| PUBLICURL         | localhost          | (public) base URL under which the services will be reached ("http://" resp. "https://" is added automatically)             | no                 |   |
| EVOKS_MAIL        | example@example.de | Mailaddress for automatically sending notifications to the instance admin (typically the person who installed the service) | no                 |   |
| FUSEKI_PASSWORD   | insecure_changeme  | Default fuseki password, change especially if not used locally                                                             | yes                |   |
| POSTGRES_USER     | postgres           | Default postgres username, change especially if not used locally                                                           | yes                |   |
| POSTGRES_PASSWORD | insecure_changeme  | Default postgres password, change especially if not used locally                                                           | yes                |   |
| EVOKS_URL         | /                  | path directory under which the web app (evoks) will be reached                                                             | no                 |   |
| POSTGRES_PORT     | 8005               | (Developers only) Port of Postgres DB, service not forwarded to host if unset                                              | no                 |   |
| FUSEKI_DEV_PORT   | 8003               | (Developers only) Port of Fuseki Triple Store, service not forwarded directly to host if unset                             | no                 |   |
| FUSEKI_LIVE_PORT  | 8004               | (Developers only) Port of Fuseki Triple Store (of published vocabularies), service not forwarded directly to host if unset | no                 |   |
| EVOKS_PORT        | 8000               | (Developers only) Port of EVOKS, service not forwarded directly to host if unset                                           | no                 |   |
| SKOSMOS_DEV_PORT  | 8001               | (Developers only) Port of Skosmos for vocabulary development, service not forwarded directly to host if unset              | no                 |   |
| SKOSMOS_LIVE_PORT | 8002               | (Developers only) Port of Skosmos for published vocabularies, , service not forwarded directly to host if unset            | no                 |   |


## Create an administrator
You need to create an administrator account for EVOKS by performing the following steps:

1. Run `docker ps`, look for `<container_prefix>_web` (or `...web_1`) container
2. Run `docker exec -it <container_prefix>_web bash` (or `...web1` accordingly)
3. Now you are within the container. Run: `python evoks/manage.py createsuperuser`
4. Follow instructions to create a superuser. You can choose whatever username, password and (arbitary) mailaddress you like
5. Log into EVOKS using the email as username and the chosen password

## Note on running the service in production state  (e.g. available from the www)
Apply the [Django deployment checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/). 
Most of it is already implemented, you should at least do the following:
- Setup https using the provided reverse proxy nginx
- Log into the web container and run `python evoks/manage.py check --deploy` and check & solve all issues
- Make sure to set / change all variables in .env where it is recommended

# Further settings (not needed for initial setup)
## Configure Mail Server
1. Open .env file
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


# For Developers

## Bypass proxy setup for direct access to services and enable Django debug mode:
- Open .env file
- Adjust all variables marked as "(Developers only)" in the [Overview of variables](##Variables). 
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up`


## Execution of Tests (only for developers needed)
Run the tests:
`docker compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from web`
Run tests within container (e.g. for test bug fixing):
Log into web container, execute `python manage.py test tests/model/ tests/migration/ tests/skosmos/ tests/fuseki/ tests/views/ tests/evoks`

**License**

EVOKS is licensed under the Apache License, Version 2.0. 
License owner: Karlsruhe Institute of Technology (KIT)

**Acknowledgement**
Development of this software product was funded by the German Research Foundation (DFG)—CRC 980 Episteme in Motion, Project-ID 191249397, and by the research program “Engineering Digital Futures” of the Helmholtz Association of German Research Centers.
