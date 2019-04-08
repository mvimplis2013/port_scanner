docker rm producer-app

docker rmi producer 

cd ~/projects/port_scanner

git pull
cd vibm/nomads/nomads/backend/internal/producer

docker build -t producer .

docker run -d --name producer-app --network app-tier producer