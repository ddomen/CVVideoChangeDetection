import argparse
from library.Blob import Blob

def getProgramArgs():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', required=True, help='path to input video file', type=str)
    ap.add_argument('-o', '--output', required=False, default='output', help='path to output video file', type=str)
    ap.add_argument('-f', '--fps', required=False, default=None, help='output video frame per seconds', type=float)
    ap.add_argument('-b', '--bg-init', required=False, default=100, help='background initialization frames', type=int)
    ap.add_argument('-nv', '--no-visual', required=False, default=False, help='disable visual editor', action="store_true")
    ap.add_argument('-nl', '--no-loop', required=False, default=False, help='play video just once', action="store_true")
    return vars(ap.parse_args())

def saveBlobsCsv(path, csvData):
    csvData = [ data for data in csvData if data is not None ]
    outputCSV = open(path, 'w')
    outputCSV.write('frame;n_blobs;{}\n'.format(';'.join(Blob.CSV_PROPERTIES)))
    for i in range(len(csvData)):
        blobs = csvData[i]
        for blob in blobs: outputCSV.write('{};{};{}\n'.format(i, len(blobs), blob))
    outputCSV.close()