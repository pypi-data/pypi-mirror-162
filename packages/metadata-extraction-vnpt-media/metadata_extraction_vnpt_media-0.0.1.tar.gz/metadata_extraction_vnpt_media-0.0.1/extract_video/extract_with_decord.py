import shutil
import cv2
import os
from decord import VideoReader
from decord import cpu
import time
from datetime import timedelta


def format_timedelta(td):
    """Utility function to format timedelta objects in a cool way (e.g 00:00:20.05)
    omitting microseconds and retaining milliseconds"""
    result = str(td)
    try:
        result, ms = result.split(".")
    except ValueError:
        return (result + ".00").replace(":", "-")
    ms = int(ms)
    ms = int(ms / 1e4)
    return f"{result}.{ms:02}".replace(":", "-")


def extract_frames(video_path, frames_dir, overwrite=False, start=-1, end=-1, time_split=-1):
    """ Extract frames from a video using decord's VideoReader
    :param video_path: path of the video
    :param frames_dir: the directory to save the frames
    :param overwrite: to overwrite frames that already exist?
    :param start: start frame
    :param end: end frame
    :param every: frame spacing
    :return: time process """
    time_start = time.perf_counter()
    video_path = os.path.normpath(video_path)
    frames_dir = os.path.normpath(frames_dir)
    # make a folder by the name of the video file
    if os.path.isdir(frames_dir):
        shutil.rmtree(frames_dir)
    os.mkdir(frames_dir)
    # video_dir, video_filename = os.path.split(video_path)
    # basename = video_filename.split('.')[0]
    basename = os.path.splitext(os.path.basename(video_path))[0]

    assert os.path.exists(video_path)
    # load the VideoReader
    vr = VideoReader(video_path, ctx=cpu(0))  # can set to cpu or gpu .. ctx=gpu(0)
    fps = int(vr.get_avg_fps())
    every = int(time_split * fps)
    if start < 0:  # if start isn't specified lets assume 0
        start = 0
    if end < 0:  # if end isn't specified assume the end of the video
        end = len(vr)
    if time_split == -1:
        frames_list = vr.get_key_indices()
        print("Get key frame")
    else:
        frames_list = list(range(start, end, every))
    saved_count = 0
    if every > 25 and len(frames_list) < 5000:  # this is faster for every > 25 frames and can fit in memory
        frames = vr.get_batch(frames_list).asnumpy()
        for index, frame in zip(frames_list, frames):
            frame_duration = index / fps
            frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
            save_path = os.path.join(frames_dir, f"{basename}_{frame_duration_formatted}.jpg")
            if not os.path.exists(save_path) or overwrite:
                cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                saved_count += 1
    else:  # this is faster for every <25 and consumes small memory
        for index in frames_list:
            frame = vr[index]
            frame_duration = index / fps
            frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
            save_path = os.path.join(frames_dir, f"{basename}_{frame_duration_formatted}.jpg")
            if not os.path.exists(save_path) or overwrite:
                cv2.imwrite(save_path, cv2.cvtColor(frame.asnumpy(), cv2.COLOR_RGB2BGR))
                saved_count += 1
    time_process = time.perf_counter() - time_start
    print(f'Time extract video: {time_process}')
    return time_process, saved_count

# start = time.perf_counter()
# print(extract_frames(r'G:\8.Data Movie\20220414\Song.Lang.1080p.mp4', r'D:\DataRun\FramesTemp', overwrite=True, start=-1, end=-1, time_split=3.5))
# print(f'Duration: {time.perf_counter() - start}')
