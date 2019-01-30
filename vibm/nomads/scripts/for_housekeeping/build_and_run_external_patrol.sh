if [ -z "$1" ]; then
  # Must define the folder with Dockerfiles to proceed ... 
  echo "You must specify the Dockerfile(s) hosting folder ... Aborting!"
  exit 1
fi

if [ ! -d "$1" ]; then
  # User deined argument must be .. a valid directory
  echo "You must specify a valid directory ... Aborting !" 
  exit 1
fi

found=0
for entry in "$1"/*
# For every file inside the folder
do 
  echo $entry
  if [[ $entry == *Dockerfile ]]; 
  then 
    # Found a Dockerfile inside the folder
    DOCKERFILE_DIR="$1"
    found=1
  fi
done

if [ $found == 0 ]; 
then
  # No Dockerfile Found to Build & Run ... Aborting!
  echo "No Dockerfile found inside the specified path ... Aborting !"
  exit 1
fi

docker build -t vlab-docker $DOCKERFILE_DIR/.
docker run -it --rm -v /opt/vlab/nomads:/nomads/ -t vlab-docker python /nomads/nomads/logger.py 