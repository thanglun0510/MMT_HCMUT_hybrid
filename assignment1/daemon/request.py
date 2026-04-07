#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#

"""
daemon.request
~~~~~~~~~~~~~~~~~

This module provides a Request object to manage and persist 
request settings (cookies, auth, proxies).
"""
from .dictionary import CaseInsensitiveDict

class Request():
    """The fully mutable "class" `Request <Request>` object."""
    __attrs__ = [
        "method", "url", "headers", "body", "_raw_headers", 
        "_raw_body", "reason", "cookies", "routes", "hook",
    ]

    def __init__(self):
        self.method = None
        self.url = None
        self.headers = CaseInsensitiveDict() # Khởi tạo dictionary trống thay vì None
        self.path = None        
        self.cookies = None
        self.body = None
        self._raw_headers = None
        self._raw_body = None
        self.routes = {}
        self.hook = None

    def extract_request_line(self, request):
        try:
            lines = request.splitlines()
            if not lines: return None, None, None
            first_line = lines[0]
            parts = first_line.split()
            if len(parts) < 3: return None, None, None
            
            method, path, version = parts
            if path == '/':
                path = '/index.html'
            return method, path, version
        except Exception:
            return None, None, None
             
    def prepare_headers(self, request):
        """Prepares the given HTTP headers."""
        lines = request.split('\r\n')
        headers = CaseInsensitiveDict()
        for line in lines[1:]:
            if ': ' in line:
                key, val = line.split(': ', 1)
                headers[key.strip()] = val.strip()
        return headers

    def fetch_headers_body(self, request):
        """Splits request into header and body sections."""
        parts = request.split("\r\n\r\n", 1)
        _headers = parts[0]
        _body = parts[1] if len(parts) > 1 else ""
        return _headers, _body

    def prepare(self, request, routes=None):
        """Prepares the entire request with the given parameters."""
        
        # 1. Phân tách Header và Body thô
        self._raw_headers, self._raw_body = self.fetch_headers_body(request)
        
        # 2. Quan trọng: Phải phân tích Header trước khi truy cập cookie
        self.headers = self.prepare_headers(self._raw_headers)

        # 3. Trích xuất dòng trạng thái
        self.method, self.path, self.version = self.extract_request_line(request)
        
        print(f"[Request] {self.method} path {self.path} version {self.version}")

        # 4. Xử lý Routing và Hook
        if routes:
            self.routes = routes
            self.hook = routes.get((self.method, self.path))
            if self.hook:
                print(f"[Request] Hook found for {self.method} {self.path}")

        # 5. Truy cập cookie (Bây giờ self.headers đã được khởi tạo, không còn lỗi NoneType)
        self.cookies = self.headers.get('cookie', '')
        
        return

    def prepare_body(self, data, files, json=None):
        if data:
            self.body = data
        return

    def prepare_content_length(self, body):
        if body:
            self.headers["Content-Length"] = str(len(body))
        else:
            self.headers["Content-Length"] = "0"
        return

    def prepare_auth(self, auth, url=""):
        return

    def prepare_cookies(self, cookies):
        self.headers["Cookie"] = cookies