#!/bin/bash

clear

echo $'\n A simple tool to check whether a particular host is Dead or Alive!\n'

read opt

if [[ $opt -eq "1" ]]; then
    clear
    tput setaf 172; tput bold; echo $'\n        MANUAL MODE\n';tput sgr0
    echo Enter the host DNS or IP address
    read arg

    ip=$(ping -c 1 $arg | grep -Eo '[0-9.]{9,}' | head -1) 

    if [[ $(ping -c 1 $arg) =~ "from" ]]; then
        tput setaf 2; echo "[+] Congrats the host $arg ($ip) is alive!";tput sgr0
    elif [[ $(ping -c 1 -t 4 $arg) =~ "100.0% packet loss" ]]; then
        (echo > /dev/tcp/$arg/80) &>/dev/null && echo "[+] The Host $arg ($ip) is alive, but has blocked ICMP requests" || echo "[-] Bummer... The host $arg is down"; tput sgr0 
    elif [[ $(ping -q -c 1 %arg &> a.txt; cat a.txt) =~ "cannot resolve" ]]; then
        tput setaf 11; echo "[!] No such Hosts found, please input a valid dns or IP address"; rm a.txt; tput sgr0
    fi
    tput blink;tput setaf 1;tput bold;
    echo "Press any key to continue";tput sgr0
    read key
    ./dead-or-alive.sh
elif [[ $opt -eq "2" ]]; then 
    clear
    tput setaf 172;tput bold;echo $'\n            AUTO MODE\n';tput sgr0
    tput setaf 172;echo 'Enter the absolute path to the host file (1 IP/Host per line)';tput sgr0
    read path
    tput setaf 1;echo 'This may take a while, so please be patient!';tput sgr0;
    input=$path
    while IFS= read -r arg
    do 
    ip=$(ping -c 1 $arg | grep -Eo '[0-9.]{9,}' | head -1)

    if [[ $(ping -c 1 $arg) =~ "from" ]]; then
        tput setaf 2;echo "[+] Congrats the host $arg ($ip) is alive!";tput sgr0
    elif [[ $(ping -c 1 -t 1 $arg) =~ "100.0% packet loss" ]]; then
        (echo >/dev/tcp/$arg/80) &>/dev/null && echo "[+] The Host $arg is ALIVE, but has blocked ICMP requests" || echo "[-] Bummer ... the host $arg ($ip) is down"
    elif [[ $(ping -q -c 1 $arg &> a.txt; cat a.txt) =~ "cannot resolve" ]]; then
        tput setaf 11; echo "[!] Host $arg is not valid, please input a valid dns or IP address"; rm a.txt;tput sgr0
    fi
    done < "$input"
    tput blink;tput setaf 1;tput bold;
    echo "Press any key to continue";tput sgr0
    read key 
    ./dead-or-alive.sh
elif [[ $opt -eq "9" ]]; then
    ./dead-or-alive.sh
elif [[ $opt -eq "0" ]]; then 
    exit
else
    clear
    echo WRONG CHOICE
    ./dead-or-alive.sh
fi