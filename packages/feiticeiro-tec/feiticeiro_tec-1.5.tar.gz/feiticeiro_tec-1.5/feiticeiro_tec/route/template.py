from flask import request, render_template
from functools import wraps
from werkzeug.wrappers.response import Response


def response_template(template, path_prefix='/api'):
    def capture_func(f):
        @wraps(f)
        def capture_args(*args, **kw):
            response = f(*args, **kw)
            if type(response) == Response:
                return response

            if type(response) in(tuple,list):
                response, status = response
            else:
                status = 200

            if request.path.startswith(path_prefix):
                return response, status
            else:
                return render_template(template, **response), status
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