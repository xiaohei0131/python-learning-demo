import asyncio
import threading

import cv2
from aiohttp import web


async def index(request):
    await asyncio.sleep(0.5)
    return web.Response(body=b'<img  src="http://localhost:8000/video/12" />', content_type='text/html',
                        charset='utf-8')


async def hello(request):
    await asyncio.sleep(5)
    text = '<h1>Hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'), content_type='application/json', charset='utf-8')


async def video(request):
    cameraId = request.match_info['cameraId']
    print(cameraId)
    url = 'rtsp://10.1.203.220/stream/'
    resp = web.StreamResponse(headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"})
    resp.enable_chunked_encoding()
    resp.enable_compression()

    await resp.prepare(request)
    await getFrame(url, resp)
    return resp


async def getFrame(url, resp):
    tmp = 0
    cap = cv2.VideoCapture(url)
    while cap.isOpened():
        ret, frame = cap.read()
        print(ret)
        tmp += 1
        if ret and tmp % 2 == 0:
            img_str = cv2.imencode('.jpg', frame)[1].tostring()
            await resp.write(b'--frame\r\n'
                             b'Content-Type:image/jpeg\r\n\r\n'
                             + img_str +
                             b'\r\n')


async def init():
    app = web.Application()
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    app.router.add_route('GET', '/video/{cameraId}', video)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
    return site


loop = asyncio.get_event_loop()
loop.run_until_complete(init())
loop.run_forever()
