import cv2
import time
import numpy as np
from scipy import stats

from library.Image import Image

class Video:
    def __init__(self, frames = [], fps=20):
        self.__callbacks = {}
        self.fps = fps
        self.playFps = 0
        self.calculation = 0
        if isinstance(frames, list): self.frames = [ Image(f) for f in frames ]
        elif isinstance(frames, tuple) or isinstance(frames, list): self.frames = [ Image(frame) for frame in frames ]
        elif isinstance(frames, str): self.load(frames)
        else: self.frames = []

    def __repr__(self): return str(self)
    def __str__(self): return 'Video<{},{}>'.format(self.length, self.channels)

    def __getitem__(self, index):
        if isinstance(index, int): return self.frames[i]
        return Video([ f.copy() for f in self.frames[index]], self.fps)
    def __setitem__(self, index, value): self.frames[index] = value

    def __len__(self): return len(self.frames)
    
    def __iter__(self):
        for frame in self.frames: yield frame
    
    def __call(self, function, *args):
        function = self.__callbacks.get(function)
        return None if function is None else function(self, *args)
    
    def load(self, path):
        cap = cv2.VideoCapture(path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frames = []
        try:
            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret and not frame is None: self.frames.append(Image(frame))
                else: break
        finally: cap.release()
        return self


    def save(self, path, fps=None):
        if self.valid:
            if fps is None: fps = self.fps
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(path, fourcc, fps, self.dimensions, self.colors)
            for frame in self.frames: out.write(frame.asByte().data)
            out.release()
        return self

    def median(self):
        median = np.stack(self.frames, axis=0)
        median = np.median(median, axis=0).astype(np.uint8)
        return Image(median)

    def mean(self):
        mean = np.stack(self.frames, axis=0)
        mean = np.mean(mean, axis=0).astype(np.uint8)
        return Image(mean)

    def max(self):
        max = np.stack(self.frames, axis=0)
        max = np.max(max, axis=0).astype(np.uint8)
        return Image(max)

    def min(self):
        min = np.stack(self.frames, axis=0)
        min = np.min(min, axis=0).astype(np.uint8)
        return Image(min)

    def mode(self):
        mode = np.stack(self.frames, axis=0)
        mode = stats.mode(mode, axis=0)[0][0]
        return Image(mode)

    
    def play(self, loop=True, name='Video Frame'):
        dataLoop = [True]
        def __exit__(): dataLoop[0] = False
        def __mouse__(e, x, y, f, p): self.__call('mouse', x, y, __exit__)
        cv2.namedWindow(name)
        cv2.setMouseCallback(name, __mouse__)
        lastException = None
        while dataLoop[0]:
            i = 0
            while i < self.length:
                frame = self.frames[i]
                now = time.clock()
                key = cv2.waitKey(1)
                if key == 27: dataLoop[0] = False
                elif key != -1:
                    self.__call('key#' + str(key), key, __exit__)
                    self.__call('keys', key, __exit__)
                if not dataLoop[0]: break
                rendered = frame.copy()
                if 'elaborate' in self.__callbacks:
                    try:
                        tmp = self.__call('elaborate', rendered, i, __exit__)
                        rendered = Image(tmp) if tmp is not None else rendered
                        printedException = False
                    except Exception as ex:
                        exMessage = str(ex)
                        if exMessage != lastException: print('video callback:', exMessage)
                        lastException = exMessage
                        rentered = frame
                cv2.imshow(name, rendered.asByte().data)
                self.calculation = time.clock() - now
                sleepAmmount = (1.0 / self.fps - self.calculation) if self.fps > 0 else 0
                if self.fps < 240 and sleepAmmount > 0: time.sleep(sleepAmmount)
                self.playFps = 1.0 / (time.clock() - now + 0.0001)
                if 'index' in self.__callbacks: i = self.__call('index', i, __exit__)
                else: i += 1
                if i < 0: i = self.length + i
            dataLoop[0] = dataLoop[0] and loop
        cv2.destroyWindow(name)
        return self

    def on(self, evt, callback):
        self.__callbacks[evt] = callback
        return self
    def onKey(self, key, callback): return self.on('key#' + (str(ord(key[0])) if isinstance(key, str) else str(key)), callback)
    def onKeys(self, callback): return self.on('keys', callback)
    def onMouse(self, callback): return self.on('mouse', callback)
    def onElaboration(self, callback): return self.on('elaborate', callback)
    def onFrame(self, callback): return self.on('index', callback)

    def BGR2RGB(self): return Video([frame.BGR2RGB() for frame in self.frames], self.fps)
    def RGB2BGR(self): return Video([frame.RGB2BGR() for frame in self.frames], self.fps)
    def BGR2Gray(self): return Video([frame.BGR2Gray() for frame in self.frames], self.fps)
    def RGB2Gray(self): return Video([frame.RGB2Gray() for frame in self.frames], self.fps)


    def copy(self): return Video([ f.copy() for f in self.frames], self.fps)

    @staticmethod
    def closeAll(): cv2.destroyAllWindows()

    @property
    def valid(self): return self.length > 0
    @property
    def length(self): return len(self.frames)
    @property
    def colors(self): return self.valid and self.frames[0].channels > 1
    @property
    def gray(self): return not self.colors
    @property
    def width(self): return self.frames[0].width if self.valid else 0
    @property
    def height(self): return self.frames[0].height if self.valid else 0
    @property
    def dimensions(self): return (self.width, self.height)
    @property
    def shape(self): return self.frames[0].shape if self.valid else (0, 0, 0)
    @property
    def channels(self): return self.frames[0].channels if self.valid else 0