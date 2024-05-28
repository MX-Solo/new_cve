import requests
from datetime import datetime
from urllib.parse import urlparse
from pyhtml2pdf import converter  # Assuming converter.convert is the function to convert URLs to PDFs
import io
from rag import rag
from dotenv import load_dotenv
import os

load_dotenv('./config/config.env')

url = os.getenv("API_VULENCHECK")
token = os.getenv("VULENCHECK_API")

headers = {
    "cookie": token
}
cve_dic = {}

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

def process_link(cve_id, idx, link):
    pdf_filename = f"{cve_id}_{idx + 1}.pdf"
    print(f'[+] Generating PDF: {pdf_filename} from {link}')
    try:
        result = io.BytesIO(converter.convert(link, pdf_filename))
        print(f'PDF created: {pdf_filename}')
        return result

    except Exception as e:
        print(f"Error processing link {link}: {e}")




response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    cve_list = data['data']
    
    with open('./config/config.ini', 'r', encoding='utf-8') as file:
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
        # Create PDFs for each matched CVE using concurrent.futures
        for cve in matched_cves:
            cve_id = cve['CVE']
            references = cve['References']
            
            cve_info = {
                'References': references,
                'References_bytes': [],
                'Published':cve['Published'],
                'Description' : cve['Description'],
            }
            
            
            for idx, link in enumerate(references):
                parsed_url = urlparse(link)
                if parsed_url.netloc.endswith('vuldb.com'): continue 
                result = process_link(cve_id, idx, link)
                cve_info['References_bytes'].append(result)
            
            cve_dic[cve_id] = cve_info
        rag(cve_dic)


else:
    print("Error API:", response.status_code)
