tool="tar"

flags="-cvzf" 

tgz_name="archives/nomads_devel_source.tgz"

src_folder="nomads/"
test_folder="tests"

exclude_folder="__pycache__"

$tool $flags $tgz_name $src_folder $test_folder --exclude=$exclude_folder