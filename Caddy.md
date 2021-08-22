# Caddy
Für HTTPS benutzen wir hier Caddy als Reverse Proxy. Caddy ist sehr einfach und braucht fast keine Konfiguration, auch das SSL Zertifikat wird automatisch (und kostenlos) erstellt.

In der aktuellen Konfiguration erstellt Caddy ein selbst signiertes Zertifikat für localhost, was natürlich in Browsern Fehler schmeißt. HTTPS ist momentan nur für production gedacht, daher wird der dev build mit Caddy nicht perfekt funktionieren (wegen dem Tailwind + Browsersync Server welche nicht über HTTPS läuft, das könnte man aber auch einfach erweitern)

Dokumentation gibt es hier: https://caddyserver.com/docs/quick-starts

Da Caddy auch als Loadbalancer arbeiten kann, haben wir es nicht zu docker-compose hinzugefügt. Damit wird es dann später einfacher wenn man Caddy und Evoks auf verschiedenen Servern laufen hat.

## Installation

Mit `caddy_install.sh` werden alle packages installiert die für Caddy notwendig sind. Caddy wird dann in dem gleichen Ordner wie Caddyfile mit `caddy start` gestartet. Das muss nur einmalig gemacht werden.

## Richtige Domain

Wenn eine richtige Domain für Evoks genutzt werden soll, muss nur die Caddy Konfiguration angepasst werden.
```
localhost:8010 {
    reverse_proxy localhost:8000
}
```

wird zu

```
example.com {
    reverse_proxy localhost:8000
}

skosmos-dev.example.com {
    reverse_proxy localhost:9090
}

skosmos-live.example.com {
    reverse_proxy localhost:9080
}

```

Außerdem müssen die Skosmos Domains in settings.py angepasst werden. Und nicht vergessen dass es A records für die Skosmos Domains gibt.
Allowed Hosts muss auch in Settings angepasst werden.
In production sollte es dann auch noch eine Firewall für die ganzen anderen Ports geben.