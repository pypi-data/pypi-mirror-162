#!/usr/bin/env python3
import requests

tlds = open('core/tld.txt', 'r').readlines()
ctld = []

for element in tlds:
    ctld.append(element.strip())

header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
def scanner(domain):
    for tld in ctld:
        try:
            req = requests.get(f"http://{domain}.{tld}", headers=header)
            if req.status_code == "404" or "301" or "200":
                print(domain+"."+tld)
        except requests.exceptions.ConnectionError:
            pass