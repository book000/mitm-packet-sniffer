import atexit
import base64
import datetime
import hashlib
import json
import os
from xml.etree import ElementTree

from mitmproxy import ctx, http, tls
from mitmproxy.utils import human
from mysql import connector


class Database:
    def __init__(self):
        self.connection = connector.connect(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'] if 'DB_PORT' in os.environ else 3306,
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME']
        )

        if not self.connection.is_connected():
            raise Exception('Database connection failed')

        self.cursor = self.connection.cursor()

    def insert_response(self, flow: http.HTTPFlow):
        sql = "INSERT INTO `responses` (`host`, `port`, `method`, `scheme`, `authority`, `path`, `path_hash`, `query`, `request_content`, `request_content_type`, `http_version`, `request_headers`, `status_code`, `response_headers`, `response_content`, `response_content_type`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        host = flow.request.host
        port = flow.request.port
        method = flow.request.method
        scheme = flow.request.scheme
        authority = flow.request.authority
        path = flow.request.path
        path_hash = self.get_md5hash(path)
        query = json.dumps(dict(flow.request.query))
        raw_request_headers = flow.request.headers
        request_headers = json.dumps(dict(raw_request_headers))
        request_content = flow.request.get_content()
        request_content_type = self.get_contenttype(request_content)
        if request_content_type == 'BINARY':
            request_content = self.to_base64(request_content)
        http_version = flow.request.http_version

        status_code = flow.response.status_code
        raw_response_headers = flow.response.headers
        response_headers = json.dumps(dict(raw_response_headers))
        content = flow.response.get_content()
        content_type = self.get_contenttype(content)
        if content_type == 'BINARY':
            content = self.to_base64(content)

        self.cursor.execute(sql, (host, port, method, scheme, authority, path, path_hash, query, request_content, request_content_type, http_version, request_headers, status_code, response_headers, content, content_type))
        self.connection.commit()

    def is_ignore_hosts(self, address: str):
        sql = "SELECT `last_seen_at`, `next_check_phase` FROM `ignore_hosts` WHERE `address` = %s"
        self.cursor.execute(sql, (address,))
        row = self.cursor.fetchone()

        # レコードが存在しない場合はFalse
        if row is None:
            return False

        # レコードが存在する場合は、is_next_check メソッドの結果によって判定
        return not self.is_next_check(row[0], row[1])

    def upsert_ignore_host(self, address: str):
        sql = "INSERT INTO `ignore_hosts` (`address`, `last_seen_at`) VALUES (%s, NOW()) ON DUPLICATE KEY UPDATE `last_seen_at` = NOW(), `next_check_phase` = `next_check_phase` + 1"
        self.cursor.execute(sql, (address,))
        self.connection.commit()

    def delete_ignore_host(self, address: str):
        sql = "DELETE FROM `ignore_hosts` WHERE `address` = %s"

        try:
          self.cursor.execute(sql, (address,))
          self.connection.commit()
        except:
          pass

    def is_next_check(self, last_seen_at: datetime.datetime, next_check_phase: int):
        # 1回目: 1分後
        # 2回目: 5分後
        # 3回目: 30分後
        # 4回目: 1時間後
        # 5回目: 3時間後
        # 6回目: 6時間後
        # 7回目: 12時間後
        # 8回目: 24時間後
        # 9回目: 48時間後
        # 10回目以降: 無制限
        timedeltas = {
            1: datetime.timedelta(minutes=1),
            2: datetime.timedelta(minutes=5),
            3: datetime.timedelta(minutes=30),
            4: datetime.timedelta(hours=1),
            5: datetime.timedelta(hours=3),
            6: datetime.timedelta(hours=6),
            7: datetime.timedelta(hours=12),
            8: datetime.timedelta(hours=24),
            9: datetime.timedelta(hours=48),
        }

        if next_check_phase not in timedeltas:
            return False

        next_check_at = last_seen_at + timedeltas[next_check_phase]
        now = datetime.datetime.now()

        return next_check_at < now


    def get_md5hash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def get_contenttype(self, content: bytes | None):
        if content is None:
            return 'NULL'

        if self.is_binary(content):
            return 'BINARY'

        text = content.decode('utf-8')

        if self.is_json(text):
            return 'JSON'

        if self.is_xml(text):
            return 'XML'

        return 'TEXT'

    def is_binary(self, content: bytes):
        try:
            content.decode('utf-8')
            return False
        except:
            return True

    def is_json(self, content):
        try:
            json.loads(content)
            return True
        except:
            return False

    def is_xml(self, content):
        try:
            ElementTree.fromstring(content)
            return True
        except:
            return False

    def to_base64(self, content: bytes):
        return base64.b64encode(content).decode('utf-8')

    def close(self):
        self.cursor.close()
        self.connection.close()

db = Database()

# Ctrl+C で終了した場合にDB接続を閉じる
def exit_handler():
  db.close()

atexit.register(exit_handler)

# ---- mitmproxy ハンドラー ----

async def response(flow: http.HTTPFlow):
  db.insert_response(flow)

def tls_clienthello(data: tls.ClientHelloData):
    if data.client_hello.sni:
        dest = data.client_hello.sni
    else:
        dest = human.format_address(data.context.server.address)

    if db.is_ignore_hosts(dest):
        data.ignore_connection = True

def tls_established_client(data: tls.TlsData):
    if data.conn.sni:
        dest = data.conn.sni
    else:
        dest = human.format_address(data.context.server.address)

    db.delete_ignore_host(dest)

def tls_failed_client(data: tls.TlsData):
    if data.conn.sni:
        dest = data.conn.sni
    else:
        dest = human.format_address(data.context.server.address)

    ctx.log.warn(data.conn.error)

    db.upsert_ignore_host(dest)
