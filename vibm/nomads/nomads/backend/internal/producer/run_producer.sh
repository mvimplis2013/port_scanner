docker rm producer-app

docker rmi producer 

cd ~/projects/port_scanner

git pull
cd vibm/nomads/nomads/backend/internal/producer

docker build -t producer .

docker run -it --name producer-app --network=host producer /bin/asash