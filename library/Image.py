import cv2
import numpy as np

from library.Blob import Blob

np.seterr(divide='ignore', invalid='ignore')

sobel_kernel_x = np.array([ [-1,0,1], [-2,0,2], [-1,0,1]]) / 4 
sobel_kernel_y = np.array([ [-1,-2,-1], [0,0,0], [1,2,1]]) / 4

class Image:
    MORPH_BLACKHAT = cv2.MORPH_BLACKHAT
    MORPH_CLOSE = cv2.MORPH_CLOSE
    MORPH_CROSS = cv2.MORPH_CROSS
    MORPH_DILATE = cv2.MORPH_DILATE
    MORPH_ELLIPSE = cv2.MORPH_ELLIPSE
    MORPH_ERODE = cv2.MORPH_ERODE
    MORPH_GRADIENT = cv2.MORPH_GRADIENT
    MORPH_HITMISS = cv2.MORPH_HITMISS
    MORPH_OPEN = cv2.MORPH_OPEN
    MORPH_RECT = cv2.MORPH_RECT
    MORPH_TOPHAT = cv2.MORPH_TOPHAT
    MORPHES = {
        'black hat': cv2.MORPH_BLACKHAT,
        'close': cv2.MORPH_CLOSE,
        'cross': cv2.MORPH_CROSS,
        'dilate': cv2.MORPH_DILATE,
        'ellipse': cv2.MORPH_ELLIPSE,
        'erode': cv2.MORPH_ERODE,
        'gradient': cv2.MORPH_GRADIENT,
        'hitmiss': cv2.MORPH_HITMISS,
        'open': cv2.MORPH_OPEN,
        'rect': cv2.MORPH_RECT,
        'tophat': cv2.MORPH_TOPHAT,
        MORPH_BLACKHAT: cv2.MORPH_BLACKHAT,
        MORPH_CLOSE: cv2.MORPH_CLOSE,
        MORPH_CROSS: cv2.MORPH_CROSS,
        MORPH_DILATE: cv2.MORPH_DILATE,
        MORPH_ELLIPSE: cv2.MORPH_ELLIPSE,
        MORPH_ERODE: cv2.MORPH_ERODE,
        MORPH_GRADIENT: cv2.MORPH_GRADIENT,
        MORPH_HITMISS: cv2.MORPH_HITMISS,
        MORPH_OPEN: cv2.MORPH_OPEN,
        MORPH_RECT: cv2.MORPH_RECT,
        MORPH_TOPHAT: cv2.MORPH_TOPHAT
    }

    def __init__(self, data = []):
        if isinstance(data, Image): self.data = data.data.copy()
        elif isinstance(data, np.ndarray): self.data = np.abs(data)
        elif isinstance(data, tuple) or isinstance(data, list): self.data = np.abs(np.array(data))
        elif isinstance(data, str): self.load(data)
        else: self.data = np.array([])

    def __repr__(self): return str(self)
    def __str__(self): return 'Image[{}]<{}>'.format(self.channels, self.data)
    
    def __getitem__(self, index):
        if isinstance(index, Image): return Image(self.data[index.data])
        result = self.data[index]
        return Image(result) if isinstance(result, np.ndarray) else result
    def __setitem__(self, index, value): self.data[index] = value

    def __add__(self, other): return Image(self.data + other)
    def __sub__(self, other): return Image(self.data - other)
    def __mul__(self, other): return Image(self.data * other)
    def __truediv__(self, other): return Image(self.data / other)
    def __matmul__(self, other): return Image(self.data @ other)
    def __or__(self, other): return Image(self.data | other)
    def __and__(self, other): return Image(self.data & other)

    def __radd__(self, other): return Image(other + self.data)
    def __rsub__(self, other): return Image(other - self.data)
    def __rmul__(self, other): return Image(other * self.data)
    def __rtruediv__(self, other): return Image(other / self.data)
    def __rmatmul__(self, other): return Image(other @ self.data)
    def __ror__(self, other): return Image(other | self.data)
    def __rand__(self, other): return Image(other & self.data)

    def __lt__(self, other): return self.data < other
    def __le__(self, other): return self.data <= other
    def __ge__(self, other): return self.data >= other
    def __gt__(self, other): return self.data > other
    def __eq__(self, other): return self.data == other
    def __ne__(self, other): return self.data != other

    def __len__(self): return len(self.data)

    def __iter__(self):
            for data in self.data: yield data

    def load(self, path):
        self.data = cv2.imread(path)
        return self
    
    def save(self, path):
        cv2.imwrite(path, self.data)
        return self

    def kernel(self, kernel, shape=None):
        if isinstance(kernel, int): kernel = (kernel, kernel)
        if shape is not None: kernel = kernel = cv2.getStructuringElement(Image.MORPHES.get(shape, Image.MORPH_RECT), kernel)
        elif isinstance(kernel, tuple): kernel = np.ones(kernel, np.uint8)
        elif isinstance(kernel, list): kernel = np.array(kernel, np.uint8)
        return kernel

    def sobel(self):
        img = self.data.astype(float)
        dx = np.abs(cv2.filter2D(img,-1,sobel_kernel_x))
        dy = np.abs(cv2.filter2D(img,-1,sobel_kernel_y))
        sobel = np.maximum(dx,dy)
        return Image(sobel)

    def asType(self, selType): return Image(self.data.astype(selType));
    def asFloat(self): return self.asType(np.float32);
    def asInt(self): return self.asType(np.int32);
    def asByte(self): return self.asType(np.uint8);
    def toNormalizedByte(self): return self.normalize().asByte()

    def copy(self): return Image(self.data.copy())
    def blankCopy(self): return Image(np.zeros(self.data.shape, dtype=self.data.dtype))

    def invert(self): return 255 - self

    def extend(self, size=10, color=0, mode=cv2.BORDER_CONSTANT): return Image(cv2.copyMakeBorder(self.data, size, size, size, size, mode, value=color))
    def cut(self, x, y, w, h): return self[y:y+h, x:x+w]
    def implode(self, size=10): return self[size:-size, size:-size]

    def opening(self, kernel=5, iterations=1, shape=None): return Image(cv2.morphologyEx(self.data, cv2.MORPH_OPEN, self.kernel(kernel, shape), iterations=iterations))
    def closing(self, kernel=5, iterations=1, shape=None): return Image(cv2.morphologyEx(self.data, cv2.MORPH_CLOSE, self.kernel(kernel, shape), iterations=iterations))
    def erode(self, kernel=5, iterations=1, shape=None): return Image(cv2.erode(self.data, self.kernel(kernel, shape), iterations=iterations))
    def dilate(self, kernel=5, iterations=1, shape=None): return Image(cv2.dilate(self.data, self.kernel(kernel, shape), iterations=iterations))
    def ellipse(self, kernel=5, iterations=1, shape=None): return Image(cv2.morphologyEx(self.data, cv2.MORPH_ELLIPSE, self.kernel(kernel, shape), iterations=iterations))

    def threshold(self, threshold):
        img = self.copy()
        img[img < threshold] = 0
        return img
    
    def binarize(self): return self.binarySelection(0, 255)
    
    def binarySelection(self, selection=255, value=0):
        img = self.copy()
        img[img != selection] = value
        return img

    def gaussianFilter(self, dx=5, dy=None): return Image(cv2.GaussianBlur(self.data, (dx, dx if dy is None else dy), cv2.BORDER_DEFAULT))

    def bilateral(self, s=5, dx=75, dy=None): return Image(cv2.bilateralFilter(self.asFloat().data, s, dx, dx if dy is None else dx))

    def histogram(self): return cv2.calcHist([self.asByte().data], [0], None, [256], [0,256])

    def histogramEqualization(self): return Image(cv2.equalizeHist(self.data))

    def blend(self, image, alpha):
        result = self * (1 - alpha) + image * alpha
        return result

    def normalize(self, maximum=255): return (self / np.max(self)) * maximum

    def contrastStretch(self, vmin=None, vmax=None, maximum=255):
        img = self.copy()
        if vmax is None: vmax = np.max(self.data)
        if vmin is None: vmin = np.min(self.data)
        if vmax == vmin:
            img[img != 0] = maximum
            return img
        rvmax = max(vmax, vmin)
        rvmin = min(vmax, vmin)
        return ((img - rvmin) / (rvmax - rvmin)) * maximum

    def gammaContrast(self, gamma=2.2):
        return Image(np.pow(255, 1 - gamma) * (np.pow(self.data, gamma)))

    def otsu(self):
        ret, otsu = cv2.threshold(self.toNormalizedByte().data, 0, 255, cv2.THRESH_TOZERO + cv2.THRESH_OTSU)
        return Image(otsu)

    def text(self, text, position, font=cv2.FONT_HERSHEY_PLAIN, fontSize=1, color=(255,255,255), thickness=1):
        return Image(cv2.putText(self.data, text, tuple(position)[:2], font, fontSize, tuple(color)[:3], thickness))

    def rect(self, start, stop, color=(255,255,255), thickness=1):
        return Image(cv2.rectangle(self.data, tuple(start)[:2], tuple(stop)[:2], tuple(color)[:3], thickness))

    def line(self, start, stop, color=(255,255,255), thickness=1):
        return Image(cv2.line(self.data, tuple(start)[:2], tuple(stop)[:2], tuple(color)[:3], thickness))

    def contours(self, minArea=None):
        _, contours, hier = cv2.findContours(self.asByte().data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if minArea is not None: contours = [c for c in contours if cv2.contourArea(c) >= minArea]
        return contours

    def drawContours(self, contours=None, minArea=None, color=(255,255,255), thickness=1):
        if contours is None: contours = [self.contours(minArea)]
        if len(contours) > 0: return Image(cv2.drawContours(self.data, contours, -1, color, thickness))
        return self.copy()

    def fillContours(self, minArea=None, color=(255,255,255), contours=None, rects=False):
        img = self.copy()
        if contours is None: contours = img.contours(minArea)
        img = img.blankCopy()
        cv2.fillPoly(img.data, pts=contours, color=color)
        if rects:
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(img.data, (x,y), (x+w,y+h), color, 1, 1)
        return Image(img)

    def extractBlobs(self, minDistance=0, minArea=None, contours=None):
        if contours is None: contours = self.contours(minArea)
        blobs = [ Blob([c]) for c in contours if minArea is None or cv2.contourArea(c) >= minArea ]
        if minDistance >= 0 and len(blobs) > 0:
            i = 0
            while i < len(blobs):
                b1 = blobs[i]
                j = i+1
                while j < len(blobs):
                    b2 = blobs[j]
                    if (minDistance == 0 and b1.overlap(b2,)) or (minDistance > 0 and b1.minimalDistance(b2, minDistance)):
                        blobs[i] = b1.join(b2)
                        blobs.pop(j)
                        i -= 1
                        break
                    j += 1
                i += 1
        for i in range(len(blobs)): blobs[i].id = i
        return blobs

    def convexHull(self, minArea=None, color=(255,255,255), contours=None):
        img = self.copy()
        if contours is None: contours = img.contours(minArea)
        hull = []
        for i in range(len(contours)): hull.append(cv2.convexHull(contours[i], False))
        img = img.blankCopy()
        cv2.fillPoly(img.data, pts=hull, color=color)
        return Image(img)


    def mask(self, mask, value = 255):
        img = self.copy()
        img[mask] = value
        return img

    def display(self, name='Image Frame', blocking=False):
        cv2.imshow(name, self.data)
        if blocking:
            cv2.waitKey(0)
            cv2.destroyWindow(name)
        return self

    def resize(self, width, height): return Image(cv2.resize(self.data, (int(width), int(height))))
    
    def split(self):
        if self.channels <= 1: return self
        return [ Image(self.data[:,:,c]) for c in range(self.channels)]

    def BGR2RGB(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_BGR2RGB))
    def RGB2BGR(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_RGB2BGR))
    def BGR2Gray(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY))
    def RGB2Gray(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_RGB2GRAY))
    def Gray2RGB(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_GRAY2RGB))
    def Gray2BGR(self): return Image(cv2.cvtColor(self.data, cv2.COLOR_GRAY2BGR))


    @staticmethod
    def closeAll(): cv2.destroyAllWindows()

    @staticmethod
    def join(*channels): return Image(channels)

    @property
    def shape(self): return self.data.shape
    @property
    def width(self): return self.data.shape[1]
    @property
    def height(self): return self.data.shape[0]
    @property
    def channels(self): return self.data.shape[2] if self.data.ndim > 2 else 1
    @property
    def size(self): return self.data.shape[:2][::-1]