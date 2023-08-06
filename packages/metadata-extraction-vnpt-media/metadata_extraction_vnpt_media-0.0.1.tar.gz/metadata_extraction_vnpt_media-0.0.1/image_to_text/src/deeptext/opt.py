from src.deeptext.utils import CTCLabelConverter, AttnLabelConverter, Averager
character=open('./src/char/char.txt', 'r', encoding="utf8").read()
batch_max_length=20
workers=4
batch_size=1
# saved_model = '/nfs/vision/DungTD12/deep-text-recognition/saved_models/saved_models_viet_mjsynth_sensitive/None-ResNet-BiLSTM-Attn-Seed1111/best_accuracy.pth'
saved_model = '/nfs/vision/DungTD12/deep-text-recognition/saved_models/a4_dangkiem_viet_aug_mjsynth_bctc_donthuoc_fakespace_20/None-ResNet-BiLSTM-Attn-Seed1111/best_accuracy.pth'
imgH=32
imgW=100
sensitive = True
export_dir = './20220209_onnx_donthuoc_name_spaces'
rgb=False
Transformation = 'None'
FeatureExtraction = 'ResNet'
SequenceModeling = 'BiLSTM'
Prediction = 'Attn'
num_fiducial=20
input_channel=1
output_channel=512
hidden_size =256

if Prediction == 'CTC':
    converter = CTCLabelConverter(character)
else:
    converter = AttnLabelConverter(character)
num_class = len(converter.character)
