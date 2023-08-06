import torch
from .clip_multi_label_class.text_image_dm import TextImageDataset
from .clip_multi_label_class.wrapper import CLIPWrapper
import torch.nn.functional as F
import PIL
import json


class MultiClass(object):
    def __init__(self, PATH="multi.ckpt", base_model='ViT-B/16', label="label.json", device="cuda" ):
        super().__init__()
        self.model = CLIPWrapper.load_from_checkpoint(model_name=base_model, config=None, checkpoint_path=PATH, minibatch_size=64, avg_word_embs=True )
        self.model.eval()
        self.model.to(device).float()
        self.data_loader = TextImageDataset(folder="")
        self.m = json.load(open(label))
        self.device = device
    
    def predict(self, image_file):
        image = self.data_loader.image_transform(PIL.Image.open(image_file))
        image = image.to(self.device)
        ims = F.normalize(self.model.model.encode_image(torch.stack([image],dim=0)), dim=1)
        result = []
        for i in range(len(self.m)):
            x = self.model.heads[i](ims)
            result.append({"score":x.detach().cpu().numpy()[0][0], "label":self.m[str(i)]})
        return result
