import os
import shutil
import cv2
from image_to_text.detector_process import load_detector_model, get_text_box, grouping_into_lines
from image_to_text.config import Config as config
from image_to_text.reader_process import load_reader_model, read_text
import time
import torch
import json


# def read_text_from_img(folder_input, folder_out, name_video):
#     start = time.perf_counter()
#     # Create a directory to store the results
#     folder_result = os.path.join(folder_out, name_video)
#     folder_detection= os.path.join(folder_out, name_video,"TextDetection")
#     if os.path.isdir(folder_result):
#         shutil.rmtree(folder_result)
#     os.makedirs(folder_result)
#     os.makedirs(folder_detection)
#
#     # load detector model
#     detect_st = time.time()
#     craft_net, refine_net = load_detector_model(config)
#     print('load detector model time: {}s'.format(time.time() - detect_st))
#
#     # load reader model
#     reade_st = time.time()
#     reader_model = load_reader_model(config)
#     print('load reader model time: {}s'.format(time.time() - reade_st))
#
#     l_text = []
#     l_time = []
#
#     for file_name in os.listdir(folder_input):
#         torch.cuda.empty_cache()  # Release gpu memory
#         full_file_name = os.path.join(folder_input, file_name)
#         time_text = file_name.split('_')[-1].split('.')[0]
#         l_time.append(time_text)
#
#         img_cv = cv2.imread(full_file_name)
#
#         # detect text box in image
#         img_detect = os.path.join(folder_detection, file_name)
#         box_info = get_text_box(full_file_name, config, craft_net, refine_net, filter_box=True, check_box=True,img_detect_name=img_detect)
#
#         print('detected have {} box'.format(len(box_info)))
#
#         # group box into lines
#         box_line, _, _ = grouping_into_lines(box_info)
#
#         # read text
#         st = time.time()
#         for line in box_line:
#             line_text = ''
#             sorted_line = sorted(line, key=lambda box: [box[0][0]])
#             for box in sorted_line:
#                 try:
#                     img_crop = img_cv[box[0][1] - config.padding:box[1][1] + config.padding,box[0][0] - config.padding:box[1][0] + config.padding]
#                     pred, confidence_score = read_text(img_crop, reader_model)
#                 except:
#                     continue
#                 if confidence_score > config.text_confidence_threshold:
#                     line_text += pred + ' '
#             l_text.append(line_text)
#
#     l_text = list(set(l_text))
#
#     if len(l_text) != 0:
#         with open(os.path.join(folder_result, 'text.txt'), 'w', encoding='utf-8') as f:
#             # write elements of list
#             for items in l_text:
#                 f.write('%s\n' % items)
#         # close the file
#         f.close()
#
#     if len(l_time) != 0:
#         with open(os.path.join(folder_result, 'time.txt'), 'w', encoding='utf-8') as f:
#             # write elements of list
#             for items in l_time:
#                 f.write('%s\n' % items)
#         # close the file
#         f.close()
#     print(f'Time read text: {time.perf_counter() - start}')

def read_text_from_img(folder_input, folder_result, folder_detection):
    time_start = time.perf_counter()
    # load detector model
    # detect_st = time.time()
    craft_net, refine_net = load_detector_model(config)
    # print('load detector model time: {}s'.format(time.time() - detect_st))

    # load reader model
    # reade_st = time.time()
    reader_model = load_reader_model(config)
    # print('load reader model time: {}s'.format(time.time() - reade_st))
    json_list = []

    for file_name in os.listdir(folder_input):
        l_text = []
        torch.cuda.empty_cache()  # Release gpu memory
        full_file_name = os.path.join(folder_input, file_name)
        time_text = file_name.split('_')[-1].replace(".jpg", "")

        img_cv = cv2.imread(full_file_name)

        # detect text box in image
        img_detect = os.path.join(folder_detection, file_name)
        box_info = get_text_box(full_file_name, config, craft_net, refine_net, filter_box=True, check_box=True,
                                img_detect_name=img_detect)

        # print('detected have {} box'.format(len(box_info)))
        """ group box into lines """
        box_line, _, _ = grouping_into_lines(box_info)

        """ read text """
        for line in box_line:
            line_text = ''
            sorted_line = sorted(line, key=lambda box: [box[0][0]])
            for box in sorted_line:
                try:
                    img_crop = img_cv[box[0][1] - config.padding:box[1][1] + config.padding,
                               box[0][0] - config.padding:box[1][0] + config.padding]
                    pred, confidence_score = read_text(img_crop, reader_model)
                except:
                    continue
                if confidence_score > config.text_confidence_threshold:
                    line_text += pred + ' '
            l_text.append(line_text)
        txt_result = '\n'.join(l_text)
        json_list.append({"time": time_text, "text": txt_result})

    if len(json_list) != 0:
        with open(os.path.join(folder_result, 'result.json'), 'w', encoding='utf-8') as f:
            # write elements of list
            json.dump(json_list, f, ensure_ascii=False, indent=4)
        # close the file
        f.close()
    time_process = time.perf_counter() - time_start
    print(f'Time read text: {time_process}')
    return time_process

# read_text_from_img(r'D:\DataRun\FramesInput', r'D:\DataRun\TextOutput', 'Test')
