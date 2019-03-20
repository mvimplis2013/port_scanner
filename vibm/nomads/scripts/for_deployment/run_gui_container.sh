#source ./scripts/for_housekeeping/containers_remove_all_regardless_state.sh

SCRIPTS_LOCATION="./scripts/for_deployment/"

OUTPUT="output.txt"
FAILURE_STRING="Aborting"

GUI_IMAGE="vlab-gui-image"

CHECK_BUILT="Successfully built"
CHECK_TAGGED="Successfully tagged"

DOCKER_BUILD_ERROR="Docker Build for GUI Image Failure !"

# ***********************
# Important Configuration
# ***********************
PORT_LOCAL=5000
PORT_CONTAINER=5000
# ***********************

GUI_CONTAINER="vlab_gui_container"
DOCKER_RUN_FLAGS="--name $GUI_CONTAINER -it --privileged -d -p $PORT_LOCAL:$PORT_CONTAINER -t -eMARIADB-SERVER=172.24.0.2 $GUI_IMAGE"

# Bring forward the GUI-container dockerfile
source "$SCRIPTS_LOCATION"/prepare_context_of_build.sh arm x32 gui | tee "$OUTPUT"

# Check if file contains FAILURE string
if grep -q "$FAILURE_STRING" "$OUTPUT"; then
  echo "Dockerfile for Context Failure !" && exit 1
fi

# Appropriate dockerfile is ready for "docker" commands to use
# DOCKER ENGINE Commands Section

docker build -t "$GUI_IMAGE" . | tee "$OUTPUT"

if ! grep -q "$CHECK_BUILT" "$OUTPUT" || ! grep -q "$CHECK_TAGGED" "$OUTPUT"; then
  # DocKer Build Failure ... No Image Available for VLAB-GUI
  echo "$DOCKER_BUILD_ERROR" && exit 1
fi

docker run $DOCKER_RUN_FLAGS
