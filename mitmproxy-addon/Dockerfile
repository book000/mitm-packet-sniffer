FROM mitmproxy/mitmproxy:12.3.0@sha256:c8a3753de11fd8266afeb103e163f7b7ac6a4a568a707fa2e15b23d20acf4eba

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY main.py /app/main.py

ENV TZ=Asia/Tokyo

ENTRYPOINT ["/app/entrypoint.sh"]
