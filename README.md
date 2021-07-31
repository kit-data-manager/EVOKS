Das folgende Vorgehen zum Aufsetzen der Applikation ist unter Linux getestet:

**Vorbedingung:**
Installation von git, docker und docker-compose

**Kommentar zu Windows**
Wir empfehlen wsl zur Ausführung zu benutzen (windows subsystem für Linux)

**Vorgehen:**
1. Clone dieses Repository.
2. Öffne ein neues Konsolenfenster und gehe in das geclonte Projekt auf die oberste Ordnerebene mit `cd implementierung`
Hier muss such die Datei `docker-compose.yml` befinden.
3. Docker muss eventuell erst gestartet werden, hierzu führe `sudo systemctl start docker.service` aus.
4. Führe `docker-compose up` aus. Docker wird dann die Python Umgebung einrichten und Bibliotheken herunterladen, dieser Schritt.
kann ein wenig Zeit in Anspruch nehmen. Der Prozess läuft dann im Hintergrund. Er kann über `strg+C` oder in einem neuen Konsolenfenster über das Kommando `docker-compose down` innerhalb des gleichen Verzeichnisses beendet werden. Für die nächsten Schritte muss der Prozess aber im Hintergrund laufen.
5. Öffne einen Browser.
6. Gehe auf die Seite `localhost:5050`.
7. Melde dich mit dem Passwort 'postgres' an.
8. Hier muss die Django Datenbank eingerichtet werden. Erstelle einen neuen Server durch Rechtsklick auf 'Servers'
in der linken Seitenleiste, wähle 'Server' aus. Im Pop Up Fenster fülle auf der Seite 'General' das Feld name=evoks und auf der Seite 'Connection' Host=postgres aus und wähle ein Passwort. Drücke speichern.
9. In der Seitenleiste erscheint nun ein neuer Server mit Namen evoks. Klappe die Unterpunkte unterhalb des Icons aus. Dort befindet sich ein Punkt 'Database'. Mache Rechtsklick auf 'Database' wähle 'Create' dann 'Database' aus. Setze im Pop Up Fenster name=dev. Drücke speichern.
10. Die Django Database ist aufgesetzt, sie muss jetzt in das Projekt migriert werden. Öffne hierzu ein neues Konsolenfenster und gehe in die oberste Ordnerebene des Projektes. 
11. Führe das Kommando `docker ps` aus. Es erscheint eine Liste aller Docker Container. In der ersten Spalte ist die id des Docker Containers gelistet. Kopiere die id des Kontainers mit namen: `implementierung_web `.
12. Führe als nächstes folgendes Kommando aus, ersetze docker_id durch die zuvor kopierte Id: `docker exec -t -i container_id bash`. Nun befindest du dich innerhalb des Docker Kontainers.
13. Wechsele in das Verzeichnis evoks mit `cd evoks`.
14. Führe die Migration aus durch: `python manage.py migrate`.
15. Verlasse den Container mit `exit`.
16. Schließe Docker mit `docker-compose down`.
17. Gehe in das erste Konsolenfenster und starte Docker neu mit `docker-compose up`.
18. Nun ist das Projekt fertig eingerichtet. Im Browser kann unter localhost:8000/vocabularies die Startseite der Applikation aufgerufen werden.

**Admin erstellen**
Um einen Admin zu erstellen müssen folgende Schritte durchgeführt werden:
1. `docker-compose up` muss im Hintergrund laufen.
2. Führe Schritt 10. und 11. der Anleitung oben aus. Führe innerhalb des Docker Containers `python manage.py createsuperuser` aus und befolge die Konsolenbefehle. 
3. Nun kann im Webbrowser `localhost:8000/admin` aufgerufen werden. Der Login funktioniert mit der im oberen Schritt festgelegten Email als username sowie Passwort.

**Tests ausführen**
Um Unittests auszuführen:
1. Führe Schritt 10. und 11. der Anleitung oben aus. 
2. Führe innerhalb des Docker Containers `python manage.py test evoks/tests` aus.
