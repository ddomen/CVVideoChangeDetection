def applyBlobsMask(masked, blobs):
    for blob in blobs: masked = blob.drawMapContour(masked)
    return masked

pipe = [
    lambda m: applyBlobsMask(m, blobs)      # apply the blob contour mask to the original frame
]