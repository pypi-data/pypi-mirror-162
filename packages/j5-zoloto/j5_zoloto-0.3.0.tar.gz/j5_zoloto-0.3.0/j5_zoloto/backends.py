"""Backends for using Zoloto."""
from pathlib import Path
from typing import Generator, List, Optional, Set, Tuple, Type, Union

from j5.backends import Backend
from j5.boards import Board
from numpy import ndarray
from zoloto import __version__ as zoloto_version
from zoloto.calibration import parse_calibration_file
from zoloto.cameras.camera import Camera, find_camera_ids
from zoloto.marker import EagerMarker, Marker, UncalibratedMarker
from zoloto.marker_type import MarkerType

from j5_zoloto.board import ZolotoCameraBoard

from .component import MarkerCameraInterface


class ZolotoHardwareBackend(MarkerCameraInterface, Backend):
    """A Zoloto Hardware backend."""

    board = ZolotoCameraBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        return {
            ZolotoCameraBoard(
                str(camera_id),
                cls(camera_id),
            )
            for camera_id in find_camera_ids()
        }

    def __init__(self, camera_id: int) -> None:
        calibration_file = self.get_calibration_file()
        resolution: Optional[Tuple[int, int]] = (
            parse_calibration_file(calibration_file).resolution
            if calibration_file is not None
            else None
        )
        self._zcam = self.camera_class(
            camera_id,
            marker_type=self.marker_type,
            calibration_file=calibration_file,
            marker_size=self.marker_size,
            resolution=resolution,
        )

    @classmethod
    @property
    def camera_class(cls) -> Type[Camera]:
        """The camera class to use."""
        return Camera

    @classmethod
    @property
    def marker_type(self) -> MarkerType:
        """The type of markers to use."""
        return MarkerType.APRILTAG_36H11

    @classmethod
    @property
    def marker_size(self) -> int:
        """The static size of a marker."""
        return 250

    def get_calibration_file(self) -> Optional[Path]:
        """Get the calibration file."""
        return None

    def process_frame(
        self,
        identifier: int,
    ) -> Generator[Union[UncalibratedMarker, Marker], None, None]:
        """
        Get markers that the camera can see.

        :param identifier: Camera identifier, ignored.
        """
        return self._zcam.process_frame()

    def process_frame_eager(self, identifier: int) -> Generator[EagerMarker, None, None]:
        """
        Get markers that the camera can see.

        :param identifier: Camera identifier, ignored.
        """
        return self._zcam.process_frame_eager()

    def save_annotated_image(self, identifier: int, file: Path) -> None:
        """
        Save an annotated image to a file.

        :param identifier: Camera identifier, ignored.
        """
        self._zcam.save_frame(file, annotate=True)

    def get_visible_markers(self, identifier: int) -> List[int]:
        """
        Get a list of visible marker IDs.

        :param identifier: Camera identifier, ignored.
        :returns: List of marker IDs that were visible.
        """
        return self._zcam.get_visible_markers()

    def capture_frame(self) -> ndarray:
        """
        Get the raw image data from the camera.

        :returns: Camera pixel data
        """
        return self._zcam.capture_frame()

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return f"Zoloto v{zoloto_version}"

    def close_camera(self, identifier: int) -> None:
        """Close the camera object."""
        self._zcam.close()
