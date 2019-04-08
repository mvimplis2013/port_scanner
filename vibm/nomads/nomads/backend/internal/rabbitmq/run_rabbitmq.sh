docker stop rabbit-server
docker rm rabbit-server

#docker rmi rabbitmq
#docker build -t rabbitmq .

cd ~/projects/port_scanner
git pull

cd vibm/nomads/nomads/backend/internal/rabbitmq

docker run -d --hostname my-rabbit --name rabbit-server --network app-tier rabbitmq