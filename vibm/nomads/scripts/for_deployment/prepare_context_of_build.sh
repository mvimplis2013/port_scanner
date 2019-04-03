# Copy the "appropriate" Dockerfile .. from 'Docker' subfolders to project's main directory

# Lists of Supported Values
declare -a processors_list=("arm" "amd")
declare -a components_list=("collector" "datastore" "gui" "internal-agent")

# ******************************
# *** Processor Manufacturer ***
# ******************************
processor=$1

# Check whether an allowable processor type
found=0
for item in ${processors_list[@]}
do 
  # Processor is handled
  if [ "$item" == "$processor" ]; then
    echo "Processor Found"
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
    echo "Architecture Found"
    found=1
  fi
fi

if [ $found == 0 ]; then
  # Not Supported Architecture ... Aborting
  echo "Defined Architecture Not Supported ... Aborting !"
  exit 1
fi

# ***********************************
# *** Project's Module/ Component ***
# ***********************************
component=$3

found=0
for item in ${components_list[@]}
do 
  if [ "$component" == "$item" ]; then
    echo "Project Component Found"
    found=1 && break
  fi
done

if [ $found == 0 ]; then
  # Not Supported Project Component ... Aborting 
  echo "Defined Project Component Not Supported ... Aborting !"
  exit 1
fi

# *************************************************************************
# *** Query Docker subfolders .. for specified processor & architecture ***
# *************************************************************************
target_folder="docker/"$processor"/"$architecture"/"$component

if [ ! -d "$target_folder" ]; then
  echo "Target Folder with Compatible Dockerfile Not Found ... Aborting !"
  exit 1
fi

dockerfile=$target_folder"/Dockerfile"
if [ ! -f "$dockerfile" ]; then 
  echo "Target Dockerfile Not Found ... Aborting !"
  exit 1
fi

# All tests OK ... hosting folder && requested dockerfile ... exist
cp "$dockerfile" ./
