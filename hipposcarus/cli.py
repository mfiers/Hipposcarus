
from bottle import run

from . import views
from .util import get_flask_app

def deploy():
    app = get_flask_app()
    app.run(debug=True, port=8080, host="0.0.0.0")
    #run(host='localhost', port=8080, debug=True, reloader=True)
