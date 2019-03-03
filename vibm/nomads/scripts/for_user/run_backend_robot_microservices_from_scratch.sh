### Under Strong Development ...
### Testing & Correcting and maybe Improving

### FROM SCRATCH .. means delete all and get latest release from github
rm -rf nomads 
mkdir nomads
cd nokmads

## STEP 0: Make hosting folder for 
## STEP 1: Download Source && Config files from Github (all included into TGZ) 
# Note: --no-check-certificate ... is not needed to download binary compressed file 

wget https://raw.githubusercontent.com/mvimplis2013/port_scanner/master/vibm/nomads/archives/nomads_devel_source_backend.tgz
tar -xvzf nomads_devel_source_backend.tgz
