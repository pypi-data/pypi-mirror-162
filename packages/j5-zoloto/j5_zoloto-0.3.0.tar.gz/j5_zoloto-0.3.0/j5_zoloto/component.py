"""Classes for Fiducial Marker Camera."""

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Generator, List, Type, Union

from j5.components.component import Component, Interface
from numpy import ndarray
from zoloto.marker import BaseMarker, EagerMarker, Marker, UncalibratedMarker

LOGGER = logging.getLogger(__name__)


class MarkerCameraInterface(Interface):
    """An interface containing the methods required for a marker camera."""

    @abstractmethod
    def process_frame(
        self,
        identifier: int,
    ) -> Generator[Union[UncalibratedMarker, Marker], None, None]:
        """
        Get markers that the camera can see.

        :param identifier: Camera identifier, ignored.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def process_frame_eager(self, identifier: int) -> Generator[EagerMarker, None, None]:
        """
        Get markers that the camera can see.

        :param identifier: Camera identifier, ignored.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def save_annotated_image(self, identifier: int, file: Path) -> None:
        """Save an annotated image to a file."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def get_visible_markers(self, identifier: int) -> List[int]:
        """
        Get a list of visible marker IDs.

        :param identifier: Camera identifier, ignored.
        :returns: List of marker IDs that were visible.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def capture_frame(self) -> ndarray:
        """
        Get the raw image data from the camera.

        :returns: Camera pixel data
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def close_camera(self, identifier: int) -> None:
        """Close the camera object."""
        raise NotImplementedError  # pragma: nocover


class MarkerCamera(Component):
    """
    Camera that can identify fiducial markers.

    Additionally, it will do pose estimation, along with some calibration
    in order to determine the spatial positon and orientation of the markers
    that it has detected.
    """

    def __init__(
            self,
            identifier: int,
            backend: MarkerCameraInterface,
    ) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[MarkerCameraInterface]:
        """Get the interface class that is required to use this component."""
        return MarkerCameraInterface

    @property
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        return self._identifier

    def see(self, *, eager: bool = True) -> List[BaseMarker]:
        """
        Capture an image and identify fiducial markers.

        :param eager: Process the pose estimations of markers immediately.
        :returns: list of markers that the camera could see.
        """
        if eager:
            return list(self._backend.process_frame_eager(self._identifier))
        else:
            return list(self._backend.process_frame(self._identifier))

    def see_ids(self) -> List[int]:
        """
        Capture an image and identify fiducial markers.

        This method does not perform pose estimation, so is faster than ``see``.

        :returns: A list of IDs for the markers that were visible.
        """
        return self._backend.get_visible_markers(self._identifier)

    def capture(self) -> ndarray:
        """
        Get the raw image data from the camera.

        :returns: Camera pixel data
        """
        return self._backend.capture_frame()

    def save(self, path: Union[Path, str]) -> None:
        """Save an annotated image to a path."""
        if isinstance(path, str):
            path = Path(path)
        if not path.suffix:
            LOGGER.info("Unable to save image without file extension, assuming .jpg")
            path = path.with_suffix(".jpg")
        self._backend.save_annotated_image(self._identifier, path)

    def close(self) -> None:
        """
        Close the camera.

        The camera will no longer work after this method is called.
        """
        self._backend.close_camera(self._identifier)
