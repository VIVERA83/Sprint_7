#!/bin/sh
flask db init
flask db migrate
flask db upgrade
python wsgi.py init_roles
python wsgi.py init_superuser "${AUTH_LOGIN}" "${AUTH_PASSWORD}"
python wsgi.py

