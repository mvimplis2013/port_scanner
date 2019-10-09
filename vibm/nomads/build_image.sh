GUI_IMAGE="vlab-gui-image"

# ***********************
# Important Configuration
# ***********************
PORT_LOCAL=5000
PORT_CONTAINER=5000
# ***********************

GUI_CONTAINER="vlab_gui_container"
#DOCKER_RUN_FLAGS="--name $GUI_CONTAINER -it --privileged --network app-tier -d -p $PORT_LOCAL:$PORT_CONTAINER -t -eMARIADB-SERVER=172.24.0.2 $GUI_IMAGE"

# Appropriate dockerfile is ready for "docker" commands to use
# DOCKER ENGINE Commands Section

docker build -t "$GUI_IMAGE" . 

#docker run $DOCKER_RUN_FLAGS
