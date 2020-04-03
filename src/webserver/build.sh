docker rm dtd-webserver
docker build -t dtd-webserver .
docker create --network mysql-network -p 80:80 --name dtd-webserver dtd-webserver
