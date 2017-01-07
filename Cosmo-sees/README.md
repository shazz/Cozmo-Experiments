# Cozmo Sees...

### Summary

A first try to use Tensorflow and Cozmo, this time I used the Inception v3 pretrained model from Google (https://research.googleblog.com/2016/03/train-your-own-image-classifier-with.html) to classify what Cozmo sees...
Considering Cozmo sees in VGA and Grayscale, the results are not yet so good so I probably need to preprocess the VGA image first. More to come.

### Installation

Install the prerequisites for Python 3.5:
```
sudo apt-get install python3-pil.imagetk

pip3 install tensorflow
pip3 install Pillow
pip3 install --user 'cozmo[camera]'
```
That should be fine...

### Run

`python3 cozmo_classify.py`
 
 
