import logging
import socketserver
import urllib
from http import server

import cv2

PAGE = """\
<html>
<head>
<title>streaming demo</title>
</head>
<body>
<h1>Streaming Demo</h1>
<img src="stream.mjpg?id=12" width="640" height="480" />
</body>
</html>
"""


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        mpath, margs = urllib.parse.splitquery(self.path)
        params = dict(urllib.parse.parse_qsl(margs))
        # o = urlparse.urlparse(self.path)
        if mpath == '/':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif mpath == '/stream.mjpg':
            print(params.get('id'))
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                tmp = 0
                url = 'rtsp://10.1.203.220/stream/'
                cap = cv2.VideoCapture(url)
                while cap.isOpened():
                    ret, frame = cap.read()
                    tmp += 1
                    if ret and tmp % 2 == 0:
                        tmp = 0
                        img_str = cv2.imencode('.jpg', frame)[1].tostring()
                        # 写入http响应
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.end_headers()

                        self.wfile.write(img_str)
                        self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'errror streaming client %s: %s',
                    self.client_address, str(e))

        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


try:
    address = ('127.0.0.1', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
except Exception as e:
    print(e)
