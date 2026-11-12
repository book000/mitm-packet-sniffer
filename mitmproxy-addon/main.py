import asyncio
import atexit
import base64
import datetime
import hashlib
import json
import os
from xml.etree import ElementTree

import aiomysql
from mitmproxy import ctx, http, tls
from mitmproxy.utils import human


class Database:
    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT'] if 'DB_PORT' in os.environ else 3306,
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            db=os.environ['DB_NAME'],
            autocommit=True
        )

        if self.pool is None:
            raise Exception('Failed to connect to database')

    def is_connected(self):
        return self.pool is not None

    async def insert_response(self, flow: http.HTTPFlow):
        sql = "INSERT INTO `responses` (`host`, `port`, `method`, `scheme`, `authority`, `path`, `path_hash`, `query`, `request_content`, `request_content_type`, `http_version`, `request_headers`, `status_code`, `response_headers`, `response_content`, `response_content_type`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        host = flow.request.host
        port = flow.request.port
        method = flow.request.method
        scheme = flow.request.scheme
        authority = flow.request.authority
        # flow.request.path includes the query string, so strip it to keep the path only
        path = flow.request.path
        if '?' in path:
            path = path[:path.index('?')]
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

        await self.execute(sql, (host, port, method, scheme, authority, path, path_hash, query, request_content, request_content_type, http_version, request_headers, status_code, response_headers, content, content_type))

    async def is_ignore_hosts(self, address: str):
        sql = "SELECT UNIX_TIMESTAMP(`last_seen_at`), `next_check_phase`, UNIX_TIMESTAMP() FROM `ignore_hosts` WHERE `address` = %s"
        row = await self.fetchone(sql, (address,))

        # No record: the host is not ignored
        if row is None:
            return False

        # Record exists: the host stays ignored until is_next_check says its re-check time has come
        return not self.is_next_check(row[0], row[1], row[2])

    async def upsert_ignore_host(self, address: str):
        sql = "INSERT INTO `ignore_hosts` (`address`, `last_seen_at`) VALUES (%s, NOW()) ON DUPLICATE KEY UPDATE `last_seen_at` = NOW(), `next_check_phase` = `next_check_phase` + 1"
        await self.execute(sql, (address,))

    async def delete_ignore_host(self, address: str):
        sql = "DELETE FROM `ignore_hosts` WHERE `address` = %s"

        try:
            await self.execute(sql, (address,))
        except:
          pass

    async def execute(self, sql: str, params: tuple):
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)

    async def fetchone(self, sql: str, params: tuple):
        if self.pool is None:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                return await cur.fetchone()

    def is_next_check(self, last_seen_at: int, next_check_phase: int, now: int) -> bool:
        """Return True when the re-check interval for next_check_phase has elapsed.

        last_seen_at and now are epoch seconds read from MySQL in the same query,
        so the result does not depend on any time zone or on the container clock.
        """
        # Re-check interval per next_check_phase (1 = 1 minute ... 9 = 48 hours).
        # Phases beyond 9 never expire, so the host stays ignored indefinitely.
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

        next_check_at = last_seen_at + timedeltas[next_check_phase].total_seconds()

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
        self.pool.close()

class Addon:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.db = Database()

    async def running(self):
        await self.db.connect()

        atexit.register(self.done)

    def done(self):
        if self.db is None or not self.db.is_connected():
            return
        self.db.close()

    async def response(self, flow: http.HTTPFlow):
        self.loop.create_task(self.db.insert_response(flow))

    async def tls_clienthello(self, data: tls.ClientHelloData):
        if data.client_hello.sni:
            dest = data.client_hello.sni
        else:
            dest = human.format_address(data.context.server.address)

        if await self.db.is_ignore_hosts(dest):
            data.ignore_connection = True

    async def tls_established_client(self, data: tls.TlsData):
        if data.conn.sni:
            dest = data.conn.sni
        else:
            dest = human.format_address(data.context.server.address)

        self.loop.create_task(self.db.upsert_ignore_host(dest))

    async def tls_failed_client(self, data: tls.TlsData):
        if data.conn.sni:
            dest = data.conn.sni
        else:
            dest = human.format_address(data.context.server.address)

        ctx.log.warn(data.conn.error)

        self.loop.create_task(self.db.delete_ignore_host(dest))

addons = [Addon()]