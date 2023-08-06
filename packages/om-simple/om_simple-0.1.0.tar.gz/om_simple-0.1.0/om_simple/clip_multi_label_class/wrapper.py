import torch, json
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
import numpy as np
import math
import yaml
import copy
from .model import CLIP
import om_simple.clip as clip


class CLIPWrapper(pl.LightningModule):
    def __init__(self,
                 model_name: str,
                 config: dict,
                 minibatch_size: int
                 ):
        """A lightning wrapper for a CLIP model as specified in the paper.

        Args:
            model_name (str): A case sensitive visual model name.
            config (dict): A dictionary containing the CLIP instantiation parameters.
        """
        super().__init__()
        self.model_name = model_name
        self.minibatch_size = minibatch_size
        self.isViT = 'ViT' in self.model_name
        device = "cuda" if torch.cuda.is_available() else "cpu"
        with torch.no_grad():
            #self.model, self.preprocess = clip.load("ViT-B/32", jit=False, device=device)
            #self.model, self.preprocess = clip.load("ViT-L/14", jit=False, device=device)
            self.model, self.preprocess = clip.load("ViT-B/16", jit=False)
        
        for p in self.model.parameters():
            p.requires_grad_(False)

        self.automatic_optimization = False
        self.heads = {}
        self.labels = json.load(open("label.json"))
        temp = []
        for i in self.labels:
            temp.append(self.labels[i])
        text_input = clip.tokenize(temp).to(device)
        text_emd  = self.model.encode_text(text_input)
        self.heads = nn.ModuleList([nn.Linear(512,1) for i in range(len(self.labels))])
        for i in range(len(self.labels)):
            #self.heads[i].weight.data = F.normalize(torch.stack([text_emd[i-1]]).to(torch.float32),dim=1)
            self.heads[i].weight.data = F.normalize(torch.stack([text_emd[i]]).to(torch.float32),dim=1)
    
    @property
    def num_training_steps(self) -> int:
        """Total training steps inferred from datamodule and devices."""
        dataset = self.train_dataloader()
        if self.trainer.max_steps:
            return self.trainer.max_steps

        dataset_size = (
            self.trainer.limit_train_batches
            if self.trainer.limit_train_batches != 0
            else len(dataset)
        )
        num_devices = max(1, self.trainer.num_gpus, self.trainer.num_processes)
        if self.trainer.tpu_cores:
            num_devices = max(num_devices, self.trainer.tpu_cores)

        effective_batch_size = dataset.batch_size * self.trainer.accumulate_grad_batches * num_devices
        return int((dataset_size // effective_batch_size) * self.trainer.max_epochs)

    def training_step(self, train_batch, idx):
        # get optimizers and scheduler
        optimizer = self.optimizers()
        image, text, neg_text, pos, neg = train_batch
        n = math.ceil(len(image) // self.minibatch_size)
        image_mbs = torch.chunk(image, n)
        text_mbs = torch.chunk(text, n)
        # calculate original statistics
        ims = [F.normalize(self.model.encode_image(im), dim=1) for im in image_mbs]
        # gather from all GPUs
        ims = self.all_gather(torch.cat(ims))

        if len(ims.shape) == 3:
            ims = list(ims)
        else:
            ims = [ims]

        sum_pos = []
        sum_neg = []
        if isinstance(optimizer, list):
            optimizer = optimizer[0]
        optimizer.zero_grad()
        batch_size = len(neg)
        c = 0
        inc = 0
        tp, tn, fp, fn = 0, 0, 0, 0
        for i in range(batch_size):
            for pj in pos[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                #num = -self.heads[int(pj)-1](z)
                num = -self.heads[int(pj)](z)
                if num < 0:
                    c+=1
                    tp += 1
                else:
                    inc+=1
                    fn+=1

                sum_pos.append(torch.exp(num))
            for nj in neg[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                #num = self.heads[int(nj)-1](z)
                num = self.heads[int(nj)](z)
                if num < 0:
                    c+=1
                    tn +=1
                else:
                    inc+=1
                    fp +=1
                sum_neg.append(torch.exp(num))
        loss = torch.log(1+sum(sum_pos)+sum(sum_neg))
        acc = float(c) /(c+inc)
        try:
            p =  float(tp) / (tp+fp)
        except:
            p = 0
        try:
            r = float(tp) / (tp+fn)
        except:
            r = 0
        try:
            f1= 2*(p*r)/(p+r)
        except:
            f1 = 0

        self.log_dict({'loss': loss, 'prec':p, 'recall':r,'f1':f1, 'acc':acc}, prog_bar=True)
        self.manual_backward(loss)
        optimizer.step()
        lr_scheduler = self.lr_schedulers()
        lr_scheduler.step()

    def forward(self, images, pos, neg):
        poss = []
        negs = []
        ims = F.normalize(self.model.encode_image(images), dim=1) 
        batch_size = len(neg)
        for i in range(batch_size):
            for pj in pos[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = -self.heads[int(pj)-1](z)
                sum_pos.append(torch.exp(num))
            for nj in neg[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = self.heads[int(nj)-1](z)
                sum_neg.append(torch.exp(num))
        loss = torch.log(1+sum(sum_pos)+sum(sum_neg))
        return loss

    def validation_step(self, val_batch, idx):
        image, text, neg_text,pos, neg = val_batch
        n = math.ceil(len(image) // self.minibatch_size)
        image_mbs = torch.chunk(image, n)
        text_mbs = torch.chunk(text, n)
        sum_pos = []
        sum_neg = []
 
        ims = [F.normalize(self.model.encode_image(im), dim=1) for im in image_mbs]
        ims = self.all_gather(torch.cat(ims))
        if len(ims.shape) == 3:
            ims = list(ims)
        else:
            ims = [ims]
 
        poss= []
        negs = []
        cor,inc = 0,0
        tp, tn, fp, fn = 0, 0, 0, 0
        batch_size = len(neg)
        for i in range(batch_size):
            for pj in pos[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = -self.heads[int(pj)-1](z)
                if num < 0:
                    tp += 1
                else:
                    fn+=1

                sum_pos.append(torch.exp(num))
            for nj in neg[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = self.heads[int(nj)-1](z)
                if num < 0:
                    tn +=1
                else:
                    fp +=1
        try: 
            p =  float(tp) / (tp+fp)
        except:
            p = 0
        try:
            r = float(tp) / (tp+fn)
        except:
            r = 0
        try:
            f1= 2*(p*r)/(p+r)
        except:
            f1 = 0
        self.log_dict({'val_prec':p,'val_recall':r,"val_f1":f1})
    
    def test_step(self, test_batch, idx):
        image, text, neg_text,pos, neg = test_batch
        n = math.ceil(len(image) // self.minibatch_size)
        image_mbs = torch.chunk(image, n)
        text_mbs = torch.chunk(text, n)
 
        ims = [F.normalize(self.model.encode_image(im), dim=1) for im in image_mbs]
        ims = self.all_gather(torch.cat(ims))
        if len(ims.shape) == 3:
            ims = list(ims)
        else:
            ims = [ims]
 
        poss= []
        negs = []
        cor,inc = 0,0
        tp, tn, fp, fn = 0, 0, 0, 0
        for i in range(batch_size):
            for pj in pos[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = -self.heads[int(pj)-1](z)
                if num < 0:
                    tp += 1
                else:
                    fn+=1

                sum_pos.append(torch.exp(num))
            for nj in neg[i]:
                z = F.normalize(torch.cat(ims).to(torch.float32)[i,:], dim=0)
                num = self.heads[int(nj)-1](z)
                if num < 0:
                    tn +=1
                else:
                    fp +=1
 
        p =  float(tp) / (tp+fp)
        r = float(tp) / (tp+fn)
        f1= 2*(p*r)/(p+r)
 
        self.log({'val_prec':p,'val_recall':r,"val_f1":f1})


    def configure_optimizers(self):
        #return {"optimizer":torch.optim.Adam(self.parameters(), lr=5e-4)}
        lr = {
            "RN50": 5e-4,
            "RN101": 5e-4,
            "RN50x4": 5e-4,
            "RN50x16": 4e-4,
            "RN50x64": 3.6e-4,
            "ViT-B/32": 5e-4,
            "ViT-B/16": 5e-4,
            "ViT-L/14": 4e-4,
            "ViT-L/14-336px": 2e-5
        }[self.model_name]

        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=lr,
            betas=(
                0.9,
                0.98 if self.isViT else 0.999
            ),
            eps=1e-6 if self.isViT else 1e-8,
            weight_decay=0.2
        )

        # Source: https://github.com/openai/CLIP/issues/107
        # Use pip install 'git+https://github.com/katsura-jp/pytorch-cosine-annealing-with-warmup'
        """
        lr_scheduler = CosineAnnealingWarmupRestarts(
            optimizer,
            first_cycle_steps=self.num_training_steps,
            cycle_mult=1.0,
            max_lr=lr,
            min_lr=0,
            warmup_steps=2000
        )
        """
        lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=2000
        )

        return {'optimizer': optimizer, 'lr_scheduler': lr_scheduler}

