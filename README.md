
docker-compose up

localhost:5050 -> "postgres" als admin passwort

server erstellen, name=evoks, host=postgres

database erstellen, name=dev

docker ps (id von pse-boilerplate-web kopieren)

`docker exec -t -i <id> bash`

cd evoks

python manage.py migrate

docker-compose down

docker-compose up
