import altius_py
import numpy as np
from PIL import Image
from torchvision import transforms
import os, random
from matplotlib import pyplot as plt
import onnxruntime as ort
from torchvision.models import mobilenetv3


def main():
    labels = open("../models/imagenet_classes.txt").readlines()
    image = Image.open("../models/cat.png")

    preprocess = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    input = preprocess(image)
    input = input.unsqueeze(0).numpy()

    model = mobilenetv3.mobilenet_v3_large(pretrained=True)
    import torch
    import time
    for i in range(10):
        start = time.time()
        t = model(torch.tensor(input))
        end = time.time()
        print(end - start)


    sess_altius = altius_py.InferenceSession("../models/mobilenetv3.onnx")
    sess_ort = ort.InferenceSession("../models/mobilenetv3.onnx")

    for i in range(2):
        for sess in [sess_altius, sess_ort]:
            inputs = {"input": input}
            start = time.time()
            output = sess.run(None, inputs)[0][0]
            end = time.time()
            print(end-start)
            output = np.argsort(output)[::-1][:5]
            output = [labels[i].strip() for i in output]
            print(f"top5: {output}")


if __name__ == "__main__":
    main()
