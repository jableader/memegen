import os
import requests

def test_prompt():
    BASE_URL = os.getenv('BASE_URL')
    assert BASE_URL is not None

    res = requests.post(f'{BASE_URL}/prompt', json={
      'style': 'Modern James Bond Film',
      'story': 'A cowboy fights aliens'
    })

    js = res.get_json()
    assert 'Bond' in js['style']
    assert len(js['frames']) == 4