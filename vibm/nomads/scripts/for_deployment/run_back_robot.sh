docker rmi back-robot-app

yes | cp -f docker/Dockerfile ./

docker network create app-tier --driver bridge
docker network inspect app-tier

# *** MySQL Server ***
# 
if [ "$(docker ps -a | grep mariadb-server)"]; then 
    echo "Mariadb-Server Exists"
else
    echo "Mariadb-Server Not Exists"
    docker run -d --name mariadb-server -e ALLOW_EMPTY_PASSWORD=yes --network app-tier bitnami/mariadb:latest
fi 

# *** MySQL Client ***
# 
# docker run -it --rm --network app-tier bitnami/mariadb:latest mysql -h mariadb-server -u root

docker build -t back-robot-app .

docker run -it --rm --network app-tier --name back-robot-running-app back-robot-app # -h mariadb-server -u root

#docker run -it --rm --name back-robot-running-app --link mariadb-server:mariadb back-robot-app # -h mariadb-server -u root