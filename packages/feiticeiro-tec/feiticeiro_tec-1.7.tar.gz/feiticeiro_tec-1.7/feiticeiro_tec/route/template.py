from contextlib import suppress
from flask import request, render_template
from functools import wraps
from werkzeug.wrappers.response import Response as wr
from flask.wrappers import Response as fr



def response_template(template, path_prefix='/api'):
    def capture_func(f):
        @wraps(f)
        def capture_args(*args, **kw):
            api = False
            if kw.get('_api') == True:
                api = True
            with suppress(Exception):
                kw.pop('_api')

            response = f(*args, **kw)
            if type(response) == wr or type(response) == fr:
                return response

            if type(response) in(tuple,list):
                response, status = response
            else:
                status = 200

            if type(response) == wr or type(response) == fr:
                return response, status

            if request.path.startswith(path_prefix) or api:
                return response, status

            elif type(response) == dict:
                return render_template(template, **response), status
            else:
                return response, status
        return capture_args
    return capture_func

if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)

    @app.route('/',methods=['GET','POST'])
    @response_template('index.html')
    def index():
        return {
            "id":1,
            "usuario":"silvio",
            "senha":"secreta"
            },400