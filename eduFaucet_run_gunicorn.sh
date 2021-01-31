#!/bin/bash

gunicorn -w 4 -b ymca.cnap.hv.se:8331 eduFaucet_webserver:app -t 900

