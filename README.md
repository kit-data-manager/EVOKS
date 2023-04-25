Install instructions (tested for linux)

**Prerequisites:**
Installation of git, docker and docker compose (docker-compose (with dash) will not be supported anymore)

**Information for windows**
We recommend to use WSL (windows subsystem for Linux) for running the software on windows (otherwise Fuseki will be VERY slow and more or less unusable, vocabulary import will take ~20 minutes..)

**installation:**

1. clone repo and go to folder
2. copy .example.env and rename to .env
3. open .env and change ports if desired
4. `docker compose up`
5. Open localhost:${EVOKS_PORT} which was set in .env file (default: 8000)
6. open evoks/evoks/settings.py
7. skosmos URLs: 
`SKOSMOS_DEV_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/"`
`SKOSMOS_LIVE_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/`"
e.g. 
`SKOSMOS_DEV_URI = "http://evoks.mydomain.edu:8001/"`
`SKOSMOS_LIVE_URI = "http://evoks.mydomain.edu:8002/"`
8. within settings.py adjust the allowed hosts to your needs (usually it should match the serverURL), e.g.
ALLOWED_HOSTS: list[str] = ['.mydomain.edu','localhost']
9. Very likely, a bug will occur since there are problems with fuseki folder access rights (creating vocabs will fail). Run `sudo chmod 777 -R fuseki-dev/ fuseki-live/` then. 
10. docker compose down (or end process) and restart (docker compose up)


**create admin**
To create an admin the following steps must be performed:

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

**License**

EVOKS is licensed under the Apache License, Version 2.0.