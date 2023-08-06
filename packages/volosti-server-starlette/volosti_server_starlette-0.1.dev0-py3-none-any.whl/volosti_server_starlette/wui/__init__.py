from starlette.routing import Mount

from volosti_server_starlette.wui.main import main

web_user_interface = Mount('/', routes=[
    main,
])
