import sys

from gevent import monkey

monkey.patch_all()

import logging
from gevent.pywsgi import WSGIServer  # noqa
from src.core.config import settings  # noqa
from src.core.settings import app  # noqa
from src.db.postgres import init_roles, init_superuser

if __name__ == "__main__":
    if len(sys.argv) == 1:
        logging.basicConfig(level=logging.INFO)
        http_server = WSGIServer((settings.auth_host, settings.auth_port), app)
        http_server.serve_forever()
    elif (len(sys.argv) == 4) and sys.argv[1] == "init_superuser":
        with app.app_context():
            init_superuser(sys.argv[2], sys.argv[3])
    elif (len(sys.argv) == 2) and sys.argv[1] == "init_roles":
        with app.app_context():
            init_roles()
