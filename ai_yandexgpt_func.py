import requests
import os
import time
from datetime import datetime, timedelta
from io import BytesIO


#импорт настроек
import settings

oauth_token = settings.oauth_token
model_id = settings.model_id
model_uri = settings.model_uri

def get_iam_token(oauth_token):
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'yandexPassportOauthToken': oauth_token
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['iamToken']

def fetch_yandex_gpt_response(iam_token, model_id, prompt):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json',
    }
    body = {
        "modelUri": model_id,
        "text": prompt,
        "maxTokens": 1000
    }
    body = {
  "modelUri": model_id,
  "completionOptions": {
    "temperature": 0.4,
    "maxTokens": "500"
  },
  "messages": [
    {
      "role": "system",
      "text": "Возьми текст и объедини СЖАТО. Выбери самое АКТУАЛЬНОЕ, УБЕРИ ЛИШНЕЕ. УЛОЖИ ОТВЕТ В 950 символов!"
    },
    {
      "role": "user",
      "text": prompt
    }
  ]
}
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    alternatives = response.json()['result']['alternatives']
    if alternatives:
        return alternatives[0]['message']['text']
    else:
        return "No response from Yandex GPT"

def get_gpt_response(prompt):
    iam_token = get_iam_token(oauth_token)
    try:
        response = fetch_yandex_gpt_response(iam_token, model_id, prompt)
        return response
        print(f"Ответ Яндекс ГПТ: {response}")
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

def get_yandex_art_image(description):
    iam_token = get_iam_token(oauth_token)
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "modelUri": model_uri,  # Замените <catalog_id> на ваш идентификатор каталога
        "generationOptions": {
            "seed": 99
        },
        "messages": [
            {
                "weight": 1,
                "text": description
            }
        ]
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync'
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200 and 'id' in response.json():
        image_data = None
        while not image_data:
            request_id = response.json()['id']
            print('Попытка получить картинку')
            time.sleep(10)  # Подождем, чтобы изображение успело сгенерироваться
            get_image_url = f'https://llm.api.cloud.yandex.net/foundationModels/v1/operations/{request_id}'
            image_response = requests.get(get_image_url, headers=headers)
            print(image_response)
            if image_response.status_code == 200:
                image_data = image_response.json()
                print(image_data)
                if 'response' in image_data and 'image' in image_data['response']:
                    return image_data['response']['image']
    return None

def generate_image(description):
    iam_token = get_iam_token(oauth_token)
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "modelUri": model_uri, 
        "generationOptions": {
            "seed": 99
        },
        "messages": [
            {
                "weight": 1,
                "text": description
            }
        ]
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync'
    response = requests.post(url, headers=headers, json=payload)
    print(response)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if 'id' in data:
            request_id = data['id']
            return request_id
    return None

def get_image_from_yandex(request_id):
    headers = {
        'Authorization': f'Bearer {iam_token}'
    }
    get_image_url = f'https://llm.api.cloud.yandex.net/foundationModels/v1/operations/{request_id}'
    for _ in range(10):  # Попробуем 10 раз с интервалом в 5 секунд
        image_response = requests.get(get_image_url, headers=headers)
        print(image_response)
        if image_response.status_code == 200:
            image_data = image_response.json()
            if 'response' in image_data and 'image' in image_data['response']:
                return image_data['response']['image']
        time.sleep(5)
    return None

def get_image_bytes(base64_image):
    return BytesIO(base64.b64decode(base64_image))



'''
# попытки сделать картинку

print(keywords)
request_id = generate_image(keywords)
print(request_id)
if request_id:
    print(f"Request ID: {request_id}")
    base64_image = get_image_from_yandex(request_id)
    if base64_image:
        image_bytes = get_image_bytes(base64_image)
        with open("image.jpeg", "wb") as f:
            f.write(image_bytes.read())
        print("Image saved successfully!")
    else:
        print("Failed to retrieve the image.")
else:
    print("Failed to generate the image.")
'''