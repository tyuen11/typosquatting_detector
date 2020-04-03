docker rm dtd-typogenerator
docker build -t dtd-typogenerator .
docker create --network mysql-network --name dtd-typogenerator dtd-typogenerator
