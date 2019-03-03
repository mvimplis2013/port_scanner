#!/bin/bash
goodnames=("gui" "backend")
appname=$1

found=0
for element in "${goodnames[@]}"; do 
    if [[ $element == $appname ]]; then
        found=1
        break
    fi
done

if [[ $found != 1 ]]; then
    echo "Invalid Module Name ... ABORD"
    exit 1
fi

tool="tar"

flags="-cvzf" 

tgz_name="archives/nomads_devel_source_"
tgz_name="$tgz_name""$appname"".tgz"
#echo "$tgz_name"

src_folder="nomads/"
src_folder="$src_folder""$appname""/"
test_folder="tests/"
test_folder="$test_folder""$appname""/"
conf_folder="config/"
conf_folder="$conf_folder""$appname""/"

requirements_txt="./requirements-back-robot.txt"

exclude_folder="__pycache__"

$tool $flags $tgz_name $src_folder $test_folder $conf_folder $requirements_txt --exclude=$exclude_folder