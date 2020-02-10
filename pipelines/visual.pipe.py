def drawBlobsInfo(frame, blobs):
    frame = frame.copy()
    for blob in blobs:
        frame = blob.drawMapRect(frame)
        frame = blob.drawInfo(frame, minBlobDistance)
    return frame

pipe = [
    lambda f: drawBlobsInfo(f, blobs) if data.showRects else f,         # display blobs info
    lambda f: f.resize(f.width * data.scale, f.height * data.scale),    # resize image to a pleasant scale
    lambda f, o, i: data.display(f, i),                                 # display change detection parameters on the fly
]