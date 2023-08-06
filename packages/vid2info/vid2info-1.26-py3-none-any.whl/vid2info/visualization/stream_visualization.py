"""
This class implements the Stream Visualization. It will display the current stream of video that is being
processed with all the annotations of the current scene state.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""

import cv2
import numpy as np
from vid2info.state.scene_state import SceneState

from vid2info.visualization.config import DEFAULT_WINDOW_SIZE_HW, KEEP_ORIGINAL_ASPECT_RATIO, DEFAULT_WINDOW_NAME
from vid2info.visualization.overlay_utils import overlay_annotations


class StreamVisualization:
    def __init__(self, window_size_hw: tuple[int, int] | list[int, int] | None = DEFAULT_WINDOW_SIZE_HW,
                 keep_original_aspect_ratio: bool = KEEP_ORIGINAL_ASPECT_RATIO,
                 window_name: str = DEFAULT_WINDOW_NAME):
        """
        Initialize the StreamVisualization. It will display the current stream of video that is being
        processed with all the annotations of the current scene state. You must use the show() method to
        display the stream and the update() method to update the visualization. You can also use "with",
        to automatically display it.

        Args:
            window_size_hw: tuple. The size of the window in (height, width). If keep_original_aspect_ratio is True,
                only one of the two dimensions will be used, and the other one will be calculated to keep the
                original aspect ratio of the input image.
            keep_original_aspect_ratio: bool. If True, the window will be resized to keep the original aspect ratio
                of the input image.
            window_name: str. The name of the window.
        """
        self.window_size_hw = window_size_hw
        self.keep_original_aspect_ratio = keep_original_aspect_ratio
        self.window_name = window_name

        # Create the cv2 window that we will be updating later
        cv2.namedWindow(winname=self.window_name, flags=cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(winname=self.window_name, x=0, y=0)
        cv2.setWindowTitle(winname=self.window_name, title=self.window_name)
        cv2.waitKey(delay=1)

    def update(self, image: np.ndarray, scene_state: SceneState, image_is_bgr = True) -> np.ndarray:
        """
        Update the visualization with the given image and scene state. And shows it in the window.

        Args:
            image: np.ndarray. The image to display.
            scene_state: SceneState. The scene state to display.
            image_is_bgr: bool. If True, the image is assumed to be in BGR format,
                otherwise it is assumed to be in RGB format.

        Returns:
            np.ndarray. The image that was displayed.

        Exceptions:
            InterruptedError: If the user pressed have closed the window.
        """
        assert image.ndim == 3, f"image must be 3D. Got: {image.shape}"
        assert image.shape[2] == 3, f"image must have 3 channels. Got: {image.shape}"
        assert type(scene_state) is SceneState, f"scene_state must be a SceneState. Got: {type(scene_state)}"

        if cv2.getWindowProperty(winname=self.window_name, prop_id=cv2.WND_PROP_VISIBLE) < 1:
            # Exit if the window is not visible
            raise InterruptedError("User has closed the visualization window")

        # Overlay the annotations on the image
        image = overlay_annotations(image=image, scene_state=scene_state, is_bgr=image_is_bgr)

        # Resize the image if necessary
        if self.window_size_hw is not None:
            image = self.resize_image(image=image, new_size_hw=self.window_size_hw)

        # Show it
        cv2.imshow(winname=self.window_name, mat=image)
        cv2.waitKey(delay=1)

        return image

    def resize_image(self, image : np.ndarray,
                     new_size_hw : tuple[int, int] | list[int, int] | np.ndarray) -> np.ndarray:
        """
        Resizes the image to self.window_size_hw, being aware of the keeping the original aspect ratio
        if self.keep_original_aspect_ratio is True.

        Args:
            image: np.ndarray. The image to resize.

        Returns:
            np.ndarray. The resized image.
        """
        assert type(new_size_hw) in (list, tuple, np.ndarray), f"new_size_hw must be a tuple or list." \
                                                               f" Got: {type(new_size_hw)}"
        assert len(new_size_hw) == 2, f"new_size_hw must be an iterable of length 2. Got: {len(new_size_hw)}"
        h, w = image.shape[:2]
        new_h, new_w = new_size_hw
        if self.keep_original_aspect_ratio:
            if h > w:
                new_w = int(new_h * w / h)
            else:
                new_h = int(new_w * h / w)
        if (h, w) != (new_h, new_w):
            image = cv2.resize(src=image, dsize=(new_w, new_h))
        return image

    def __enter__(self):
        """
        Enter the with block.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the with block.

        Args:
            exc_type: Exception. The type of the exception.
            exc_val: Exception. The value of the exception.
            exc_tb: Exception. The traceback of the exception.
        """
        if cv2.getWindowProperty(winname=self.window_name, prop_id=cv2.WND_PROP_VISIBLE) > 0:
            self.close()

    def close(self):
        """
        Close the window.
        """
        cv2.destroyWindow(winname=self.window_name)