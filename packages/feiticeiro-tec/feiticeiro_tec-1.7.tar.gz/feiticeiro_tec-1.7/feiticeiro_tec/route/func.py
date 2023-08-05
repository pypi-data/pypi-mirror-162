from flask import request
from contextlib import suppress
from functools import wraps


def call_func(route_acepts=[], args_acepts=[]):
    def capture_func(f):
        @wraps(f)
        def capture_args(*args, **kw):
            data = kw.get('_data')#! Para Chamadas Internas
            if type(data) == dict:
                return f(data=data,_api=True)

            if request.is_json:
                data = dict(request.json)
            else:
                data = {**dict(request.form), **dict(request.files)}

            for key in args_acepts:
                data[key] = request.args.get(key)

            for key in route_acepts:
                data[key] = kw.get(key)
            return f(data=data)
        return capture_args
    return capture_func

if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)

    @app.route('/<id>/',methods=['GET','POST'])
    @call_func(route_acepts=['id'],args_acepts=['teste'])
    def index(data={}):
        return {
            "id":data.get('id'),
            "usuario":"silvio",
            "senha": data.get('teste')
            },400