docker stop internal-agent-container
docker rm internal-agent-container

docker rmi internal-agent

cd ..
cd ..

git pull

cd vibm/nomads

docker build -t internal-agent .
docker run --name internal-agent-container -it --privileged internal-agent