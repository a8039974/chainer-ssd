#! /usr/bin/env python3

import argparse
import cv2
import matplotlib.pyplot as plot
import numpy as np

from chainer import serializers

import config
from lib import MultiBoxEncoder
from lib import SSD300
from lib import VOCDataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model')
    parser.add_argument('image')
    args = parser.parse_args()

    model = SSD300(20)
    serializers.load_npz(args.model, model)

    multibox_encoder = MultiBoxEncoder(
        model=model,
        steps=config.steps,
        sizes=config.sizes,
        variance=config.variance)

    src = cv2.imread(args.image, cv2.IMREAD_COLOR)

    x = cv2.resize(src, (model.insize, model.insize)).astype(np.float32)
    x -= config.mean
    x = x.transpose(2, 0, 1)
    x = x[np.newaxis]

    loc, conf = model(x)
    results = multibox_encoder.decode(loc.data[0], conf.data[0], 0.45, 0.01)

    figure = plot.figure()
    ax = figure.add_subplot(111)
    ax.imshow(src[:, :, ::-1])

    for box, label, score in results:
        box = np.array(box)
        box[:2] *= src.shape[1::-1]
        box[2:] *= src.shape[1::-1]
        box = box.astype(int)

        print(label + 1, score, *box)

        if score > 0.6:
            ax.add_patch(plot.Rectangle(
                (box[0], box[1]), box[2] - box[0], box[3] - box[1],
                fill=False, edgecolor='red', linewidth=3))
            ax.text(
                box[0], box[1], VOCDataset.labels[label],
                bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 10})

    plot.show()