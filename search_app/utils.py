import requests

def download_image(url: str, save_path: str):
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)