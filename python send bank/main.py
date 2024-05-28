import json
import os
import urllib.request
import urllib.error

def log_error(message):
    with open("error.log", "a", encoding='utf-8') as error_file:
        error_file.write(message + "\n")

bearer_file_path = "./bearer_token.txt"

with open(bearer_file_path, 'r', encoding='utf-8') as bearer_file:
    bearer_token = bearer_file.read().strip()

json_files_path = "./news_file"

json_files = [f for f in os.listdir(json_files_path) if f.endswith('.json')]

for json_file in json_files:
    file_path = os.path.join(json_files_path, json_file)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        url = "http://*/api/news/vulnerability-news/"

        data = {
            "publish_date": json_data["publish_date"],
            "title": json_data["title"],
            "source": json_data["source"],
            "link": json_data["link"],
            "summary": json_data["summary"],
            "info": json_data["info"],
            "chart": json_data["chart"],
            "tags": json_data["tags"]
        }

        data = json.dumps(data).encode('utf-8')

        headers = {
            "Host": "*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"{bearer_token}",
            "Origin": "http://*",
            "Connection": "close",
        }

        req = urllib.request.Request(url, data=data, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    response_text = response.read().decode('utf-8')
                    print(f"✔ Successfully sent: {json_file}")
                    # Delete the JSON file if request is successful
                    os.remove(file_path)
                else:
                    error_message = f"✘ Error: Received response code {response.status} for file {json_file}"
                    print(error_message)
                    log_error(error_message)
                    log_error(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_message = f"✘ HTTPError: {e.code} for file {json_file}"
            print(error_message)
            log_error(error_message)
            log_error(e.read().decode('utf-8'))
        except urllib.error.URLError as e:
            error_message = f"✘ URLError: {e.reason} for file {json_file}"
            print(error_message)
            log_error(error_message)
    
    except json.JSONDecodeError:
        error_message = f"✘ JSONDecodeError: Could not parse file {json_file}"
        print(error_message)
        log_error(error_message)
    except Exception as e:
        error_message = f"✘ Unexpected error with file {json_file}: {str(e)}"
        print(error_message)
        log_error(error_message)
