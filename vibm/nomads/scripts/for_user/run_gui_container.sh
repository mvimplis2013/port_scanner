# Pull latest image from Docker Hub 
# docker pull -t vlab-docker .

VERSION=10.0
GUI_IMAGE="vibm69/vlab-gui"
docker run -it -p 5000:5000 -e"MARIADB-SERVER=$1" --network app-tier --name vlab-gui $GUI_IMAGE:$VERSION"