import torch
import random
import cv2
import numpy as np
from torchvision.transforms import ColorJitter as ImageColorJitter

from .image_augmentation import ImageResize, ImageCropResize, \
    ImageMotionBlur, ImageCompression

from detectron2.data import transforms as T
from detectron2.data.transforms import Resize, HFlipTransform, RandomCrop, ResizeTransform, CropTransform
from detectron2.structures import Boxes, BoxMode, Instances

class VideoTransformer(object):
    def __init__(self, transform_fn=None):
        if transform_fn is None:
            raise KeyError('Transform function should not be None.')
        self.transform_fn = transform_fn

    def __call__(self, video, target=None):
        """
        A data transformation wrapper for video
        :param video: a list of images
        :param target: a list of BoxList (per image)
        """
        if not isinstance(video, (list, tuple)):
            return self.transform_fn(video, target)

        new_video = []
        new_target = []
        for (image, image_target) in zip(video, target):
            (image, image_target) = self.transform_fn(image, image_target)
            new_video.append(image)
            new_target.append(image_target)

        return new_video, new_target


class SiamVideoResize(ImageResize):
    def __init__(self, min_size, max_size, size_divisibility):
        super(SiamVideoResize, self).__init__(min_size, max_size, size_divisibility)
        # self.resize = T.ResizeShortestEdge(short_edge_length=list(min_size), max_size=max_size, sample_style='choice')

    def __call__(self, video, target=None):
        if not isinstance(video, (list, tuple)):
            return super(SiamVideoResize, self).__call__(video, target)

        assert len(video) >= 1
        new_size = self.get_size(video[0].shape[:2])
        new_video = []
        new_target = []
        for (image, image_target) in zip(video, target):
            (image, image_target) = self._resize(image, new_size, image_target)
            new_video.append(np.array(image))
            new_target.append(image_target)

        return new_video, new_target

    def _resize(self, image, size, target=None):
        resize = [Resize(size)]
        image, transform = T.apply_augmentations(resize, image)
        if target is None:
            return image, target
        transform_box = transform.apply_box(target.gt_boxes.tensor)
        h, w = size
        new_target = Instances((h, w))
        for field in target.get_fields():
            if field == "gt_boxes":
                new_target.set(field, Boxes(transform_box))
            else:
                new_target.set(field, target.get(field))
        return image, new_target

class SiamVideoRandomHorizontalFlip(object):
    def __init__(self, prob=0.5):
        self.prob = prob

    def __call__(self, video, target=None):

        if not isinstance(video, (list, tuple)):
            return video, target

        new_video = []
        new_target = []
        # All frames should have the same flipping operation
        if random.random() < self.prob:
            h, w = video[0].shape[:2]
            hflip = [HFlipTransform(w)]
            for (image, image_target) in zip(video, target):
                new_image, transform = T.apply_augmentations(hflip, image)
                transform_boxes = transform.apply_box(image_target.gt_boxes.tensor)
                image_target.set("gt_boxes", Boxes(transform_boxes))
                new_video.append(new_image)
                new_target.append(image_target)
        else:
            new_video = video
            new_target = target
        return new_video, new_target


class SiamVideoColorJitter(ImageColorJitter):
    def __init__(self,
                 brightness=None,
                 contrast=None,
                 saturation=None,
                 hue=None):
        super(SiamVideoColorJitter, self).__init__(brightness, contrast, saturation, hue)

    def __call__(self, video, target=None):
        # Color jitter only applies for Siamese Training
        if not isinstance(video, (list, tuple)):
            return video, target

        idx = random.choice((0, 1))
        transform = self.get_params(self.brightness, self.contrast,
                                    self.saturation, self.hue)
        new_video = []
        new_target = []
        for i, (image, image_target) in enumerate(zip(video, target)):
            if i == idx:
                image = self(image)[0]
            new_video.append(image)
            new_target.append(image_target)

        return new_video, new_target


