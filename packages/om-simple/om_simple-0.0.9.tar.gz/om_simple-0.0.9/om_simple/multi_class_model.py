import torch
from .clip_multi_label_class.text_image_dm import TextImageDataset
from .clip_multi_label_class.wrapper import CLIPWrapper
import torch.nn.functional as F
import PIL
import json
import pprint

class MultiClass(object):
    def __init__(self, PATH, label="label.json",  base_model='ViT-B/16', device="cuda"):
        super().__init__()
        self.model = CLIPWrapper.load_from_checkpoint(model_name=base_model, config=None, checkpoint_path=PATH, minibatch_size=64, avg_word_embs=True )
        self.model.eval()
        self.model.to(device).float()
        self.data_loader = TextImageDataset(folder="")
        self.m = json.load(open(label))
        self.device = device
    
    def predict(self, images:list, threshold=0):
        temp = []
        results = []
        for image_file in images:
            image = self.data_loader.image_transform(PIL.Image.open(image_file))
            image = image.to(self.device)
            temp.append(image)
            results.append([])
        ims = F.normalize(self.model.model.encode_image(torch.stack(temp,dim=0)), dim=1)
        for i in range(len(self.m)):
            x = self.model.heads[i](ims)
            for j in range(len(x)):
                score = x.detach().cpu().numpy()[j][0]
                if score > threshold:
                    results[j].append({"score":score, "label":self.m[str(i)]})
        return results
