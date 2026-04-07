import datetime
import os
import mimetypes
from .dictionary import CaseInsensitiveDict

BASE_DIR = ""

class Response():   
    """The :class:`Response <Response>` object, which contains a
    server's response to an HTTP request.
    """

    __attrs__ = [
        "_content", "_header", "status_code", "headers", "url", 
        "encoding", "reason", "cookies", "elapsed", "request"
    ]

    def __init__(self, request=None):
        self._content = b""
        self._header = b""
        self._content_consumed = False
        self.status_code = 200
        self.headers = {}
        self.url = None
        self.encoding = "utf-8"
        self.reason = "OK"
        self.cookies = CaseInsensitiveDict()
        self.request = request

    def get_mime_type(self, path):
        try:
            mime_type, _ = mimetypes.guess_type(path)
        except Exception:
            return 'application/octet-stream'
        return mime_type or 'application/octet-stream'

    def prepare_content_type(self, mime_type='text/html'):
        base_dir = ""
        if not hasattr(self, "headers") or self.headers is None:
            self.headers = {}

        main_type, sub_type = mime_type.split('/', 1)
        if main_type == 'text':
            self.headers['Content-Type'] = 'text/{}'.format(sub_type)
            if sub_type in ['plain', 'css']:
                base_dir = BASE_DIR + "static/"
            elif sub_type == 'html':
                base_dir = BASE_DIR + "www/"
        elif main_type == 'image':
            base_dir = BASE_DIR + "static/"
            self.headers['Content-Type'] = 'image/{}'.format(sub_type)
        elif main_type == 'application':
            base_dir = BASE_DIR + "apps/"
            self.headers['Content-Type'] = 'application/{}'.format(sub_type)
        else:
            self.headers['Content-Type'] = mime_type
        
        return base_dir

    def build_content(self, path, base_dir):
        filepath = os.path.join(base_dir, path.lstrip('/'))
        try:
            with open(filepath, "rb") as f:
               content = f.read()
            return len(content), content
        except Exception as e:
            return -1, b""

    def build_response_header(self, request):
        """Constructs formatted HTTP response headers."""
        reqhdr = request.headers
        
        # Ensure Content-Length is set correctly based on _content
        self.headers["Content-Length"] = str(len(self._content))
        self.headers["Date"] = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.headers["Server"] = "AsynapRous/2026"

        # Build the status line
        status_line = "HTTP/1.1 {} {}\r\n".format(self.status_code, self.reason)
        
        # Build header lines
        header_lines = []
        for key, value in self.headers.items():
            header_lines.append("{}: {}".format(key, value))
        
        fmt_header = status_line + "\r\n".join(header_lines) + "\r\n\r\n"
        return fmt_header.encode('utf-8')

    def build_notfound(self):
        return (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "Connection: close\r\n"
            "\r\n"
            "404 Not Found"
        ).encode('utf-8')

    def build_response(self, request, envelop_content=None):
        """Builds full HTTP response bytes."""
        path = request.path
        mime_type = self.get_mime_type(path)

        # 1. Determine Content and Base Directory
        if envelop_content is not None:
            # Case: RESTful API response (e.g., Tracker list)
            self._content = envelop_content if isinstance(envelop_content, bytes) else str(envelop_content).encode('utf-8')
            self.prepare_content_type('application/json')
        else:
            # Case: Static file serving
            base_dir = self.prepare_content_type(mime_type)
            length, content = self.build_content(path, base_dir)
            if length == -1:
                return self.build_notfound()
            self._content = content

        # 2. Build the Header based on prepared content
        self._header = self.build_response_header(request)

        # 3. Combine Header and Content
        return self._header + self._content