# Image Classification
```
pip install om-simple
```

## Data Preparation

```
{dataset name}/
├── train/
│   ├── {class1}/
│   ├── {class2}/
│   ├── ...
└── val/
    ├── {class1}/
    ├── {class2}/
    ├── ...
```

## Example Code
```python
from om_simple.img_class_head import ImageClassification
from om_simple.img_class_model import run_train
from om_simple.tools.utils import is_blur

# Train
run_train("{dataset name}",
    model_name="{model_name}", # e.g., resnet18, resnet50, vit_base_patch16_224, etc....
    outdir="{output_dir}")

# Simple Classification
X = ImageClassification("epoch099.ckpt")
z = X.predict(images=["sample.jpg"])


# Blur detection
print (is_blur("sample.jpg"))

# Multi label classification

from om_simple.multi_class_model import MultiClass
X = MultiClass("model.ckpt","label.json")
z = X.predict(images=["sample.jpg"])




```


# How to get available model_name
```
import timm
avail_pretrained_models = timm.list_models(pretrained=True)
print (avail_pretrained_models)

all_vit_models = timm.list_models('vit*')
print (all_vit_models)

```

# Tensorboard
```
tensorboard --logdir {output_dir} --bind_all
```
