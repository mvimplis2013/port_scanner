tool="tar"

flags="-cvzf" 

tgz_name="archives/nomads_devel_config.tgz"

config_folder="config/"
requirements_file="dev_requirements.txt"

$tool $flags $tgz_name $requirements_file $config_folder