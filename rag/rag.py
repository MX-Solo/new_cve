from time import sleep
from datetime import datetime
import requests
import json
from googletrans import Translator
import urllib3
from bs4 import BeautifulSoup
from markdown import markdown
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from dotenv import load_dotenv
import os

load_dotenv('./config/config.env')

url = os.getenv("RAGURL")
rag_cookie = os.getenv("RAGCOOKIES")


def markup_to_text(markup_text):
    html = markdown(markup_text)
    text = ''.join(BeautifulSoup(html).findAll(text=True))

    return text

def convert_datetime_format(datetime_str):
    dt = datetime.fromisoformat(datetime_str)
    formatted_date = dt.strftime('%Y-%m-%d')
    return formatted_date

def translate(text , lang='fa'):
    translator = Translator()
    translated_text = translator.translate(text, lang)

    return translated_text.text

def create_json(cve,cve_data):
    references_str = "\n".join(cve_data['References'])
    tags_list = [tag.strip().replace(' ##0$$', '') for tag in cve_data['tags'].split('\n') if tag.strip()]

    data = {
        'tags': tags_list,
        'source': "زفتا",
        'title': title,
        'link': "https://nvd.nist.gov/vuln/detail/" + cve_data["CVE"],
        'summary': summary,
        'info': info,
        'publish_date': publish_date,
        'chart': [2, 92]  # Assuming chart is a constant list
    }

    # Dump the data to JSON with proper indentation and encoding
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    json_file.write(json_data)

    data = {
        'tags': tags_list,
        'source': "زفتا",
        'title': markup_to_text(cve_data['title'].replace('عنوان: ', references_str).replace(' ##0$$', '')),
        'link': "https://nvd.nist.gov/vuln/detail/"+cve,
        'summary': markup_to_text(translate(cve_data['Description'])).replace(' ##0$$', ''),
        'info': markup_to_text(f"{cve_data['description_ai']}\n\nمنابع:\n{references_str}").replace(' ##0$$', '') ,
        'publish_date': convert_datetime_format(cve_data['Published']),
        'chart':[2,92]
    }
    
    print(data)

    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    
    filename = f"{cve}.json"
    with open('./json/'+filename, 'w', encoding='utf-8') as file:
        file.write(json_data)

 