class SiamVideoMotionAugment(object):
    def __init__(self, motion_limit=None, amodal=False):
        # maximum motion augmentation
        self.motion_limit = min(0.1, motion_limit)
        if motion_limit is None:
            self.motion_limit = 0
        self.crop_limit = motion_limit
        self.amodal = amodal

    def crop_motion(self, image, target):
        w, h = image.size

        tl_x = int(w * (random.random() * self.crop_limit))
        tl_y = int(h * (random.random() * self.crop_limit))
        br_x = int(w - w * (random.random() * self.crop_limit))
        # keep aspect ratio
        br_y = int((h / w) * (br_x - tl_x) + tl_y)

        if len(target) > 0:
            box = target.gt_boxes.tensor.clone()
            # get the visible part of the objects
            box_w = box[:, 2].clamp(min=0, max=w - 1) - \
                    box[:, 0].clamp(min=0, max=w - 1)
            box_h = box[:, 3].clamp(min=0, max=h - 1) - \
                    box[:, 1].clamp(min=0, max=h - 1)
            box_area = box_h * box_w
            max_area_idx = torch.argmax(box_area, dim=0)
            max_motion_limit_w = int(box_w[max_area_idx] * 0.25)
            max_motion_limit_h = int(box_h[max_area_idx] * 0.25)
            tl_x = min(tl_x, max_motion_limit_w)
            tl_y = min(tl_y, max_motion_limit_h)
            br_x = max(br_x, w-max_motion_limit_w)
            br_y = max(br_y, h-max_motion_limit_h)

        assert (tl_x < br_x) and (tl_y < br_y)
        top, left, height, width = tl_y, tl_x, (br_y - tl_y), (br_x - tl_x)

        im = np.array(image)
        h, w = im.shape[:2]
        randomcrop = [CropTransform(left, top, width, height)]

        im, crop_transform = T.apply_augmentations(randomcrop, im)
        crop_box = crop_transform.apply_box(target.gt_boxes.tensor)
        t_h, t_w = im.shape[:2]

        resize = [ResizeTransform(t_h, t_w, h, w)]

        im, resize_transform = T.apply_augmentations(resize, im)
        resize_box = resize_transform.apply_box(crop_box)


        new_target = Instances(target.image_size)
        for field in target.get_fields():
            if field != "gt_boxes":
                new_target.set(field, target.get(field))
            else:
                new_target.set("gt_boxes", Boxes(resize_box))
        return im, new_target


    def __call__(self, video, target=None):

        # Motion augmentation only applies for Siamese Training
        if not isinstance(video, (list, tuple)) or self.motion_limit == 0:
            return video, target

        new_video = []
        new_target = []
        # Only 1 frame go through the motion augmentation,
        # the other unchanged
        idx = random.choice((0, 1))
        for i, (image, image_target) in enumerate(zip(video, target)):
            if i == idx:
                (image, motion_target) = self.crop_motion(image, image_target)
            else:
                motion_target = image_target
            new_video.append(np.array(image))
            new_target.append(motion_target)
        return new_video, new_target


class SiamVideoMotionBlurAugment(object):
    def __init__(self, motion_blur_prob=None):
        self.motion_blur_prob = motion_blur_prob
        if motion_blur_prob is None:
            self.motion_blur_prob = 0.0
        self.motion_blur_func = ImageMotionBlur()

    def __call__(self, video, target):
        # Blur augmentation only applies for Siamese Training
        if not isinstance(video, (list, tuple)) or self.motion_blur_prob == 0.0:
            return video, target

        new_video = []
        new_target = []
        idx = random.choice((0, 1))
        for i, (image, image_target) in enumerate(zip(video, target)):
            if i == idx:
                random_prob = random.uniform(0, 1)
                if random_prob < self.motion_blur_prob:
                    image = self.motion_blur_func(image)
            new_video.append(image)
            new_target.append(image_target)

        return new_video, new_target


class SiamVideoCompressionAugment(object):
    def __init__(self, max_compression=None):
        self.max_compression = max_compression
        if max_compression is None:
            self.max_compression = 0.0
        self.compression_func = ImageCompression(self.max_compression)

    def __call__(self, video, target):
        # Compression augmentation only applies for Siamese Training
        if not isinstance(video, (list, tuple)) or self.max_compression == 0.0:
            return video, target

        idx = random.choice((0, 1))
        new_video = []
        new_target = []
        for i, (image, image_target) in enumerate(zip(video, target)):
            if i == idx:
                image = self.compression_func(image)
            new_video.append(image)
            new_target.append(image_target)

        return new_video, new_target

class SiamVideoNormalize(object):
    def __init__(self, mean, std, to_bgr255=True):
        self.mean = np.array(mean)
        self.std = np.array(std)
        self.to_bgr255 = to_bgr255

    def __call__(self, video, target, transform_=None):
        if not isinstance(video, (list, tuple)):
            video = np.array(video, dtype=np.float32)
            mean = np.float64(self.mean.reshape(1, -1))  # [[123.675 116.28 103.53]]
            stdinv = 1 / np.float64(self.std.reshape(1, -1))  # [[0.01712475 0.017507   0.01742919]]
            if self.to_bgr255:
                cv2.cvtColor(video, cv2.COLOR_BGR2RGB, video)
            cv2.subtract(video, mean, video)  # inplace
            cv2.multiply(video, stdinv, video)
            return video, target

        new_video = []
        new_target = []
        for i, (image, image_target) in enumerate(zip(video, target)):
            image = np.array(image, dtype=np.float32)
            mean = np.float64(self.mean.reshape(1, -1))
            stdinv = 1 / np.float64(self.std.reshape(1, -1))
            if self.to_bgr255:
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
            cv2.subtract(image, mean, image)
            cv2.multiply(image, stdinv, image)
            new_video.append(image)
            new_target.append(image_target)

        return new_video, new_target