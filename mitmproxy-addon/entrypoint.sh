#!/bin/bash

echo "Starting mitmproxy"

/usr/local/bin/mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/ &
mitmdump_pid=$!

# PID 1 (init: true 経由の tini) から受け取った SIGTERM/SIGINT を
# バックグラウンド実行中の mitmdump に転送する（trap を張らないと
# シグナルが mitmdump まで届かず、停止が遅延する可能性があるため）
trap 'kill -TERM "$mitmdump_pid" 2>/dev/null' TERM INT

wait "$mitmdump_pid"
exit_code=$?

# 正常終了(0)および SIGTERM による終了(143)以外の異常終了時のみ、
# ホストへの再起動連打を避けるために30 秒待機してから終了する
if [ "$exit_code" -ne 0 ] && [ "$exit_code" -ne 143 ]; then
    echo "mitmdump exited with code $exit_code. Waiting 30s before exiting to avoid hammering the host with rapid restarts."
    sleep 30
fi

exit "$exit_code"