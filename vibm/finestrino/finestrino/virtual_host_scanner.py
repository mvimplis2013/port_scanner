#!/usr/bin/python

import os
import requests

class virtual_host_scanner(object):
    """ Virtual host scanning class

    Virtual host scanner has the following properties:

    Attributes:
        wordlist: location to a wordlist file to use with scans
        target: the target for scanning
        port: the port to scan [default is 80]
        ignore_http_codes: comma-separated list of http codes to ignore
        ignore_content_length: integer value of content length to ignore
        output: folder to write output file to

    """

    def __init__(self, target, output, port=80, ignore_http_codes='404', 
        ignore_content_length=0, wordlist="./wordlist/virtual-host-scanning.txt"
        ):
        self.target = target
        self.output = output + '/' + target + '_virtualhosts.txt'
        self.port = port 
        self.ignore_http_codes = list(map(int, ignore_http_codes.replace(' ', '').split(',')))
        self.ignore_content_length = ignore_content_length
        self.wordlist = wordlist

    def scan(self):
        print("[+] Starting virtual host scan for %s using port %s and wordlist %s" 
            % (self.target, str(self.port), self.wordlist))
        print("[>] Ignoring HTTP codes: %s" 
            % (self.ignore_http_codes))

        if (self.ignore_content_length > 0):
            print("[>] Ignoring Content Length: %s" % (self.ignore_content_length))

        if not os.path.exists(self.wordlist):
            print("[!] Wordlist %s does not exist, exiting virtual host scanner." % self.wordlist)
            return

        virtual_host_list = open(self.wordlist).read().splitlines()
        results = ''

        for virtual_host in virtual_host_list