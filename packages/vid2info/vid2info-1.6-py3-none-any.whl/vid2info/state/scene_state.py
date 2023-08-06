"""
This class implements the state of a concrete frame.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""

from src.state.element_state import ElementState

from time import time
import numpy as np
from src.inference.utils import crop_bbox_from_image
from src.inference.config import BBOX_XYXY, SEGMENTATION_MASK

crop_img_if_given = lambda img, bbox, copy = True: crop_bbox_from_image(image=img, bbox_xyxy=bbox, is_normalized=True, copy=copy) \
                                        if img is not None else None

class SceneState:
    def __init__(self, tracker_out : dict, get_first_element_time_stamp: callable = lambda track_id : None,
                 frame: np.ndarray | None = None, segmentation_mask : dict | None = None,
                 save_full_segmentation_mask : bool = False):
        """
        Initialize the SceneState. It is used for defining the current scene, and will contain the
        state of each individual element in the scene.

        :param tracker_out: dictionary. The output of the tracker. It is the dictionary outputted by
                get_track_ids when return_as_dict is True. It's keys are the track_ids and the values are
                dictionaries with, at least, the following keys: ('bbox_xyxy', 'confidence', 'class_id', 'track_length')
        :param get_first_element_time_stamp: callable. A function that returns the first_timestamp of the first
                detection of the element with the given track_id in the buffer or the current timestamp if the
                element is not in the buffer.
        :param frame: np.ndarray or None. The frame of the scene. If given, it will save a cropped subimage for
                each detected element.
        :param segmentation_mask: dict or None. The segmentation mask of the scene, embedded within a dictionary
                with the following keys: ('segmentation_mask', 'background_class_idx', 'class_names_list'). If given,
                it will save a cropped subimage for each detected element.

        :param save_full_segmentation_mask: bool. If True, it will save the full segmentation mask of the scene.
        """

        self.elements = {track_id :
                             ElementState(element_tracker_info=element,
                                          first_detection_timestamp=get_first_element_time_stamp(track_id=track_id),
                                          element_img=crop_img_if_given(img=frame, bbox=element[BBOX_XYXY], copy=True),
                                          element_segmentation_mask=crop_segmentation_mask(segmentation_mask=segmentation_mask,
                                                                                           bbox=element[BBOX_XYXY],
                                                                                           copy=not save_full_segmentation_mask)
                                                                    if segmentation_mask is not None else None)
                         for track_id, element in tracker_out.items()}
        self.timestamp = time()
        self.segmentation_mask = segmentation_mask if save_full_segmentation_mask else None

    def __len__(self):
        return len(self.elements)

    def get_elements_age_in_seconds(self) -> dict:
        """
        Returns the age of each element in the scene in seconds.

        :return dict. The age of each element in the scene. The keys are the track_ids and
                        the values are the age in seconds.
        """
        return {track_id : self.elements[track_id].age_in_seconds for track_id in self.elements}

    def get_element_counts(self) -> dict:
        """
        Returns the number of elements in the scene for each class.

            Returns:
                dict. The number of elements in the scene for each class. The keys are the class names and
                the values are the number of elements in the scene for that class.
            """
        classes_list = [element.class_name for element in self.elements.values()]
        return {class_name : classes_list.count(class_name) for class_name in set(classes_list)}

def crop_segmentation_mask(segmentation_mask: dict,
                           bbox: np.ndarray | list[int|float, int|float, int|float, int|float] |
                                 tuple[int|float, int|float, int|float, int|float],
                           copy: bool = True) -> dict:
    """
    Crops the segmentation mask to the given bounding box.

    :param segmentation_mask: dict. The segmentation mask of the scene. Contains the following keys:
            ('segmentation_mask', 'background_class_idx', 'class_names_list').
    :param bbox: np.ndarray or iterable with 4 ints or floats. The bounding box of the subimage to be cropped.
    :param copy: bool. If True, the returned segmentation mask will be copied.

    :return dict. The input dictionary but with the segmentation mask cropped to the given bounding box.
    """
    assert type(segmentation_mask) is dict, f"The segmentation mask must be a dictionary. Got {type(segmentation_mask)}."
    seg_mask = segmentation_mask[SEGMENTATION_MASK]
    assert type(seg_mask) is np.ndarray, f"The segmentation mask must be a numpy array. Got {type(seg_mask)}."
    assert len(bbox) == 4, f"The bounding box must be a list or tuple of length 4. Got {len(bbox)}."

    mask = crop_bbox_from_image(image=seg_mask, bbox_xyxy=bbox, is_normalized=True, copy=copy)

    return {**segmentation_mask, SEGMENTATION_MASK: mask}

