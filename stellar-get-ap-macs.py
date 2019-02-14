#!/usr/bin/env python3

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

#
# This script is meant to return a list of Stellar APs managed by the given OmniVista Enterprise
#

# TODO
# -

#
# Imports
#
import sys
try:
    import requests
except ImportError as ie:
    print(ie)
    sys.exit("Please install python-requests!")
import json
import random
import urllib3
import uuid

#
# Functions
#

print("\nStellar Get-AP-MACs - a simple tool to obtain the Stellar AP managed by given OmniVista Enterprise")
print("Written by Benny Eggerstedt in 2019")
print("This is free software not provided/shipped by Alcatel-Lucent Enterprise. Use it at your own risk!\n")

# Load settings from settings.json file
print("[+] Reading settings.json file")
try:
    with open("settings.json", "r") as json_data:
        settings = json.load(json_data)
        ov_hostname = settings["ov_hostname"]
        ov_username = settings["ov_username"]
        ov_password = settings["ov_password"]
        validate_https_certificate = settings["validate_https_certificate"]
        #ap_groups = settings["ap_groups"]
        #ssid = settings["ssid"]
        #encr = settings["encryption"]
        #psk_length = settings["psk_length"]
        #send_psk_via_mail = settings["send_psk_via_mail"]
        #email_from = settings["email_from"]
        #smtp_server = settings["smtp_server"]
        #smtp_auth = settings["smtp_auth"]
        #smtp_user = settings["smtp_user"]
        #smtp_port = settings["smtp_port"]
        #smtp_password = settings["smtp_password"]
        #language = settings["language"]
        #email_to = settings["email_to"]
except IOError as ioe:
    print(ioe)
    sys.exit("ERROR: Couldn't find/open settings.json file!")
except TypeError as te:
    print(te)
    sys.exit("ERROR: Couldn't read json format!")

# Validate that setting.json is configured and not using the default
if ov_hostname == "omnivista.example.com":
    sys.exit("ERROR: Can't work with default template value for OmniVista hostname!")

# Validate that the hostname is a hostname, not URL
if "https://" in ov_hostname:
    print("[!] Found \"https://\" in ov_hostname, removing it!")
    ov_hostname = ov_hostname.lstrip("https://")

# Validate that the hostname doesn't contain a "/"
if "/" in ov_hostname:
    print("[!] Found \"/\" in hostname, removing it!")
    ov_hostname = ov_hostname.strip("/")


# Figure out if HTTPS certificates should be validated
# That should actually be the default, so we'll warn if disabled.

if(validate_https_certificate.lower() == "yes"):
    check_certs = True
else:
    # This is needed to get rid of a warning coming from urllib3 on self-signed certificates
    print("[!] Ignoring certificate warnings or self-signed certificates!")
    print("[!] You should really fix this!")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    check_certs = False    

# Test connection to OmniVista
print("[*] Attempting to connect to OmniVista server @ https://{0}".format(ov_hostname))

req = requests.Session()

# Use the ca-certificate store managed via Debian
# This is just for development, should be commented out for production.
req.verify = "/etc/ssl/certs/"

# Check if we die on the HTTPS certificate
try:
    ov = req.get("https://{0}".format(ov_hostname), verify=check_certs)
except requests.exceptions.SSLError as sslerror:
    print(sslerror)
    sys.exit("[!] Caught issues on certificate, try to change \"validate_https_certificate\" to \"no\" in settings.json. Exiting!")

if ov.status_code == 200:
    print("[*] Connection to {0} successful!".format(ov_hostname))
else:
    sys.exit("[!] Connection to {0} failed, exiting!".format(ov_hostname))

ov_login_data = {"userName" : ov_username, "password" : ov_password}
ov_header = {"Content-Type": "application/json"}

# requests.post with json=payload was introduced in version 2.4.2
# otherwise it would need to be "data=json.dumps(ov_login_data),"

ov = req.post("https://{0}/api/login".format(ov_hostname),
              headers=ov_header,
              json=ov_login_data,
              verify=check_certs)

if ov.status_code == 200:
    token = ov.json()
    token = token["accessToken"]
    ov_header["Authorization"] = "Bearer {0}".format(token)
else:
    sys.exit("[!] The connection to OmniVista was not successful! Exiting!")

print("[*] Get list of Stellar APs from OmniVista @ {0}".format(ov_hostname))

ap_full_details = req.get("https://{0}/api/wma/accessPoint/getAPList/normal".format(ov_hostname),
                        headers=ov_header,
                        verify=check_certs)

if ap_full_details.status_code == 200:
    ap_list = ap_full_details.json()
    ap_list = ap_list["data"]
    print("[*] Found {0} Stellar Wireless AP(s)".format(len(ap_list)))
    ap_macs = []
    policy_statement = "policy mac group MG_trusted_APs"
    for ap in ap_list:
        ap_macs.append(ap["macAddress"])
        policy_statement = policy_statement + " {0}".format(ap["macAddress"])
    print("ALE OmniSwitch AOS CLI command:")
    print(policy_statement)
else:
    sys.exit("[!] Couldn't get AP list from OmniVista! Exiting!")
