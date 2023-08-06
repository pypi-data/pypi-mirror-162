from sanic import Blueprint

from volosti_server_sanic.wui.main import main

web_user_interface = Blueprint.group(
    main,
    url_prefix='/',
)
