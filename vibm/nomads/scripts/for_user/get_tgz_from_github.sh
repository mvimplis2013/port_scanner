# Script variables defined first for easy access
GIT_PROJECT_URL="https://raw.githubusercontent.com/mvimplis2013/port_scanner/master/vibm/nomads"
GIT_ARC_FOLDER="archives"
GIT_ARC_FILENAME="nomads_devel_source.tgz"

LOCAL_VLAB_FOLDER="/opt/vlab/nomads"
LOCAL_NOMADS_FILENAME=$GIT_ARC_FILENAME

TEST_TAR_1="nomads"
# EndOdf Script Variables

if [ ! -d $LOCAL_VLAB_FOLDER ]; then
  # Control will enter here if DIRECTORY doesn't exist
  echo "Ready to create the local VLAB folder ...." + $LOCAL_VLAB_FOLDER
  sudo mkdir -p $LOCAL_VLAB_FOLDER
fi

cd $LOCAL_VLAB_FOLDER

# CAUTION : This is wrong ... if you download archive from github directly ... file-size of downloaded is smaller
# wget --no-check-certificate https://github.com/mvimplis2013/port_scanner/tree/master/vibm/nomads/archives/nomads_dev.tgz

# tar -xvzf nomads_dev.tgz

# IMPORTANT: For correct filesize ... always download from RAW content area
sudo wget -O $LOCAL_NOMADS_FILENAME $GIT_PROJECT_URL/$GIT_ARC_FOLDER/$GIT_ARC_FILENAME --no-check-certificate 

# Check if local file of nomads source code ... Exists ?
if [ ! -s $LOCAL_NOMADS_FILENAME ]; then
  # Problem with archive downloaded from github ... No Source files to mount
  echo "Problem with Archived file ... No sources to mount !"
  exit 1
fi

# Decompress archive with project source code
sudo tar xzf ./$GIT_ARC_FILENAME

if [ ! -d $TEST_TAR_1 ]; then 
  # Problem with source archive decompress
  echo " Problem with Source Archive Decompress ... Folders are missing"
  exit 1
fi