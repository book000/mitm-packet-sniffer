#!/bin/bash

echo "Starting mitmproxy"

/usr/local/bin/mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/