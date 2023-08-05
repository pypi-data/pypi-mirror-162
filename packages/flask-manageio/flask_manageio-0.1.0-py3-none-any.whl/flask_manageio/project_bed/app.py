from flask import Flask, render_template
from db import db
from ma import ma
from apidoc import apidoc

from controller import _home

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
ma.init_app(app)
apidoc.init_app(app)


"""Register blueprints"""
app.register_blueprint(_home)
"""-/Register blueprints"""


@apidoc.doc()
@app.route('/doc')
def documented_endpoints():
    return render_template("index.html", value=apidoc.generate())


if __name__ == '__main__':
    app.run(port=5001, debug=True)
