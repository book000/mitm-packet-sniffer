#!/bin/bash

echo "Starting mitmproxy"

/usr/local/bin/mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/
exit_code=$?

# 正常終了(0)および SIGTERM による終了(143)以外の異常終了時のみ、
# ホストへの再起動連打を避けるために30秒待機してから終了する
if [ "$exit_code" -ne 0 ] && [ "$exit_code" -ne 143 ]; then
    echo "mitmdump exited with code $exit_code. Waiting 30s before exiting to avoid hammering the host with rapid restarts."
    sleep 30
fi

exit "$exit_code"