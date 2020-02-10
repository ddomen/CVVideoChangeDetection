# classification parameters
speedThreshold = 5
minBlobDistance = 8
maxDeviation = 15

# similarity parameters
mustOverlap = True      # a blob must overlap the blob on the previous frame to be the same
maxPerimeterDiff = None # perimeter varies too much to be considered
maxDiameterDiff = None  # diameter varies too much to be considered
minOverlapArea = 15
maxAspectDiff = 1.9
maxExtentDiff = 0.25
maxSolidityDiff = 0.20

def drawBlobs(frame, blobs):
    original = frame.copy()
    frame = frame.blankCopy().Gray2RGB()
    for blob in blobs: frame = blob.fillMapContour(frame)
    return frame

def extractBlobs(frame, original, blobs):
    lastFrameBlobs = blobs[::]
    blobs.clear()
    blobs.extend(frame.extractBlobs(minDistance=minBlobDistance))
    data.nblobs = len(blobs)
    blobs.sort(key=lambda b: b.area, reverse=True)
    
    for b1 in lastFrameBlobs:
        for b2 in blobs:
            if b1.similar(b2, overlapArea=minOverlapArea, perimeter=maxPerimeterDiff, aspect=maxAspectDiff, extent=maxExtentDiff, solidity=maxSolidityDiff, diameter=maxDiameterDiff, mustOverlap=mustOverlap):
                b2.assume(b1)
                break
        
    blobs.sort(key=lambda b: b.id)
    for i in range(len(blobs)):
        blob = blobs[i]
        if data.playing:
            blob.stdDev = blob.deviation(original)
            blob.classify(maxDeviation, speedThreshold)
        blob.id = i
    return frame

pipe = [
    lambda f, c, o: extractBlobs(f, o, blobs),      # extracting blobs from the mask and look for similarities for cross frame blob recognition
    lambda f: drawBlobs(f, blobs)                   # draw blobs in the frame
]