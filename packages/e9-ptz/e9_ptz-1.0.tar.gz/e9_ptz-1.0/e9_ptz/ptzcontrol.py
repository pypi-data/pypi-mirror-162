from time import sleep
from gevent.pywsgi import WSGIServer

from onvif import ONVIFCamera
import zeep
import sys

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})


def move_up(ptz, request, timeout=0.2):
    print('move up...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMAX
    perform_move(ptz, request, timeout)


def move_down(ptz, request, timeout=0.2):
    print('move down...')
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = YMIN
    perform_move(ptz, request, timeout)


def move_right(ptz, request, timeout=0.2):
    print('move right...')
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)


def move_left(ptz, request, timeout=0.2):
    print('move left...')
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)


def move_upleft(ptz, request, timeout=0.2):
    print('move up left...')
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMAX
    perform_move(ptz, request, timeout)

def move_upright(ptz, request, timeout=0.2):
    print('move up left...')
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMAX
    perform_move(ptz, request, timeout)

def move_downleft(ptz, request, timeout=0.2):
    print ('move down left...')
    request.Velocity.PanTilt.x = XMIN
    request.Velocity.PanTilt.y = YMIN
    perform_move(ptz, request, timeout)

def move_downright(ptz, request, timeout=0.2):
    print ('move down left...')
    request.Velocity.PanTilt.x = XMAX
    request.Velocity.PanTilt.y = YMIN
    perform_move(ptz, request, timeout)


def zoom_up(ptz,request,timeout=0.5):
    print('zoom up')
    request.Velocity.Zoom.x = 1
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    perform_move(ptz,request,timeout)


def zoom_down(ptz,request,timeout=0.5):
    print('zoom down')
    request.Velocity.Zoom.x = -1
    request.Velocity.PanTilt.x = 0
    request.Velocity.PanTilt.y = 0
    perform_move(ptz, request, timeout)
