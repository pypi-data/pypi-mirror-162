"""
This class implements a buffer containing a set of states. It will serve as interface with the
individual states.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 16-07-2022
"""

from collections import deque

import numpy as np

from vid2info.state.config import BUFFER_SIZE
from vid2info.state.scene_state import SceneState
from vid2info.state.element_state import ElementState
from time import time

class StateBuffer:
    def __init__(self, buffer_size : int = BUFFER_SIZE, running_online = False,
                 scene_state_class : type = SceneState, element_state_class : type = ElementState):
        """
        Initialize the StateBuffer. It is used for tracking the history of the last scene and
         element states.

        :param buffer_size: int. The size of the history buffer to keep.
        :param running_online: bool. If True, it will assume that the video is comming from an online stream
                like a webcam. So the timestamps of the states will update with the current time in every call.
                If False, it will assume that the video is coming from a pre-recorded file. So the timestamps
                will have to be served from the video.
        :param scene_state_class: type. The class of the scene state. It should be a subclass of SceneState.
        :param element_state_class: Class. The class of the element states. It should be a subclass of ElementState.
        """
        self.buffer_size = max(buffer_size, 1)
        self.buffer = deque(maxlen=self.buffer_size)
        self.running_online = running_online
        self.scene_state_class = scene_state_class
        self.element_state_class = element_state_class

    def state_from_tracker_out(self, tracker_out : dict, add_to_buffer : bool = True,
                               frame: np.ndarray | None = None,
                               segmentation_mask : dict | None = None) -> SceneState:
        """
        Create a new state from the tracker output.

        :param tracker_out: dictionary. The output of the tracker. It is the dictionary outputted by
                get_track_ids when return_as_dict is True. It's keys are the track_ids and the values are
                dictionaries with, at least, the following keys: ('bbox_xyxy', 'confidence', 'class_id', 'track_length')
        :param add_to_buffer: bool. If True, the state will be added to the buffer.
        :param frame: np.ndarray or None. The frame of the scene. If given, it will save a cropped subimage for
                each detected element.
        :param segmentation_mask: np.ndarray or None. The segmentation mask of the scene. If given, it will save a
                cropped segmentation mask for each detected element.
        :return: SceneState. The new state. If add_to_buffer was True it can be also found in the last element of the
                current self.buffer.
        """
        state = self.scene_state_class(tracker_out=tracker_out,
                           get_first_element_time_stamp=self.get_first_element_time_stamp,
                           frame=frame, segmentation_mask=segmentation_mask,
                           element_state_class=self.element_state_class)
        if add_to_buffer:
            self.buffer.append(state)
        return state


    def get_first_element_time_stamp(self, track_id : int) -> float | None:
        """
        Get the first_timestamp of the first detection of the element with the given track_id in the buffer
        or None if the element is not in the buffer.

        Args:
            track_id: int. The track_id of the element to get the first_timestamp of.
        """
        for scene_state in self.buffer:
            if track_id in scene_state.elements:
                return scene_state.elements[track_id].first_detection_timestamp
        if self.running_online:
            return time()
        else:
            raise NotImplementedError("Not implemented yet for the case where the video is not coming from an online stream.")


