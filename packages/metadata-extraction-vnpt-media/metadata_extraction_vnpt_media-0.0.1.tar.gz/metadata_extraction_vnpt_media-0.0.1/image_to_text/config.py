from image_to_text.src.deeptext.utils import CTCLabelConverter, AttnLabelConverter
import torch


class Config:
    is_cuda = True
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    detector_threshold = {'text_threshold': 0.7, 'link_threshold': 0.5, 'low_text': 0.4, 'long_size': 1280}
    character = open(r'D:\Source\MetaDataExtraction\image_to_text\src\char\char.txt', 'r', encoding="utf8").read()
    batch_max_length = 20
    workers = 4
    batch_size = 1
    saved_model = r'D:\Source\MetaDataExtraction\image_to_text\model\best_accuracy.pth'
    imgH = 32
    imgW = 100
    sensitive = True
    rgb = False
    Transformation = 'None'
    FeatureExtraction = 'ResNet'
    SequenceModeling = 'BiLSTM'
    Prediction = 'Attn'
    num_fiducial = 20
    input_channel = 1
    output_channel = 512
    hidden_size = 256

    if Prediction == 'CTC':
        converter = CTCLabelConverter(character)
    else:
        converter = AttnLabelConverter(character)
    num_class = len(converter.character)
    padding = 4
    text_confidence_threshold = 0.1
    filter_box_y_threshold = 10
