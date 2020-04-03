docker rm dtd-urlverifier
docker build -t dtd-urlverifier .
docker create --network mysql-network --name dtd-urlverifier dtd-urlverifier
