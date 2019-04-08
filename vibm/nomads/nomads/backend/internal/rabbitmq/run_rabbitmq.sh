docker stop rabbit-server
docker rm rabbit-server

#docker rmi rabbitmq
#docker build -t rabbitmq .

docker run -d --hostmame my-rabbit --name rabbit-server --network app-tier rabbitmq