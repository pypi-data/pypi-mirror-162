#encodeing: utf-8


import requests
from tqdm import tqdm

def download(url: str, fname: str):
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77"
    }
    resp = requests.get(url, stream=True, headers=header)
    total = int(resp.headers.get('content-length',0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


