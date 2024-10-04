import json

import json

from flask import Blueprint, request

app_webhook = Blueprint('webhook', __name__)

@app_webhook.route('/api/webhook/')
def hello_world():
    if request.method == 'POST':
        try:
            data = request.data.decode('utf-8')  # Декодируем данные из байтового объекта в строку
            print(data)
        except Exception as e:
            return {'result': 'Unable to parse data: {}'.format(str(e))}
    elif request.method == 'GET':
        return {'result1' : 'success for get '}
