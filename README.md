**Caution**
This software is only for internal development purposes. It is *not ready* for production and shall not be available for public. 

*Achtung*
Der Masterbranch enthält nicht die neusten Entwicklungen. Diese sind unter dem *testing* (mehr Funktionen, weniger usability) bzw. *sfb980* (weniger Funktionen, höhere usability) branch zu finden. 

Das folgende Vorgehen zum Aufsetzen der Applikation ist unter Linux getestet:

**Vorbedingung:**
Installation von git, docker und docker-compose

**Kommentar zu Windows**
Wir empfehlen wsl zur Ausführung zu benutzen (windows subsystem für Linux) (Sonst wird Fuseki SEHR langsam und quasi nicht nutzbar, der vokabular import dauert ~20 minuten..)

**Vorgehen:**

1. clone repo and go to folder
2. `docker-compose build --no-cache` (using cache sometimes leads to errors)
3. `docker-compose up`
4. Open localhost:${EVOKS_PORT} which was set in .env file (default: 8000)
5. open evoks/evoks/settings.py
6. skosmos URLs: 
`SKOSMOS_DEV_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/"`
`SKOSMOS_LIVE_URI = "http://<yourserverURL>:<chosen_port_in_evn_file>/`"
e.g. 
`SKOSMOS_DEV_URI = "http://evoks.mydomain.edu:8001/"`
`SKOSMOS_LIVE_URI = "http://evoks.mydomain.edu:8002/"`
7. within settings.py adjust the allowed hosts to your needs (usually it should match the serverURL), e.g.
ALLOWED_HOSTS: list[str] = ['.mydomain.edu']
8. Very likely, a bug will occur since there are problems with fuseki folder access rights (creating vocabs will fail). Run `sudo chmod 777 -R fuseki-dev/ fuseki-live/` then. 



**Admin erstellen**
Um einen Admin zu erstellen müssen folgende Schritte durchgeführt werden:

1. `docker ps`, look for <container_prefix>_web_1 container
2. `docker exec -it <container_prefix>_web_1 bash`
3. Within the container: `python evoks/manage.py createsuperuser`
4. Follow instructions to create a superuser
5. Log into EVOKS using the email as username and the chosen password

**Tests ausführen**
for running the unittests:

1. `docker ps`, look for <container_prefix>_web_1 container
2. `docker exec -it <container_prefix>_web_1 bash`
3. Within the container: `cd evoks`
4. run `coverage run --source='.' --omit='*/migrations/*.py','guardian/*','theme/*','evoks/__init__.py','evoks/asgi.py','evoks/wsgi.py','manage.py','tests/*' manage.py test tests/model/ tests/migration/ tests/skosmos/ tests/fuseki/ tests/views/ tests/evoks && coverage html` aus.
4. Open index.html from folder htmlcov with a browser.

**Bugs die eventuell auftreten**

1. Wenn Fuseki nicht starten will weil es keine Zugriffsrechte hat: `sudo chmod 777 -R fuseki-dev/ fuseki-live/`
2. Leere Ordner werden von Git nicht getrackt. Eventuell muss in den Ordnern fuseki-dev und fuseki-live ein leerer Ordner namens `backup` manuell erstellt werden.
3. Wenn ganz viel output schnell erscheint: `docker-compose down` und `docker-compose up`
4. Wenn tailwind docker container nicht starten will, tailwind.sh text rauskopieren und in eine neue datei mit gleichen namen einfügen und neustarten
5. Wenn Vokabular import ganz lange dauert, Linux oder WSL benutzen.
6. Wenn Seiten langsam laden, Linux oder WSL benutzen.
7. Docker neustarten
8. Wenn Änderungen am Code nicht erkannt werden, `docker-compose build --no-cache` und dann `docker-compose up` (und evlt alle container, images und volumes löschen aber Achtung, Datenverlust!)

**Mail Server konfigurieren**

1. Erstelle .env Datei unter evoks/evoks/
2. Schreibe `EMAIL_HOST_USER=deineemail`, `EMAIL_HOST_PASSWORD=deinpassword` in diese Datei rein.
3. Dann in Settings.py unter evoks/evoks/ muss die SMTP konfiguriert werden. Also Zeile 85 - 88 in Setting.py `EMAIL_HOST = 'smtp.gmail.com', EMAIL_PORT = 587, EMAIL_USE_TLS = TRUE(Beispiel für Gmail)`. Das kann man finden wenn man in einer Suchmaschiene "SMTP confiriguation gmail" schreibt. Die meisten Emails akzeptieren als default keine Less Secure Apps deshalb muss in den Einstellungen der verwendete Email Less Secure Apps akzeptiert werden.

**HTTPs + Domains**

1. Baue mit Docker ganz normal
2. Siehe Caddy.md für Caddy setup
3. Führe `docker-compose -f docker-compose.prod.yml up --detach` aus.
