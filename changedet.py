import library.utils as utils
from library.Video import Video
from library.Image import Image
from library.DynamicData import DynamicData
from library.FilePipeline import FilePipeline

args = utils.getProgramArgs()

target_video = Video(args.get('input')).BGR2Gray()
saved_fps = args.get('fps')
if saved_fps is None: saved_fps = target_video.fps
start_n_frames = args.get('bg_init')
if start_n_frames is None: start_n_frames = 100
start_frames = target_video[:start_n_frames]
bg = start_frames.median().blend(start_frames.mean(), 0.5)
init_bg = bg.copy()
data = DynamicData()
blobs = []

pipe_context = { 'data': data, 'bg': bg, 'init_bg': init_bg, 'blobs': blobs }
# CHANGE DETECTION PIPELINE
change_detection_pipe = FilePipeline('pipelines/change.detection.pipe.py', pipe_context)
# RENDERING PIPELINE
visual_pipe = FilePipeline('pipelines/visual.pipe.py', pipe_context)
# MASK RENDERING PIPELINE
mask_pipe = FilePipeline('pipelines/mask.pipe.py', pipe_context)
# BACKGROUND SELECTIVE ADAPTATION PIPELINE
bg_pipe = FilePipeline('pipelines/background.pipe.py', pipe_context)
# BLOBS PIPELINE
blob_pipe = FilePipeline('pipelines/blobs.pipe.py', pipe_context)

outputFrames = [None] * target_video.length
csvData = [None] * target_video.length

if args.get('no_visual'):
    data.noVisual()

    print('elaborating video...')
    for nframe in range(target_video.length):
        frame = target_video.frames[nframe]
        original = frame
        frame = change_detection_pipe(frame)
        bg = bg_pipe(bg, frame, original)
        frame = blob_pipe(frame, original)
        frame = mask_pipe(original.Gray2BGR())

        csvData[nframe] = [ b.toCSV() for b in blobs ]
        outputFrames[nframe] = frame.copy()
    print('done\nsaving outputs...')

else:
    data.visual()

    def __elaborate__(video, frame, nframe, exit):
        global bg, data, pipeline, csvData
        if nframe == 0: blobs.clear()
        original = frame
        masked = frame.Gray2RGB()
        changes = change_detection_pipe(frame)
        if data.changes: frame = changes
        bg = bg_pipe(bg, frame, original)
        rbg = bg.copy()
        if not data.background: rbg = rbg.blankCopy()
        pipe_context['bg'] = rbg
        blob_frame = blob_pipe(frame, original)
        if data.blobs: frame = blob_frame
        masked = mask_pipe(masked, original)

        original.display('input')
        rbg.asByte().display('background')
        masked.display('outuput')

        csvData[nframe] = [ b.toCSV() for b in blobs ]
        outputFrames[nframe] = masked.copy()

        if not data.filter:
            frame = original
            pipe_context['bg'] = bg
        frame = visual_pipe(frame, nframe)
        data.applyTo(video)
        return frame

    def __index__(video, nframe, exit):
        if data.speed == 0: return nframe
        elif data.speed > 0: return nframe + 1
        else: return nframe - 1

    def makeKeyLambda(fun, *args): return lambda v,k,e: fun(*args)

    target_video.onMouse(data.OnMouseMove)
    target_video.onElaboration(__elaborate__)
    target_video.onFrame(__index__)

    target_video.onKey('n', makeKeyLambda(data.toggle_background))
    target_video.onKey('\r', makeKeyLambda(data.toggle_changes)) # enter
    target_video.onKey(' ', makeKeyLambda(data.pause)) # space
    target_video.onKey('v', makeKeyLambda(data.toggle_visualization))
    target_video.onKey('f', makeKeyLambda(data.toggle_filter))
    target_video.onKey('r', makeKeyLambda(data.toggle_rects))
    target_video.onKey('b', makeKeyLambda(data.toggle_blobs))
    target_video.onKey('t', makeKeyLambda(data.toggle_render))
    target_video.onKey('0', makeKeyLambda(data.reset))
    target_video.onKey('+', makeKeyLambda(data.add_speed, 1, False))
    target_video.onKey('-', makeKeyLambda(data.add_speed, -1, False))
    target_video.onKey('*', makeKeyLambda(data.add_speed, 2, True))
    target_video.onKey('/', makeKeyLambda(data.add_speed, .5, True))
    target_video.onKey('.', makeKeyLambda(data.add_speed, -1, True))
    target_video.onKey('q', makeKeyLambda(data.add_scale, -.1))
    target_video.onKey('w', makeKeyLambda(data.add_scale, .1))
    target_video.onKey('a', makeKeyLambda(data.add_threshold, -1))
    target_video.onKey('s', makeKeyLambda(data.add_threshold, 1))

    target_video.play(loop=not args.get('no_loop'), name="Visual Editor")

    Video.closeAll()


# Saving output
outputVideo = Video([s for s in outputFrames if s is not None])
outputVideo.save(args.get('output') + '.avi', fps=saved_fps)

utils.saveBlobsCsv(args.get('output') + '.csv', csvData)