cookies = {
    'session': rag_cookie,
}

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Authorization': 'Imdob19NMWhCbUJ1SUFwZlRFWER4N2tBdElxdW9IcTlicTUzNjZvQjki.ZkxPzg.1dwP0xvnhmt_c2NvD69m-lhtIak',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    # 'Cookie': 'session=gxOG5Et4ZXPXnPEBiEV5VqtMKfbOaQqdxRhZoai-m18',
    'Origin':  url ,
    'Referer':  url +'/knowledge',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def rag(dic):
        for cve, cve_data in dic.items():

            print(f"[+] Working on: {cve}")

            cve_id = cve
            cve_description = cve_data['Description']

            json_data = {
                'name': 'pdf',
            }

            response = requests.post( url +'/v1/kb/create', cookies=cookies, headers=headers, json=json_data,
                                    verify=False)
            if response.status_code == 200:
                kb_id = response.json()['data']['kb_id']
                json_data = {"name": "test", "avatar": "", "description": None, "language": "English", "permission": "me",
                            "embd_id": "BAAI/bge-large-en-v1.5", "parser_id": "naive", "parser_config": {"chunk_token_num": 128},
                            "kb_id": kb_id}
                response = requests.post( url +'/v1/kb/update', cookies=cookies, headers=headers,
                                        json=json_data, verify=False)
                if response.status_code == 200:
                    for idx, ref in enumerate(cve_data['References_bytes']):
                        files = {
                            'file': (f"{cve}_{idx + 1}.pdf", ref, 'application/pdf'),
                            'kb_id': (None, kb_id),
                        }

                        up_headers = headers
                        try:
                            del up_headers['Content-Type']
                        except:
                            pass
                        response = requests.post( url +'/v1/document/upload', cookies=cookies, headers=up_headers,
                                                files=files, verify=False)
                        
                    params = {
                        'kb_id': kb_id,
                        'page': '1',
                        'page_size': '10',
                    }

                    response = requests.get( url +'/v1/document/list', params=params, cookies=cookies, headers=headers, verify=False)
                    if response.status_code == 200:
                        doc_ids =  [docs['id'] for docs in response.json()['data']['docs']]


                    json_data = {
                        'doc_ids': doc_ids,
                        'run': 1,
                    }

                    response = requests.post( url +'/v1/document/run', cookies=cookies, headers=headers,
                                            json=json_data, verify=False)

                    if response.status_code == 200:
                        params = {
                            'kb_id': kb_id,
                            'page': '1',
                            'page_size': '10',
                        }

                        response = requests.get( url +'/v1/document/list', params=params, cookies=cookies,
                                                headers=headers, verify=False)

                        counter = 0
                        while response.json()['data']['docs'][0]['run'] != '3':
                            sleep(40)
                            params = {
                                'kb_id': kb_id,
                                'page': '1',
                                'page_size': '10',
                            }

                            response = requests.get( url +'/v1/document/list', params=params,
                                                    cookies=cookies,
                                                    headers=headers, verify=False)

                            counter += 1
                            if counter >= 3:
                                print("Job failed.")
                                counter = 0
                                json_data = {
                                    'doc_ids': [
                                        doc_ids,
                                    ],
                                    'run': 2,
                                }

                                requests.post( url +'/v1/document/run', cookies=cookies,
                                            headers=headers, json=json_data, verify=False)

                                json_data = {
                                    'doc_ids': [
                                        doc_ids,
                                    ],
                                    'run': 1,
                                }

                                requests.post( url +'/v1/document/run', cookies=cookies,
                                            headers=headers,
                                            json=json_data, verify=False)

                                params = {
                                    'kb_id': kb_id,
                                    'page': '1',
                                    'page_size': '10',
                                }

                                response = requests.get( url +'/v1/document/list', params=params,
                                                        cookies=cookies,
                                                        headers=headers, verify=False)

                        json_data = {
                            'name': 'Assistant 1',
                            'language': 'English',
                            'prompt_config': {
                                'empty_response': '',
                                'prologue': "Hi! I'm your assistant, what can I do for you?",
                                'system': 'You are an intelligent assistant. Please summarize the content of the knowledge base to answer the question. Please list the data in the knowledge base and answer in detail. When all knowledge base content is irrelevant to the question, your answer must include the sentence "The answer you are looking for is not found in the knowledge base!" Answers need to consider chat history.\n      Here is the knowledge base:\n      {knowledge}\n      The above is the knowledge base.',
                                'quote': True,
                                'parameters': [
                                    {
                                        'key': 'knowledge',
                                        'optional': False,
                                    },
                                ],
                            },
                            'kb_ids': [
                                kb_id,
                            ],
                            'llm_id': 'deepseek-chat',
                            'llm_setting': {
                                'temperature': 0.1,
                                'top_p': 0.3,
                                'presence_penalty': 0.4,
                                'frequency_penalty': 0.7,
                                'max_tokens': 2000,
                            },
                            'similarity_threshold': 0.2,
                            'vector_similarity_weight': 0.3,
                            'top_n': 8,
                        }

                        response = requests.post( url +'/v1/dialog/set', cookies=cookies, headers=headers,
                                                json=json_data, verify=False)

                        conversation_id = response.json()['data']['id']

                        queries = {'title' : f"Please generate a concise and informative title for a security vulnerability using the following details:\r\n\r\nCVE ID: {cve_id}\r\nDescription: {cve_description}",
                                   'description_ai': f'Please Generate a detailed description for a security vulnerability identified by its CVE ID, accompanied by the following parameters:\r\nCVE ID: `{cve_id}`\r\nDescription: `{cve_description}`\r\n\r\nPlease ensure the output just includes a detailed description explaining the nature, impact, exploitation (if available) of the vulnerability.',
                                   'tags' : f"Please generate a set of relevant tags for a security vulnerability using the following details. print each tag per line:\r\n\r\nCVE ID: {cve_id}\r\nDescription: {cve_description}"}
                        
                        if response.status_code == 200:
                                json_data = {
                                    'dialog_id': response.json()['data']['id'],
                                    'name': 'AI',
                                    'message': [
                                        {
                                            'role': 'assistant',
                                            'content': '',
                                        },
                                    ],
                                }

                                response = requests.post( url +'/v1/conversation/set', cookies=cookies,
                                                        headers=headers, json=json_data, verify=False)
                                                        

                                if response.status_code == 200:
                                    d_id = response.json()['data']['id']

                                    for  k,q in queries.items() :
                                            
                                            json_data = {
                                                'conversation_id': d_id,
                                                'messages': [
                                                    {
                                                        'role': 'assistant',
                                                        'content': "Hi! I'm your assistant, what can I do for you?",
                                                    },
                                                    {
                                                        'role': 'user',
                                                        'content': q,
                                                    },
                                                ],
                                            }

                                            response = requests.post( url +'/v1/conversation/completion', cookies=cookies,
                                                                    headers=headers, json=json_data, verify=False, stream=True)

                                            if response.status_code == 200:
                                                lines = []
                                                for line in response.iter_lines():
                                                    if line:
                                                        decoded_line = line.decode('utf-8')
                                                        try:
                                                            # Parse the JSON data (if the response is JSON formatted)
                                                            event_data = json.loads(decoded_line[5:])
                                                            lines.append(event_data)
                                                        except json.JSONDecodeError as e:
                                                            pass
                                            
                                                answer = lines[-2]['data'].get('answer', '')

                                                if(k == "tags") :
                                                    cve_data[k] = answer
                                                else :
                                                    translate_text = translate(answer)
                                                    cve_data[k] = translate_text
                                                    print(translate_text)
                                                    
                                    create_json(cve,cve_data)        



                                    json_data = {
                                        'kb_id': kb_id,
                                    }

                                    requests.post( url +'/v1/kb/rm', cookies=cookies,
                                                            headers=headers, json=json_data, verify=False)

                                    json_data = {
                                        'dialog_ids': [
                                            conversation_id,
                                        ],
                                    }

                                    requests.post( url +'/v1/dialog/rm', cookies=cookies,
                                                            headers=headers, json=json_data, verify=False)