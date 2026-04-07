#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#

from .request import Request
from .response import Response
from .dictionary import CaseInsensitiveDict

import asyncio
import inspect

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.
    """

    __attrs__ = [
        "ip", "port", "conn", "connaddr", "routes", "request", "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        self.ip = ip
        self.port = port
        self.conn = conn
        self.connaddr = connaddr
        self.routes = routes
        self.request = Request()
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Xử lý kết nối từ client (Synchronous/Threads).
        """
        self.conn = conn        
        self.connaddr = addr
        req = self.request
        resp = self.response

        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                conn.close()
                return
                
            msg = raw_data.decode('utf-8')
            req.prepare(msg, routes)
            print("[HttpAdapter] Invoke handle_client connection {}".format(addr))

            response_content = b""
            if req.hook:
                # Xử lý nếu hàm hook là async (dành cho SampleApp)
                if inspect.iscoroutinefunction(req.hook):
                    result = asyncio.run(req.hook(req.headers, req._raw_body))
                else:
                    result = req.hook(req.headers, req._raw_body)
                
                response_content = resp.build_response(req, envelop_content=result)
            else:
                response_content = resp.build_notfound()

            conn.sendall(response_content)
            
        except Exception as e:
            print("[HttpAdapter] Lỗi xử lý client {}: {}".format(addr, e))
            conn.sendall(resp.build_notfound())
        finally:
            conn.close()

    async def handle_client_coroutine(self, reader, writer):
        """
        Xử lý kết nối client bất đồng bộ (Asynchronous).
        """
        req = self.request
        resp = self.response
        addr = writer.get_extra_info("peername")
        print("[HttpAdapter] Invoke handle_client_coroutine connection {}".format(addr))

        msg = await reader.read(1024)
        # Nạp lại routes của instance thay vì truyền {}
        req.prepare(msg.decode("utf-8"), routes=self.routes)

        response_content = b""
        if req.hook:
            if inspect.iscoroutinefunction(req.hook):
                result = await req.hook(req.headers, req._raw_body)
            else:
                result = req.hook(req.headers, req._raw_body)
            
            response_content = resp.build_response(req, envelop_content=result)
        else:
            response_content = resp.build_notfound()

        writer.write(response_content)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    def build_response(self, req, resp_obj):
        """Builds a :class:`Response <Response>` object."""
        response = Response()
        response.request = req
        response.connection = self
        return response

    def build_notfound(self):
        return self.response.build_notfound()