import cv2
from image_to_text.craft_text_detector import get_prediction, load_craftnet_model, load_refinenet_model
from image_to_text.config import Config as config
import numpy as np


def load_detector_model(config):
    # load models
    refiner_net = load_refinenet_model(cuda=config.is_cuda)
    craft_net = load_craftnet_model(cuda=config.is_cuda)
    return craft_net, refiner_net


def get_text_box(image_name, config, craft_net, refiner_net, filter_box=True, check_box=True,img_detect_name='img'):
    img = cv2.imread(image_name)
    h, w, c = img.shape
    # perform prediction
    prediction_result = get_prediction(
        image=image_name,
        craft_net=craft_net,
        refine_net=refiner_net,
        text_threshold=config.detector_threshold['text_threshold'],
        link_threshold=config.detector_threshold['link_threshold'],
        low_text=config.detector_threshold['low_text'],
        cuda=config.is_cuda,
        long_size=config.detector_threshold['long_size'],
        poly=True
    )
    bboxes_word = prediction_result['boxes']
    sorted_boxes = sorted(bboxes_word, key=lambda box: [box[0][0]])
    box_rect_info = []
    for i, box in enumerate(sorted_boxes):
        # filter box not is rectangle
        if filter_box:
            (x0, y0) = (int(box[0][0]), int(box[0][1]))
            (x1, y1) = (int(box[1][0]), int(box[1][1]))
            (x2, y2) = (int(box[2][0]), int(box[2][1]))
            (x3, y3) = (int(box[3][0]), int(box[3][1]))
            if x0 <= 0 or y0 <= 0 or x2 >= w or y2 >= h:
                continue
            if abs(y0 - y1) < config.filter_box_y_threshold and abs(y2 - y3) < config.filter_box_y_threshold:
                box_rect_info.append([(x0, y0), (x2, y2)])
                if check_box:
                    pts = np.array([(x0, y0), (x1, y1), (x2, y2), (x3, y3)], np.int32)
                    cv2.polylines(img, [pts], True, (0, 255, 0), 1)
                    cv2.rectangle(img, (x0, y0), (x2, y2), (0, 0, 255), 1)
        else:
            (x0, y0) = (int(box[0][0]), int(box[0][1]))
            (x1, y1) = (int(box[1][0]), int(box[1][1]))
            (x2, y2) = (int(box[2][0]), int(box[2][1]))
            (x3, y3) = (int(box[3][0]), int(box[3][1]))
            if x0 <= 0 or y0 <= 0 or x2 >= w or y2 >= h:
                continue
            if check_box:
                pts = np.array([(x0, y0), (x1, y1), (x2, y2), (x3, y3)], np.int32)
                cv2.polylines(img, [pts], True, (0, 255, 0), 2)
                cv2.rectangle(img, (x0, y0), (x2, y2), (0, 0, 255), 2)
            box_rect_info.append([(x0, y0), (x2, y2)])
    if check_box:
        cv2.imwrite(img_detect_name, img)

    return box_rect_info


def grouping_into_lines(boxes):
    if len(boxes) == 0:
        return [], 1024, 0
    elif len(boxes) == 1:
        return [boxes], 1024, 0

    lines = []
    sorted_boxes = sorted(boxes, key=lambda box: [box[0][1], box[0][0]])
    lines.append([sorted_boxes[0]])

    top_border = sorted_boxes[0][0][1]
    bot_border = sorted_boxes[0][1][1]
    stopping_idx = 0

    for i, box in enumerate(sorted_boxes[1:]):
        stopping_idx = i + 1
        middle_point = (box[0][1] + box[1][1]) / 2
        if top_border <= middle_point <= bot_border:  # same line
            lines[0].append(box)
            top_border = min(top_border, box[0][1])
            bot_border = max(bot_border, box[1][1])
        else:  # different line
            stopping_idx -= 1
            break

    if stopping_idx < len(sorted_boxes) - 1:
        new_line, new_top_border, new_bot_border = grouping_into_lines(
            sorted_boxes[stopping_idx + 1:])
        lines.extend(new_line)
        top_border = min(top_border, new_top_border)
        bot_border = max(bot_border, new_bot_border)

    return lines, top_border, bot_border


# if __name__ == '__main__':
#     image = 'image_test/test.PNG'
#     img = cv2.imread(image)
#     craft_net, refine_net = load_detector_model(config)
#     box_info = get_text_box(image, config, craft_net, refine_net)
#     print(box_info)

