import os

import requests


def remove_voice(voice_id):
    headers = {
        'Authorization': f'Bearer {os.getenv("API_KEY")}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "voice-enrollment",
        "input": {
            "action": "delete_voice",
            "voice_id": voice_id
        }
    }
    response = requests.post(os.getenv('VOICE_URL'), json=data, headers=headers)
    return response.json()
