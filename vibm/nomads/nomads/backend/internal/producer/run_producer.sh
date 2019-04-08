docker rm producer-app

docker rmi producer 

cd ..
cd ..
cd ..
cd ..
cd ..

git pull
cd vibm/nomads/nomads/backend/internal/producer

docker build -t producer .

docker run -d --name producer-app producer