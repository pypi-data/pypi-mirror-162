from flask import Blueprint

from apidoc import apidoc
from service import HomeService

_home = Blueprint('home', __name__)


@apidoc.doc()
@_home.get('/')
def home():
    return HomeService().say_hello()
