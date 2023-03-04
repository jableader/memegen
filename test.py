import os
import requests

def test_prompt():
    BASE_URL = os.getenv('BASE_URL')
    assert BASE_URL is not None

    res = requests.post(f'{BASE_URL}/prompt', json={
      'style': 'Simpsons Cartoon',
      'story': 'A cowboy fights aliens'
    })

    js = res.json()
    assert 'cartoon' in js['setting']
    assert len(js['frames']) == 4
    assert 'frameDescription'in js['frames'][0]
    assert 'caption'in js['frames'][0]