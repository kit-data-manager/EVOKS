Das folgende Vorgehen zum Aufsetzen der Applikation ist unter Linux getestet:

**Vorbedingung:**
Installation von git, docker und docker-compose

**Kommentar zu Windows**
Wir empfehlen wsl zur Ausführung zu benutzen (windows subsystem für Linux) (Sonst wird Fuseki SEHR langsam und quasi nicht nutzbar, der vokabular import dauert ~20 minuten..)

**Vorgehen:**
1. Clone dieses Repository.
2. Öffne ein neues Konsolenfenster und gehe in das geclonte Projekt auf die oberste Ordnerebene mit `cd implementierung`
Hier muss such die Datei `docker-compose.yml` befinden.
3. Docker muss eventuell erst gestartet werden, hierzu führe `sudo systemctl start docker.service` aus.
4. Führe `docker-compose -f docker-compose.prod.yml build --no-cache` aus. Docker wird dann die Python Umgebung einrichten und Bibliotheken herunterladen, dieser Schritt kann ein wenig Zeit in Anspruch nehmen. Führe dann `docker-compose -f docker-compose.prod.yml up` aus. Der Prozess läuft dann im Hintergrund. Er kann über `strg+C` oder in einem neuen Konsolenfenster über das Kommando `docker-compose down` innerhalb des gleichen Verzeichnisses beendet werden. Für die nächsten Schritte muss der Prozess aber im Hintergrund laufen.
5. Öffne einen Browser.
6. Gehe auf die Seite `localhost:5050`.
7. Melde dich mit dem Passwort 'postgres' an.
8. Hier muss die Django Datenbank eingerichtet werden. Erstelle einen neuen Server durch Rechtsklick auf 'Servers'
in der linken Seitenleiste, wähle 'create', dann 'Server' aus. Im Pop Up Fenster fülle auf der Seite 'General' das Feld 'Name' aus mit dem Wert 'evoks' und auf der Seite 'Connection' das Feld 'Host' mit dem Wert 'postgres' aus und fülle als Passwort 'changeme' aus. Drücke speichern.
9. In der Seitenleiste erscheint nun ein neuer Server mit Namen evoks. Klappe die Unterpunkte unterhalb des Icons aus. Dort befindet sich ein Punkt 'Database'. Mache Rechtsklick auf 'Database' wähle 'Create' dann 'Database' aus. Setze im Pop Up Fenster für das Feld 'Database' den Wert 'dev'. Drücke speichern.
10. Die Django Database ist aufgesetzt, sie muss jetzt in das Projekt migriert werden. Öffne hierzu ein neues Konsolenfenster und gehe wieder in die oberste Ordnerebene des Projektes. (Der Ordner in der sich die Datei `docker-compose.yml` befindet)
11. Führe das Kommando `docker ps` aus. Es erscheint eine Liste aller Docker Container. In der ersten Spalte ist die id des Docker Containers gelistet. Kopiere die id des Kontainers mit namen: `implementierung_web`.
12. Führe als nächstes folgendes Kommando aus, ersetze im folgenden Kommando container_id durch die zuvor kopierte Id: `docker exec -t -i container_id bash`. Nun befindest du dich innerhalb des Docker Kontainers.
13. Wechsele in das Verzeichnis evoks mit `cd evoks`.
14. Führe die Migration aus: `python manage.py migrate`.
15. Verlasse den Container mit `exit`.
16. Schließe Docker mit `docker-compose down`.
17. Gehe in das erste Konsolenfenster und starte Docker neu mit `docker-compose up`.
18. Nun ist das Projekt fertig eingerichtet. Im Browser kann unter localhost:8000/vocabularies die Startseite der Applikation aufgerufen werden.

**Admin erstellen**
Um einen Admin zu erstellen müssen folgende Schritte durchgeführt werden:
1. `docker-compose up` muss im Hintergrund laufen.
2. Führe Schritt 10-13 der Anleitung oben aus, um wieder in die Konsole innerhalb des Docker Kontainers zu kommen. Führe innerhalb des Docker Containers `python manage.py createsuperuser` aus und befolge die Konsolenbefehle. 
3. Nun kann im Webbrowser `localhost:8000/admin` aufgerufen werden. Der Login funktioniert mit der im oberen Schritt festgelegten Email als username sowie Passwort.

**Tests ausführen**
Um Unittests auszuführen:
1. Führe Schritt 10-13 der Anleitung oben aus.
2. Führe innerhalb des Docker Containers `coverage run --source='.' --omit='*/migrations/*.py','guardian/*','theme/*','evoks/__init__.py','evoks/asgi.py','evoks/wsgi.py','manage.py','tests/*' manage.py test  tests/model/ tests/migration/ tests/skosmos/ tests/fuseki/ tests/views/  tests/evoks &&  coverage html` aus.
3. Öffne index.html aus htmlcov mit einem Browser.

**Bugs die eventuell auftreten**
1. Wenn Fuseki nicht starten will weil es keine Zugriffsrechte hat: `sudo chmod 777 -R fuseki-dev/ fuseki-live/`
2. Leere Ordner werden von Git nicht getrackt. Eventuell muss in den Ordnern fuseki-dev und fuseki-live ein leerer Ordner namens `backup` manuell erstellt werden.
3. Wenn ganz viel output schnell erscheint: `docker-compose down` und `docker-compose up`
4. Wenn tailwind docker container nicht starten will, tailwind.sh text rauskopieren und in eine neue datei mit gleichen namen einfügen und neustarten
5. Wenn Vokabular import ganz lange dauert, Linux oder WSL benutzen. 
6. Wenn Seiten langsam laden, Linux oder WSL benutzen.
7. Docker neustarten

**Mail Server konfigurieren**
1. Erstelle .env Datei unter evoks/evoks/ 
2. Schreibe `EMAIL_HOST_USER=deineemail`, `EMAIL_HOST_PASSWORD=deinpassword` in diese Datei rein. 
3. Dann in Settings.py unter evoks/evoks/ muss die SMTP konfiguriert werden. Also Zeile 85 - 88 in Setting.py `EMAIL_HOST = 'smtp.gmail.com', EMAIL_PORT = 587, EMAIL_USE_TLS = TRUE(Beispiel für Gmail)`. Das kann man finden wenn man in einer Suchmaschiene "SMTP confiriguation gmail" schreibt. Die meisten Emails akzeptieren als default keine Less Secure Apps deshalb muss in den Einstellungen der verwendete Email Less Secure Apps akzeptiert werden.

