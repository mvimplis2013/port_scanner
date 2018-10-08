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

    def __init__(self, target, output, port=80, ignore_http_codes=`404`, ignore_content_length=0, wordlist="./wordlist/virtual-host-scanning.txt"):
        self.target = target
        self.output = output        