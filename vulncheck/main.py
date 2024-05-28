import requests
import os
from datetime import datetime

def read_last_checked_time():
    try:
        with open('./config/time.txt', 'r', encoding='utf-8') as file:
            last_time_str = file.readline().strip()
        return datetime.fromisoformat(last_time_str)
    except FileNotFoundError:
        return datetime.min

def write_last_checked_time(time):
    with open('./config/time.txt', 'w', encoding='utf-8') as file:
        file.write(time.isoformat())

def parse_cve_time(cve_time_str):
    return datetime.fromisoformat(cve_time_str.replace('Z', '+00:00'))

url = "https://api.vulncheck.com/v3/index/nist-nvd2"
headers = {
    "cookie": "token=vulncheck_6973d6a0a88165b652e578ec9b415dc1de2048af6da4ae48f442a5885cca77a0"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    cve_list = data['data']
    
    with open('./config/config.txt', 'r', encoding='utf-8') as file:
        keywords = [line.strip().lower() for line in file.readlines()]

    last_checked_time = read_last_checked_time()
    new_last_checked_time = datetime.now() 
    write_last_checked_time(new_last_checked_time) 
    
    matched_cves = []
    
    for cve in cve_list:
        published_time = parse_cve_time(cve['published'])
        
        if published_time > last_checked_time:
            description = cve['descriptions'][0]['value'].lower()
            if any(keyword in description for keyword in keywords):
                references = [ref['url'] for ref in cve.get('references', [])]
                
                cve_data = {
                    "CVE": cve['id'],
                    "Published": cve['published'],
                    "Description": cve['descriptions'][0]['value'],
                    "References": references
                }
                
                matched_cves.append(cve_data)
    
    if matched_cves:
        filename = 'cve.txt'
        with open(filename, 'w', encoding='utf-8') as output_file:
            for cve_data in matched_cves:
                output_file.write(f"CVE: {cve_data['CVE']}\n")
                output_file.write(f"{'\n'.join(cve_data['References'])}\n")
                output_file.write("\n") 
else:
    print("error api:", response.status_code)
