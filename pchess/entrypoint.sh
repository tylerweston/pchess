#!/usr/bin/env bash

# unused? to be removed!

flask db upgrade
flask db migrate
python app.py --host 0.0.0.0