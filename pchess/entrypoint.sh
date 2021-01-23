#!/usr/bin/env bash
flask db upgrade
flask db migrate
python app.py --host 0.0.0.0