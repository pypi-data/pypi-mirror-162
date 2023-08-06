"""
This class implements the state of a single element on a concrete time step.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""

from vid2info.inference.config import CONFIDENCE, CLASS_ID, CLASS_NAME, BBOX_XYXY, SEGMENTATION_MASK, CLASS_NAMES_LIST, \
    BACKGROUND_CLASS_IDX
from vid2info.inference.tracking.tracker import TRACK_LENGTH

from time import time
import numpy as np

MANDATORY_ELEMENT_KEYS = (BBOX_XYXY, CONFIDENCE, CLASS_ID, TRACK_LENGTH)

class ElementState:
    def __init__(self, element_tracker_info : dict, first_detection_timestamp : float | None = None,
                 element_img : np.ndarray | None = None, element_segmentation_mask : dict | None = None):
        """
        Initialize the State of an element.

        :param element_tracker_info: dictionary. The information of the element, outputed from the tracker.
        :param first_detection_timestamp: float or None. If given, it is the timestamp of the first detection of this
                element.
        :param element_img: np.ndarray or None. If given, it is the cropped image of the element.
        :param element_segmentation_mask: dict or None. If given, it is the dictionary containing the cropped
                                          segmentation mask of the element and the segmenter meta-information.
                                          It contains the following keys: ('segmentation_mask', 'background_class_idx',
                                            'class_names_list').
        """
        assert all(key in element_tracker_info for key in MANDATORY_ELEMENT_KEYS), f"element_tracker_info must contain the following " \
                                                                           f"keys: {MANDATORY_ELEMENT_KEYS}. " \
                                                                           f"Got: {tuple(element_tracker_info.keys())}"

        assert type(first_detection_timestamp) is float, f"first_detection_timestamp must be a float. " \
                                                         f"It is {type(first_detection_timestamp)}"

        if element_img is not None and element_segmentation_mask is not None:
            assert element_img.shape[:2] == element_segmentation_mask[SEGMENTATION_MASK].shape[:2], \
                f"cropped_img and cropped_segmentation_mask must have the same height and width if given. " \
                f"Got: {element_img.shape[:2]} and {element_segmentation_mask[SEGMENTATION_MASK].shape[:2]}"

        current_time = time()
        assert current_time >= first_detection_timestamp, f"current time must be greater than or equal to first_detection_timestamp." \
                                                          f" But current_time is  {current_time} and first_detection_timestamp is " \
                                                          f"{first_detection_timestamp}"

        self.bbox_xyxy = element_tracker_info[BBOX_XYXY]
        self.confidence = element_tracker_info[CONFIDENCE]
        self.class_name = element_tracker_info[CLASS_NAME] if CLASS_NAME in element_tracker_info else \
            str(element_tracker_info[CLASS_ID])
        self.track_length = element_tracker_info[TRACK_LENGTH]
        self.first_detection_timestamp = first_detection_timestamp
        self.age_in_seconds = current_time - self.first_detection_timestamp
        self.element_img = element_img
        if element_segmentation_mask is not None:
            self.element_segmentation_mask = element_segmentation_mask[SEGMENTATION_MASK]
            self.segmentation_class_names = element_segmentation_mask[CLASS_NAMES_LIST]
            self.segmentation_background_class_idx = element_segmentation_mask[BACKGROUND_CLASS_IDX]
            if element_img is not None:
                assert self.element_segmentation_mask.shape == element_img.shape[:2], \
                    f"element_segmentation_mask and element_img must have the same height and width. " \
                    f"Got: {self.element_segmentation_mask.shape[:2]} and {element_img.shape[:2]}"
        else:
            self.element_segmentation_mask = None
            self.segmentation_class_names, self.segmentation_background_class_idx = None, None
