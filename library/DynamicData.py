import cv2
import numpy as np

class DynamicData:
    def __init__(self):
        self.__ratios = [1,2,5,10,100]
        self.__ratio = 0
        self.scale = 2.5
        self.x = 0
        self.y = 0
        self.calculation = 0
        self.realFps = 0
        self.frame = None
        self.visualize = True
        self.hue = (0,)
        self.nblobs = 0

        self.__color = (255,255,255)
        self.__font = cv2.FONT_HERSHEY_PLAIN
        self.__fontSize = 1
        self.__lineSpace = 12
        self.__line = 1
        self.__lastSpeed = 0

        self.reset()

    @property
    def ratio(self): return self.__ratios[self.__ratio]

    def clamp(self, val, vmin, vmax): return min(max(val, vmin), vmax)
    
    def add_ratio(self, sign):
        sign = np.sign(sign)
        self.__ratio += sign
        self.__ratio = self.clamp(self.__ratio, 0, len(self.__ratios))
    
    def add_speed(self, value, mul):
        if mul:
            self.speed = int(self.clamp(self.speed * value, -240, 240))
            self.__lastSpeed = int(self.clamp(self.__lastSpeed * value, -240, 240))
        else:
            self.speed = int(self.clamp(self.speed + (value * np.sign(self.speed)), -240, 240))
    def pause(self):
        if self.speed != 0:
            self.__lastSpeed = self.speed
            self.speed = 0
        else:
            self.speed = self.__lastSpeed if self.__lastSpeed != 0 else 20
            self.__lastSpeed = 0
    
    def add_scale(self, value): self.scale = self.clamp(self.scale + value, 1, 5)
    def add_threshold(self, value): self.threshold = self.clamp(self.threshold + value * self.ratio, 0, 255)
    def toggle_background(self): self.background = not self.background
    def toggle_filter(self): self.filter = not self.filter
    def toggle_changes(self): self.changes = not self.changes
    def toggle_visualization(self): self.visualize = not self.visualize
    def toggle_rects(self): self.showRects = not self.showRects
    def toggle_blobs(self): self.blobs = not self.blobs
    def toggle_render(self): self.render = not self.render

    def reset(self):
        self.threshold = 40
        self.filter = True
        self.changes = True
        self.background = True
        self.blobs = True
        self.showRects = False
        self.visualize = True
        self.render = False
        self.speed = 20
        self.__ratio = 0
        return self

    def visual(self):
        return self.reset()

    def noVisual(self):
        self.reset()
        self.speed = 20
        self.render = False
        self.visualize = False
        return self

    
    def OnMouseMove(self, video, x, y, exit):
        self.x = int(x / self.scale)
        self.y = int(y / self.scale)
        if self.frame is not None:
            h = self.frame[y, x]
            if isinstance(h, int) or isinstance(h, float) or np.isscalar(h): self.hue = (h, )
            else: self.hue = tuple(h)
        else: self.hue = (0,)

    
    def __displayLine(self, text, frame):
        frame = frame.text(text, (0, self.__line * self.__lineSpace), self.__font, self.__fontSize, self.__color, 1)
        self.__line += 1
        return frame

    def display(self, frame, nframe):
        self.frame = frame
        if self.visualize:
            self.__line = 1
            frame = self.__displayLine('ACT:{}'.format(self.filter), frame)
            frame = self.__displayLine('f:{}'.format(nframe), frame)
            frame = self.__displayLine('fps:{}'.format(self.speed if abs(self.speed) < 240 else 'MAX'), frame)
            frame = self.__displayLine('rfps:{0:.1f}'.format(self.realFps), frame)
            frame = self.__displayLine('calc:{0:.2f}'.format(self.calculation*1000), frame)
            frame = self.__displayLine('WxH:{0:.1f}'.format(self.scale), frame)
            frame = self.__displayLine('hue:{}'.format(self.hue), frame)
            frame = self.__displayLine('x:{}'.format(self.x), frame)
            frame = self.__displayLine('y:{}'.format(self.y), frame)
            frame = self.__displayLine('nBLB:{}'.format(self.nblobs), frame)
            if self.filter:
                frame = self.__displayLine('th:{}'.format(self.threshold), frame)
                frame = self.__displayLine('BGS:{}'.format(self.background), frame)
                frame = self.__displayLine('CHG:{}'.format(self.changes), frame)
                frame = self.__displayLine('BLB:{}'.format(self.blobs), frame)
                frame = self.__displayLine('RCT:{}'.format(self.showRects), frame)
                frame = self.__displayLine('OVL:{}'.format(self.render), frame)
        return frame

    def applyTo(self, video):
        video.fps = abs(self.speed)
        self.calculation = video.calculation
        self.realFps = video.playFps
        return self

    @property
    def playing(self): return self.speed != 0
