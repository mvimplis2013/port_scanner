docker stop consumer-app
docker rm consumer-app

docker rmi consumer

cd ~/projects/port-scanner
git pull

cd vibm/nomads/nomads/backend/internal/consumer

docker build -t consumer .
docker run -it --name consumer-app --network app-tier consumer /bin/ash