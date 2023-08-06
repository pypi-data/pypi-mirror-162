import os
from configparser import ConfigParser
import time
import nvidia_smi
from numba import cuda
from classify_image.classify import find_img_contain_text
from extract_video.extract_with_decord import extract_frames
from image_to_text.read_text import read_text_from_img
import sys
import shutil

if __name__ == '__main__':
    if len(sys.argv) == 2:
        """ Read file config """
        pathVideo = sys.argv[1]
        # pathVideo = r"D:\VideoTest\BrothersForLife3.mp4"
        path_real, fl = os.path.split(os.path.realpath(__file__))
        try:
            configur = ConfigParser()
            configur.read(os.path.join(path_real, 'config_param.ini'))
            framesTemp = configur.get('folder', 'frames')
            imgInput = configur.get('folder', 'img')
            folder_output = configur.get('folder', 'output')
            FPS = float(configur.get('param', 'fps'))
            modelClassify = configur.get('param', 'model_classify')
        except:
            print("Error: param not found")
        """ Extract frames from video """
        l_time_process = []
        start = time.perf_counter()
        print('Extracting frames from video...')
        time_extract, _ = extract_frames(pathVideo, framesTemp, overwrite=True, start=-1, end=-1, time_split=3.5)
        l_time_process.append(f'Time extract video: {round(time_extract)} seconds')
        """ Find images containing text """
        print('Find images containing text...')
        time_classify = find_img_contain_text(modelClassify, framesTemp, imgInput)
        l_time_process.append(f'Time classify: {round(time_classify)} seconds')
        """ Check GPU Memory Free """
        nvidia_smi.nvmlInit()
        device = cuda.get_current_device()
        device.reset()
        # handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
        # info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        # print("Free GPU memory:", info.free / 1024 ** 2)
        """ Create a directory to store the results """
        name_video = os.path.splitext(os.path.basename(pathVideo))[0]
        folder_result = os.path.join(folder_output, name_video)
        folder_detection = os.path.join(folder_output, name_video, "TextDetection")
        if os.path.isdir(folder_result):
            shutil.rmtree(folder_result)
        os.makedirs(folder_result)
        os.makedirs(folder_detection)
        """ Read text """
        time_read_text = read_text_from_img(imgInput, folder_result, folder_detection)
        l_time_process.append(f'Time read text: {round(time_read_text)} seconds')

        """ write time processing """
        time_total = time.perf_counter() - start
        l_time_process.append(f'Total time: {round(time_total)} seconds')

        if len(l_time_process) != 0:
            with open(os.path.join(folder_result, 'time_processing.txt'), 'w', encoding='utf-8') as f:
                for items in l_time_process:
                    f.write('%s\n' % items)
                f.close()

        print(f'Time processing: {time_total}')
    else:
        print("Error: No parameter")
