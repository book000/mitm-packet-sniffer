FROM mitmproxy/mitmproxy:10.2.3

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY main.py /app/main.py

ENV TZ=Asia/Tokyo

ENTRYPOINT ["/app/entrypoint.sh"]

