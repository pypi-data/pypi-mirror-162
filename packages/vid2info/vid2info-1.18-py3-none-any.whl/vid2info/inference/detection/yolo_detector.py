"""
This class implements the YoloDetector. It is used to detect elements in a
given image or batch of images. It uses YOLOv6 as the backbone of the detector.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 09-07-2022
"""

import numpy as np

from vid2info.inference.detection.config import WEIGTHS_PATH, DETECTOR_MIN_CONFIDENCE_TH, IOU_NMS_TH, \
    MAX_DETECTIONS_PER_IMAGE, DETECTOR_IMAGE_SIZE, HALF_MODE, DATASET_YML, NORMALIZE_OUTPUT, DEFAULT_MAX_CLASSES
from vid2info.inference.config import INFERENCE_DEVICE, XMIN, YMIN, YMAX, XMAX, CONFIDENCE, CLASS_ID, CLASS_NAME, BBOX_XYXY, \
    UINT8_TO_FLOAT
from vid2info.inference.utils import raw_yolo_bboxes_to_xyxy_co_cl
from yolov6.layers.common import DetectBackend

from yolov6.data.data_augment import letterbox
from yolov6.utils.nms import non_max_suppression

import os
import torch
import math
from warnings import warn

class YoloDetector:
    def __init__(self, weights : str = WEIGTHS_PATH, dataset_yml : str | None = DATASET_YML,
                 confidence_th : float = DETECTOR_MIN_CONFIDENCE_TH, nms_th : float = IOU_NMS_TH,
                 max_dets : int = MAX_DETECTIONS_PER_IMAGE, inference_device : str = INFERENCE_DEVICE,
                 image_size : int = DETECTOR_IMAGE_SIZE, half_mode = HALF_MODE):

        """
        Initialize the YoloDetector.
        """
        assert os.path.isfile(weights), f'Weights file {weights} not found.'
        if inference_device.startswith('cuda'):
            assert torch.cuda.is_available(), 'CUDA is not available.'
        else:
            assert inference_device == 'cpu', f'Inference device must be cpu or cuda. Got {inference_device}.'
            assert half_mode is False, f'Half mode must be False for CPU inference.'

        if dataset_yml is not None:
            assert os.path.isfile(dataset_yml), f'Dataset yml file {dataset_yml} not found.'
            from yolov6.utils.events import load_yaml
            self.dataset_info = load_yaml(dataset_yml)
            self.class_names = self.dataset_info['names']
        else:
            self.dataset_info, self.class_names = None, [None] * DEFAULT_MAX_CLASSES

        self.confidence_th = confidence_th
        self.nms_th = nms_th
        self.max_dets = max_dets
        self.image_size = image_size
        self.half_mode = half_mode
        self.inference_device = torch.device(inference_device)
        self.half = half_mode
        self.model = DetectBackend(weights=weights, device=self.inference_device).eval()
        # Warm the model up (Don't set in self to let the garbage collector free the memory)
        input_sample = torch.zeros(1, len('RGB'), self.image_size, self.image_size, dtype=torch.float32, device=self.inference_device)
        self.model(input_sample)
        if self.half:
            self.model = self.model.half()
        self.stride = self.model.stride

        self.image_size = self.check_img_size(self.image_size, s=self.stride)  # check image size

    def detect(self, image : np.ndarray, input_is_bgr : bool = False, classes_to_keep : None | list[int] | tuple[int] = None,
               return_as_dict : bool = False, return_normalized : bool = NORMALIZE_OUTPUT,
               return_all_below_th : float = 0.) -> list[dict] | np.ndarray:
        """
        Detect objects in a given image.
        NOTE: 99.99...% of the time, this function takes is spent in the inference. The unique way to
        make it faster is to batch images or, ideally, to use a GPU.
        :param image: Numpy.ndarray of shape (H, W, C). The image to detect objects in.
        :param input_is_bgr: Boolean. Whether the input image is in BGR format or not (RGB).
        :param classes_to_keep: List of integers. The classes to keep in the output.
        :return: Numpy.ndarray of shape (N, 6) or List of Dictionaries. The detected objects.
        """
        image = self.preprocess_image(image=image, input_is_bgr=input_is_bgr)
        input_h, input_w = image.shape[-2:]
        if image.ndim == 3:
            image = image[None]
        assert image.ndim == 4, f'Image must be 4D. Got {image.shape}.'
        # Predictions here are in the format (x_center, y_center, width, height, confidence, class_id)
        pred = self.model(image, val=True)
        below_th = []
        # Keeping classes below the confidence threshold could help the tracker.
        if return_all_below_th > 0.:
            below_th = pred[pred[..., 4] < return_all_below_th]
            below_th = raw_yolo_bboxes_to_xyxy_co_cl(preds=below_th)

        pred = non_max_suppression(prediction=pred, conf_thres=self.confidence_th, iou_thres=self.nms_th,
                                   classes=classes_to_keep, agnostic=False, multi_label=False, max_det=self.max_dets)
        if len(below_th) > 0:
            pred = (torch.cat((pred[0], below_th), dim=0),)
        assert len(pred) == 1, f'Expected 1 prediction. Got {len(pred)}.'
        pred = self.post_process_output_detection(prediction=pred[0], input_h=input_h, input_w=input_w,
                                                  as_dict=return_as_dict, normalize=return_normalized)
        return pred

    def post_process_output_detection(self, prediction : torch.Tensor, input_h : int, input_w : int,
                                      normalize : bool = True, as_dict : bool = False) -> list[dict] | np.ndarray:
        """
        Postprocess the output of the detector. Return a dictionary with the detected objects.

        :param prediction: List of tensors. The output of the detector.
        :param input_h: Integer. The height of the input image.
        :param input_w: Integer. The width of the input image.
        :param as_dict: Boolean. Whether to return the output as a dictionary or not.
        :return: List of Dictionaries or numpy.ndarray. The detected objects.
        As a dictionary, the keys are  ('xmin', 'ymin', 'xmax', 'ymax', 'class_id', 'class_name', 'confidence',
                                        'bbox_xyxy').
        As a numpy.ndarray, the shape is (N, 6). The columns are: (xmin, ymin, xmax, ymax, confidence, class_id).
        If normalize, all coordinates are in the range [0., 1.]
        """

        if normalize:
            # Convert from the bbox from (w1, h1, w2, h2) to the range [0., 1.] (w'1, h'1, w'2, h'2).
            prediction[:, [0, 2]] /= input_w
            prediction[:, [1, 3]] /= input_h
        if as_dict:
            prediction = prediction.tolist()
            prediction = [{XMIN: xmin, YMIN: ymin, XMAX: xmax, YMAX: ymax,
                           BBOX_XYXY: (xmin, ymin, xmax, ymax), CONFIDENCE: confidence,
                           CLASS_ID: int(class_id), CLASS_NAME: self.class_names[int(class_id)]}
                          for (xmin, ymin, xmax, ymax, confidence, class_id) in prediction]
        else:
            if self.inference_device.type != 'cpu':
                prediction = prediction.detach().cpu()
            prediction = prediction.numpy()

        return prediction

    def preprocess_image(self, image: np.ndarray, input_is_bgr = False) -> torch.Tensor:
        '''Process image before image inference.'''
        assert image.dtype == np.uint8, f'Image must be uint8. Got {image.dtype}.'
        assert image.ndim == 3, f'Image must be 3D. Got {image.shape}.'
        assert image.shape[2] == 3, f'Image must have 3 channels (Format HWC). Got {image.shape}.'

        image = letterbox(image, new_shape=self.image_size, stride=self.stride)[0]

        # Convert
        image = image.transpose((2, 0, 1))  # HWC to CHW
        if input_is_bgr:
            # BGR to RGB
            image = image[::-1, ...]
        image = torch.tensor(np.ascontiguousarray(image), device=self.inference_device,
                             dtype=torch.float16 if self.half else torch.float32).to(self.inference_device)
        image *= UINT8_TO_FLOAT  # 0 - 255 to 0.0 - 1.0
        return image

    def check_img_size(self, image_size, s=32, floor=0):
        def make_divisible(x, divisor):
            # Upward revision the value x to make it evenly divisible by the divisor.
            return math.ceil(x / divisor) * divisor
        """Make sure image size is a multiple of stride s in each dimension, and return a new shape list of image."""
        if isinstance(image_size, int):  # integer i.e. img_size=640
            new_size = max(make_divisible(image_size, int(s)), floor)
        elif isinstance(image_size, list) or isinstance(image_size, tuple):  # list i.e. img_size=[640, 480]
            new_size = [max(make_divisible(x, int(s)), floor) for x in image_size]
        else:
            raise Exception(f"Unsupported type of img_size: {type(image_size)}")

        if new_size != image_size:
            warn(f'image_size {image_size} must be multiple of max stride {s}, updating to {new_size}')
        return new_size if isinstance(image_size, list) else [new_size] * 2