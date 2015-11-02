
import os

from flask import Flask
import humanize
from jinja2 import Environment, PackageLoader, FileSystemLoader

from path import Path

JENV = None
APP = None

def get_dynamic_dir(name=None):
    """g
    Folder containing the dynamically server generated content
    """
    ddir = Path('~/data/hipposcarus/dynamic').expanduser()
    if not name is None:
        ddir /= name
        
    if not ddir.exists():
        os.makedirs(ddir)
    return ddir


def get_static_dir():
    return Path(__file__).dirname().dirname() / 'static'


def get_flask_app():
    global APP
    if not APP is None:
        return APP
    APP = Flask(__name__)
    return APP


def shasum_to_colors(v):
    rv = []
    w = v
    while w:
        tb, w = (w[:6] + 'ffffff')[:6], w[6:]
        rv.append('<span class="shacol" style="background-color: #%s;">&nbsp;</span>' % (tb,))
    return("".join(rv))
        
    
def get_jinja_env():
    global JENV
    
    if not JENV is None:
        return JENV

    JENV = Environment(loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))

    def _naturalsize(v):
        try:
            return humanize.naturalsize(v)
        except:
            return "n.a."
    JENV.filters['humanfilesize'] = lambda v: _naturalsize(v)
#    JENV.filters['humanfilesize'] = lambda v: type(v)
    JENV.filters['humanday'] = lambda v: humanize.naturalday(v)
    JENV.filters['shacol'] = shasum_to_colors
    return JENV


def render(template_name, context={}):
    env = get_jinja_env()
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)
    
