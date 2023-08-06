from starlette.applications import Starlette

from volosti_server_starlette.wui import web_user_interface

app = Starlette(
    debug=True,
    routes=[
        web_user_interface,
    ],
)
