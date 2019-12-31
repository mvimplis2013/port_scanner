# DockerHub Credentials
DOCKER_HUB_USER=vibm69
DOCKER_HUB_PASS=firewind

LOCAL_IMAGE_TAG=vlab-gui-image

TARGET_NAME=vlab-gui
TARGET_VERSION=23.0

# In case need to save ... local image to a new one
# docker ps ... Search for vlab-docker 
# docker commit <vlab-docker-id> vlab-docker-commit-a  

REMOTE="$DOCKER_HUB_USER/$TARGET_NAME:$TARGET_VERSION"

docker login -u "$DOCKER_HUB_USER" -p "$DOCKER_HUB_PASS" 

docker tag "$LOCAL_IMAGE_TAG" "$REMOTE"

docker push "$REMOTE"
