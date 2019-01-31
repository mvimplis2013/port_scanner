# Copy the "appropriate" Dockerfile .. from 'Docker' subfolders to project's main directory

# ******************************
# *** Processor Manufacturer ***
# ******************************
processor=$1

# Check whether an allowable processor type
found=0

declare -a processors_list=("arm" "amd")
for item in ${processors_list[@]}
do 
  # Processor is handled
  if [ "$item" == "$processor" ]; then
    echo "Processor found"
    found=1 && break
  fi
done

if [ $found == 0 ]; then
  # Processor Not Supported 
  echo "Defined Processor Not Supported ... Aborting !"
  exit 1
fi

# ********************
# *** Architecture ***
# ********************
architecture=$2

found=0
if [ "$processor" == "arm" ]; then
  if [[ ("$architecture" == "x32") || ("$architecture" == "x64") ]]; then 
    echo "Architecture found"
    found=1
  fi
fi

if [ $found == 0 ]; then
  # Not Supported Architecture ... Aborting
  echo "Defined Architecture Not Supported ... Aborting !"
  exit 1
fi

# *************************************************************************
# *** Query Docker subfolders .. for specified processor & architecture ***
# *************************************************************************
if [ -d "docker/"$processor"/"$architecture ]; then
  echo "Folder Found"
  cp "docker/"$processor"/"$architecture/gui/Dockerfile ./
fi