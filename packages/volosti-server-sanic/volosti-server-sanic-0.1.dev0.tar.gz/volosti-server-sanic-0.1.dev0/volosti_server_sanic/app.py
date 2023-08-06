from sanic import Sanic

from volosti_server_sanic.wui import web_user_interface

app = Sanic("Volosti")
app.blueprint(web_user_interface)
