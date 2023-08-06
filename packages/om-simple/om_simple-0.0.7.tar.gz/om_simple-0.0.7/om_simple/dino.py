import torch
from torchvision import transforms as pth_transforms
from PIL import Image
import om_simple.vision_transformer as vits


class Dino(object):
    def __init__(self, pretrained_weights, arch="vit_small",patch_size=8, checkpoint_key="teacher",image_size=(480,480)):
        self.pretrained_weights = pretrained_weights #"checkpoint0020.pth"
        self.image_size = image_size
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        # build model
        self.model = vits.__dict__[arch](patch_size=patch_size, num_classes=0)
        for p in self.model.parameters():
            p.requires_grad = False
        self.model.eval()
        self.model.to(self.device)
        self.state_dict = torch.load(pretrained_weights, map_location="cpu")
        if checkpoint_key is not None and checkpoint_key in self.state_dict:
            print(f"Take key {checkpoint_key} in provided checkpoint dict")
            self.state_dict = self.state_dict[checkpoint_key]
        # remove `module.` prefix
        self.state_dict = {k.replace("module.", ""): v for k, v in self.state_dict.items()}
        # remove `backbone.` prefix induced by multicrop wrapper
        self.state_dict = {k.replace("backbone.", ""): v for k, v in self.state_dict.items()}
        msg = self.model.load_state_dict(self.state_dict, strict=False)
        print('Pretrained weights found at {} and loaded with msg: {}'.format(pretrained_weights, msg))
    
    def encode(self, image_paths):
        imgs = []
        for image_path in image_paths:
            with open(image_path, 'rb') as f:
                img = Image.open(f)
                img = img.convert('RGB')
            transform = pth_transforms.Compose([
                pth_transforms.Resize(self.image_size),
                pth_transforms.ToTensor(),
                pth_transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
            ])
            img = transform(img)
            imgs.append(img)
        imgs = torch.stack(imgs)
        feats = self.model(imgs.to(self.device))
        return feats
   

if __name__ == "__main__":
    X = Dino("checkpoint0020.pth")
    e = X.encode(["/mnt/soco1/public/bolts/00566860.jpg"])
    print (e)
