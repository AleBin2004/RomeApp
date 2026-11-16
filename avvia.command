#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
(sleep 2; open http://localhost:8080) &
python3 server.py
