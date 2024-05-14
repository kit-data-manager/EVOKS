**Caution**
This software is only for internal development purposes. It is *not ready* for production and shall not be available for public. 

Install instructions (tested for linux)

**Requirements:**
Installation of 
* git
* docker (docker-compose (with dash) will not be supported anymore)

**Comment regarding Windows**
We recommend to use WSL (windows subsystem for Linux) for running the software on windows (otherwise Fuseki will be VERY slow virtuall unusuable)

**Installation procedure:**

1. clone repo and go to folder
2. copy .example.env and rename to .env
3. open .env and change ports if desired
4. `docker compose build`
5. `docker compose up`
6. Open localhost:${EVOKS_PORT} which was set in .env file (default: 8000)
7. open evoks/evoks/settings.py
8. skosmos URLs: 
`SKOSMOS_DEV_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/"`
`SKOSMOS_LIVE_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/`"
e.g. 
`SKOSMOS_DEV_URI = "http://evoks.mydomain.edu:8001/"`
`SKOSMOS_LIVE_URI = "http://evoks.mydomain.edu:8002/"`
9. within settings.py adjust the allowed hosts to your needs (usually it should match the serverURL), e.g.
ALLOWED_HOSTS: list[str] = ['.mydomain.edu','localhost']
10. Very likely, a bug will occur since there are problems with fuseki folder access rights (creating vocabs will fail). Run `sudo chmod 777 -R fuseki-dev/ fuseki-live/` then. 
11. docker compose down (or end process) and restart (docker compose up)


**Create an administrator**
To create an administrator account for evoks the following steps have to be performed:

1. `docker ps`, look for <container_prefix>_web_1 container
2. `docker exec -it <container_prefix>_web_1 bash`
3. Within the container: `python evoks/manage.py createsuperuser`
4. Follow instructions to create a superuser
5. Log into EVOKS using the email as username and the chosen password


**Configure Mail Server**
1. create .env file under evoks/evoks/
2. write `EMAIL_HOST_USER=youremail`, `EMAIL_HOST_PASSWORD=yourpassword` in this file.
3. then in Settings.py under evoks/evoks/ you have to configure the SMTP. E.g. `EMAIL_HOST = 'smtp.gmail.com', EMAIL_PORT = 587, EMAIL_USE_TLS = TRUE(example for Gmail)`.  Most of the emails do not accept Less Secure Apps by default, so you have to accept Less Secure Apps in the settings of the email you are using.

**HTTPs + Domains**

1. do while containers are not running
2. See Caddy.md for Caddy setup
3. run containers again

**Execution of Tests (only for developers needed)**
for running the unittests:

Run the unit/integration tests with `docker compose -f docker-compose.test.yml up --abort-on-container-exit`. 
This will run all tests, create a coverage report and stop all containers afterwards.

- You can keep the associated containers running by removing `--abort-on-container-exit`. This might be useful for checking database states after testing (mainly for troubleshooting test setup).
- Change [configuration for coverage](https://coverage.readthedocs.io/en/latest/config.html) report in `evoks/.coveragerc` if needed.
- Add or remove test targets in `docker-compose.test.yml` in the `command` section of the web / testrunner container.
- You can change the verbosity level of the test runner by changing or removing the `-v` parameter from the command.

**License**

EVOKS is licensed under the Apache License, Version 2.0.
