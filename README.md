# stellar-get-ap-macs
Quick tool to get a list of Stellar AP MAC addresses from OmniVista 2500

# Example
```
$ python3 stellar-get-ap-macs.py 

Stellar Get-AP-MACs - a simple tool to obtain the Stellar AP managed by given OmniVista Enterprise
Written by Benny Eggerstedt in 2019
This is free software not provided/shipped by Alcatel-Lucent Enterprise. Use it at your own risk!

[+] Reading settings.json file
[*] Attempting to connect to OmniVista server @ https://omnivista.home
[*] Connection to omnivista.home successful!
[*] Get list of Stellar APs from OmniVista @ omnivista.home
[*] Found 2 Stellar Wireless AP(s)
ALE OmniSwitch AOS CLI command:
policy mac group MG_trusted_APs dc:08:56:aa:aa:aa dc:08:56:bb:bb:bb
```
