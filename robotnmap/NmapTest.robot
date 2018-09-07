*** Settings ***
Library RoboNmap
Library Collections

*** Variables ***
${TARGET} example.com

*** Test Cases ***
Run Basic Port Scan
    nmap_script_scan ${TARGET} version_intense=3 file_export=nmap.txt
    nmap_print_results