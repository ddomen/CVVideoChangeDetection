import numpy as np
import cv2

def distance(dx, dy): return dx*dx + dy*dy

def overlap(R1, R2): return not(R1[2] < R2[0] or R1[0] > R2[2] or R1[3] < R2[1] or R1[1] > R2[3])

def overlapArea(R1, R2):
    area1 = abs(R1[0] - R1[2]) * abs(R1[1] - R1[3])
    area2 = abs(R2[0] - R2[2]) * abs(R2[1] - R2[3])
    areaI = (min(R1[2], R2[2]) - max(R1[0], R2[0])) * (min(R1[3], R2[3]) - max(R1[1], R2[1]))
    return area1 + area2 - areaI

class Blob:
    COLORS = (
        (100,100,255),
        (100,255,100),
        (255,100,100),
        (255,255,100),
        (255,100,255),
        (100,255,255),
        (100,100,100),
    )

    MAPPED_COLORS = {
        'person': (255,100,100),
        'true object': (100,255,100),
        'false object': (100,100,255),
        0: (255,100,100),
        1: (100,255,100),
        2: (100,100,255)
    }

    CSV_PROPERTIES = [
        'blob_id',
        'blob_classification',
        'blob_classification_color',
        'blob_motion_index',
        'blob_positive_index',
        'blob_contour_std_deviation',
        'blob_centerX',
        'blob_centerY',
        'blob_speedX',
        'blob_speedY',
        'blob_minX',
        'blob_minY',
        'blob_maxX',
        'blob_maxY',
        'blob_area',
        'blob_perimeter',
        'blob_convex_hull_area',
        'blob_convex_hull_perimeter',
        'blob_aspect_ratio',
        'blob_extent_ratio',
        'blob_solidity_ratio',
        'blob_diameter',
        'blob_compactness',
        'blob_major_axis_rotation',
        'blob_minor_axis_rotation',
        'blob_rotation'
    ]

    def __init__(self, contours):
        # blob image properties
        self.stackedContours = np.vstack(contours)
        self.contours = contours
        self.moment = cv2.moments(self.stackedContours)
        self.centerX = self.moment['m10'] / (self.moment['m00'] + .01) # preventing 0 division
        self.centerY = self.moment['m01'] / (self.moment['m00'] + .01) # preventing 0 division
        self.area = np.sum((cv2.contourArea(c) for c in self.contours))
        self.perimeter = np.sum((cv2.arcLength(c, True) for c in self.contours))
        self.minX, self.minY, self.width, self.height = cv2.boundingRect(self.stackedContours)
        self.rectArea = self.width * self.height
        self.maxX = self.minX + self.width
        self.maxY = self.minY + self.height
        self.minRect = [cv2.boxPoints(cv2.minAreaRect(self.stackedContours))]
        # blob classification properties
        self.id = 0
        self.speedX = 0
        self.speedY = 0
        self.classification_index = 0
        self.classification_positive = 0
        self.stdDev = 0.0
        # blob shape properties
        self.hull = cv2.convexHull(self.stackedContours)
        self.hullArea = cv2.contourArea(self.hull)
        self.hullPerimeter = cv2.arcLength(self.hull, True)
        self.aspect = float(self.width) / self.height
        self.extent = float(self.area) / self.rectArea
        self.solidity = float(self.area) / self.hullArea
        self.diameter = np.sqrt(4.0 * self.area / np.pi)
        self.compactness = float(self.perimeter * self.perimeter) / self.area
        if self.stackedContours.shape[0] > 4:
            (_, _), (self.majorAxis, self.minorAxis), self.angle = cv2.fitEllipse(self.stackedContours)
        else:
            self.majorAxis = 0
            self.minorAxis = 0
            self.angle = 0


    def drawContour(self, image, color=None, thickness=1):
        image = image.copy()
        cv2.drawContours(image.data, self.contours, -1, self.color if color is None else color, thickness)
        return image
    def drawMapContour(self, image, thickness=1): return self.drawContour(image, self.mappedColor, thickness)
    
    def fillContour(self, image, color=None): return self.drawContour(image, self.color if color is None else color, -1)
    def fillMapContour(self, image): return self.fillContour(image, self.mappedColor)

    def drawRect(self, image, color=None, thickness=1): return image.rect((self.minX, self.minY), (self.maxX, self.maxY), self.color if color is None else color, thickness)
    def drawMapRect(self, image, thickness=1): return self.drawRect(image, self.mappedColor, thickness)

    def drawInfo(self, image, minimalDistance, color=(255,255,255), thickness=1):
        minRect = self.minimalRectangle(minimalDistance)
        image = image.text(str(self.id), (int(self.centerX + 5), int(self.centerY + 5)), color=color, fontSize=thickness/2)
        image = image.text(str(self.classification[0]), (int(self.centerX + 5), int(self.centerY + 15)), color=color, fontSize=thickness)
        image = image.text(str(self.classification_index), (int(self.centerX - 5), int(self.centerY + 15)), color=color, fontSize=thickness/3)
        image = image.text(str(self.classification_positive), (int(self.centerX - 15), int(self.centerY + 15)), color=color, fontSize=thickness/3)
        image = image.text('a:{0:.2f}'.format(self.area), (int(self.centerX - 5), int(self.centerY - 5)), color=color, fontSize=thickness/2)
        image = image.text('p:{0:.2f}'.format(self.perimeter), (int(self.centerX - 5), int(self.centerY - 15)), color=color, fontSize=thickness/2)
        image = image.text('s:{0:.2f}'.format(distance(self.speedX, self.speedY)), (int(self.centerX - 5), int(self.centerY - 22)), color=color, fontSize=thickness/2)
        image = image.text('r:{0:.2f}'.format(self.aspect), (int(self.centerX + 5), int(self.centerY + 25)), color=color, fontSize=thickness/2)
        image = image.text('e:{0:.2f}'.format(self.extent), (int(self.centerX + 5), int(self.centerY + 33)), color=color, fontSize=thickness/2)
        image = image.text('s:{0:.2f}'.format(self.solidity), (int(self.centerX + 5), int(self.centerY + 41)), color=color, fontSize=thickness/2)
        image = image.text('d:{0:.2f}'.format(self.diameter), (int(self.centerX + 5), int(self.centerY + 49)), color=color, fontSize=thickness/2)
        image = image.line((int(self.centerX), int(self.centerY)), (int(round(self.centerX - self.speedX)), int(round(self.centerY - self.speedY))), color, thickness * 2)
        return image.rect(minRect[0:2], minRect[2:4], color, thickness)

    def deviation(self, image):
        mask = self.drawContour(image.blankCopy(), 255, 1)
        return np.std(image[mask != 0])

    def distance(self, blob): return (self.centerX - blob.centerX) ** 2 + (self.centerY - blob.centerY) ** 2

    def minimalDistance(self, blob, minDistance): return overlap(self.minimalRectangle(minDistance), blob.minimalRectangle(minDistance))
    def overlap(self, blob): return self.minimalDistance(blob, 0)

    def minimalOverlapArea(self, blob, minDistance): return overlapArea(self.minimalRectangle(minDistance), blob.minimalRectangle(minDistance))
    def overlapArea(self, blob): return self.minimalOverlapArea(blob, 0)

    
    def minimalRectangle(self, minDistance): return (self.minX - minDistance, self.minY - minDistance, self.maxX + minDistance, self.maxY + minDistance)

    def calculateSpeed(self, oldBlob):
        self.speedX = self.centerX - oldBlob.centerX
        self.speedY = self.centerY - oldBlob.centerY
        return self

    def classify(self, maxDeviation=15, speedThreshold=10):
        self.classification_index += (1 if distance(self.speedX, self.speedY) > speedThreshold else -2)
        self.classification_positive += (1 if self.stdDev > maxDeviation else -2)
        return self
    
    def similar(self, blob, overlapArea=None, perimeter=None, aspect=None, extent=None, solidity=None, diameter=None, mustOverlap=True):
        overlap = self.overlap(blob)
        overlapArea = overlapArea is None or self.overlapArea(blob) >= overlapArea
        perimeter = perimeter is None or abs(self.perimeter - blob.perimeter) <= perimeter
        aspect = aspect is None or abs(self.aspect - blob.aspect) <= aspect
        extent = extent is None or abs(self.extent - blob.extent) <= extent
        solidity = solidity is None or abs(self.solidity - blob.solidity) <= solidity
        diameter = diameter is None or abs(self.diameter - blob.diameter) <= diameter
        parameters = overlapArea and perimeter and aspect and extent and solidity and diameter
        return (overlap and parameters) if mustOverlap else (overlap or parameters)

    def assume(self, blob):
        self.id = blob.id
        self.classification_index = blob.classification_index
        self.classification_positive = blob.classification_positive
        self.calculateSpeed(blob)
        return self

    def toCSV(self, sep=';', dot=','):
        props = [ str(p).replace('.', dot) for p in [
            self.id, self.classification, self.mappedColorString,
            self.classification_index, self.classification_positive, self.stdDev,
            self.centerX, self.centerY, self.speedX, self.speedY,
            self.minX, self.minY, self.maxX, self.maxY,
            self.area, self.perimeter, self.hullArea, self.hullPerimeter,
            self.aspect, self.extent, self.solidity, self.diameter, self.compactness,
            self.majorAxis, self.minorAxis, self.angle
        ]]
        return sep.join(props)

    def join(self, blob): return Blob([*self.contours, *blob.contours])

    @property
    def classification(self): return 'person' if self.classification_index > 0 else self.objectClassification
    @property
    def objectClassification(self): return '{} object'.format(self.classification_positive > 0).lower()
    @property
    def mappedColor(self): return Blob.MAPPED_COLORS[self.classification]
    @property
    def color(self): return Blob.COLORS[self.id]
    @property
    def mappedColorString(self): return 'blue' if self.classification_index > 0 else ('green' if self.classification_positive > 0 else 'red') 

    @property
    def rectangle(self): return self.minimalRectangle(0)

