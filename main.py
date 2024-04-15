import requests

iam_token = 't1.9euelZrJxpOdk52OjZCJnJOdjcaKiu3rnpWanJ3Hyp6OzZGYi5TGzYrIlZHl8_ceNzRQ-e8uKHAM_t3z915lMVD57y4ocAz-zef1656Vmoudx42YyY6Tk5uOzI_PzI-O7_zF656Vmoudx42YyY6Tk5uOzI_PzI-OveuelZrJm5vMlM3Oz5fGyY2Njo6PjLXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.YlB095LQZ4et_-uSe5rEVZYw5MXSTjlDMBSrrHSJp60yfERI-tJ527MgyxolXQnjLtYKUhTPX3cRzQsQqJomAA'


def text_to_speech(text):

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'emotion': 'good',
        'voice': 'jane',
        'speed': '1',
        'folderId': "b1gm3iaupnoqro4lc9lk",
    }

    # Выполняем запрос
    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

    if response.status_code == 200:
        return True, response.content  # Возвращаем голосовое сообщение
    else:
        return False, "Возникла ошибка при запросе в SpeechKit!"