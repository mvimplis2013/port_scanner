set GIT_PROJECT_URL="https://raw.githubusercontent.com/mvimplis2013/port_scanner/master/vibm/nomads"
set GIT_ARC_FOLDER="archives"
set GIT_ARC_FILENAME="nomads_devel_source.tgz"

set LOCAL_VLAB_FOLDER="/opt/vlab/"
set LOCAL_NOMADS_FILENAME=$GIT_ARC_FILENAME

if [ ! -d $LOCAL_VLAB_FOLDER ]; then
  # Control will enter here if DIRECTORY doesn't exist
  echo "Ready to create the local VLAB folder ...." + $LOCAL_VLAB_FOLDER
  sudo mkdir $(LOCAL_VLAB_FOLDER)
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

sudo tar xzf ./$GIT_ARC_FILENAME