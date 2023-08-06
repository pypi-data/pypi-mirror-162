import numpy as np
import torch
from torchvision import transforms
import torch.nn.functional as F
from image_to_text.config import Config as config
from PIL import Image
from image_to_text.src.deeptext.model import Model
from torch.utils.data import Dataset


class INFER_DATASET(Dataset):
    def __init__(self, img_list, size, input_channel=1, interpolation=Image.BICUBIC):
        super().__init__()
        self.img_list = img_list
        self.size = size
        self.input_channel = input_channel
        self.interpolation = interpolation
        self.toTensor = transforms.ToTensor()

    def __len__(self):
        return len(self.img_list)

    def __getitem__(self, index):
        if self.input_channel == 1:
            im = Image.fromarray(self.img_list[index]).convert('L')
        else:
            im = Image.fromarray(self.img_list[index]).convert('RGB')
        im = im.resize(self.size, self.interpolation)
        im = self.toTensor(im)
        im.sub_(0.5).div_(0.5)
        return im


class ResizeNormalize(object):

    def __init__(self, size, interpolation=Image.BICUBIC):
        self.size = size
        self.interpolation = interpolation
        self.toTensor = transforms.ToTensor()

    def __call__(self, img):
        img = img.resize(self.size, self.interpolation)
        img = self.toTensor(img)
        img.sub_(0.5).div_(0.5)
        return img


transform = ResizeNormalize((config.imgW, config.imgH))


def load_reader_model(config):
    model = Model(config)
    model = torch.nn.DataParallel(model).to(config.device)
    model.load_state_dict(torch.load(config.saved_model, map_location=config.device))
    return model


def read_text(image, model):
    preds_str = None
    pred = None
    confidence_score = None
    image = Image.fromarray(image).convert('L')
    image = transform(image)
    image = image.unsqueeze(0)
    model.eval()
    image = image.to(config.device)
    length_for_pred = torch.IntTensor([config.batch_max_length] * config.batch_size).to(config.device)
    text_for_pred = torch.LongTensor(config.batch_size, config.batch_max_length + 1).fill_(0).to(config.device)

    if 'CTC' in config.Prediction:
        preds = model(image, text_for_pred)
        preds_size = torch.IntTensor([preds.size(1)] * config.batch_size)
        _, preds_index = preds.max(2)
        pred = config.converter.decode(preds_index.data, preds_size.data)
    else:
        preds = model(image, text_for_pred, is_train=False)
        preds = preds[:, :config.batch_max_length, :]
        _, preds_index = preds.max(2)
        preds_str = config.converter.decode(preds_index, length_for_pred)

    preds_prob = F.softmax(preds, dim=2)
    preds_max_prob, _ = preds_prob.max(dim=2)
    for pred, pred_max_prob in zip(preds_str, preds_max_prob):
        if 'Attn' in config.Prediction:
            pred_EOS = pred.find('[s]')
            pred = pred[:pred_EOS]  # prune after "end of sentence" token ([s])
            pred_max_prob = pred_max_prob[:pred_EOS]
            confidence_score = pred_max_prob.cumprod(dim=0)[-1].item()

    return pred, confidence_score


def read_text_with_batch(list_img, model):
    infer_data = INFER_DATASET(list_img, (config.imgW, config.imgH), config.input_channel)
    model.eval()
    batch_size = config.batch_size
    if batch_size >= len(list_img):
        batch_size = len(list_img)
    evaluation_loader = torch.utils.data.DataLoader(infer_data, batch_size=batch_size,
                                                    shuffle=False,
                                                    num_workers=int(config.workers),
                                                    pin_memory=True)
    length_of_data = 0
    results = []
    for i, image_tensors in enumerate(evaluation_loader):
        batch_size = image_tensors.size(0)
        length_of_data = length_of_data + batch_size
        image = image_tensors.to(config.device)

        # For max length prediction
        length_for_pred = torch.IntTensor([config.batch_max_length] * batch_size).to(config.device)
        text_for_pred = torch.LongTensor(batch_size, config.batch_max_length + 1).fill_(0).to(config.device)

        preds = model(image, text_for_pred, is_train=False)
        preds = preds[:, :text_for_pred.shape[1] - 1, :]
        _, preds_index = preds.max(2)
        preds_str = config.converter.decode(preds_index, length_for_pred)

        preds_prob = F.softmax(preds, dim=2)
        preds_max_prob, _ = preds_prob.max(dim=2)
        for pred, pred_max_prob in zip(preds_str, preds_max_prob):
            pred_EOS = pred.find('[s]')
            pred = pred[:pred_EOS]
            pred_max_prob = pred_max_prob[:pred_EOS]
            confidence_score = pred_max_prob.cumprod(dim=0)[-1].item()
            results.append((pred, confidence_score))
    return results