import base64
import json

import requests

url = 'https://europe-west1-salesrecon.cloudfunctions.net/function-1'
image_file = "D:\\projects\\GoogleHackaton\\testAI\\20220122_170004.jpg"


if __name__ == '__main__':

    with open(image_file, "rb") as f:
        im_bytes = f.read()
    im_b64 = base64.b64encode(im_bytes).decode("utf8")

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    payload = json.dumps({"image": im_b64, "product": "cola"})
    response = requests.post(url, data=payload, headers=headers)
    try:
        data = response.json()
        print(data)
    except requests.exceptions.RequestException:
        print(response.text)
