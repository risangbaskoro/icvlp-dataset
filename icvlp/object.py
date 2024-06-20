import json
from typing import List, TypeVar, Dict

T = TypeVar("T", bound="DataObject")


class ObjectWrapper:
    r""" Base class for all data objects
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, T]:
        r""" Converts the object to a dictionary.

        Returns:
            Dict[str, T]
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                result[key] = [v.to_dict() if isinstance(v, ObjectWrapper) else v for v in value]
            else:
                result[key] = value.to_dict() if isinstance(value, ObjectWrapper) else value
        return result

    def __repr__(self):
        class_name = self.__class__.__name__
        attributes = ', '.join(f"{key}={getattr(self, key)}" for key in self.__dict__)
        return f"{class_name}({attributes})"

    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __delattr__(self, item):
        try:
            del self.__dict__[item]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


class Frame(ObjectWrapper):
    r""" Data object of a video frame with bounding box.

    Arguments:
        frame (str): Frame number of the video.
        bbox (list): Bounding box of the frame. Configured in [``x_min``, ``y_min``, ``x_max``, ``y_max``].
    """

    def __init__(self, frame: str, bbox: List[int]):
        super().__init__(frame=frame, bbox=bbox)


class Plate(ObjectWrapper):
    r""" Data object of a plate with labels and frames.

    Arguments:
        label (str): Label of the plate.
        frame_start (int): First occurred frame of the plate.
        frame_end (int): Second occurred frame of the plate.
        frames (List[Frame]): List of frames of the plate.
    """

    def __init__(self, label: str, frame_start: int, frame_end: int, frames: List[T]):
        super().__init__(label=label, frame_start=frame_start, frame_end=frame_end,
                         frames=[Frame(**frame) for frame in frames])

    def add_frames(self, frames: List[Frame]) -> None:
        r""" Adds frames to the plate.

        Arguments:
            frames (List[Frame]): List of frames of the plate.
        """
        for frame in frames:
            assert self.frame_start <= frame.frame <= self.frame_end, \
                f"Frame should be between {self.frame_start} and {self.frame_end}. Got {frame.frame}"
        self.frames.extend(frames)


class Video(ObjectWrapper):
    r""" Data object of a video with its URL, source, and plates.

    Arguments:
        video_id (str): Unique video identifier.
        source (str): Owner or source of the video.
        url (str): URL of the video.
        fps (int): Frame to get per second when extracting frames from video.
        plates (List[Plate]): List of plates of the video.
    """

    def __init__(self, video_id: str, source: str, url: str, fps: int, plates: List[T]):
        super().__init__(video_id=video_id, source=source, url=url, fps=fps,
                         plates=[Plate(**plate) for plate in plates])

    def add_plates(self, plates: List[Plate]) -> None:
        r""" Adds plates to the video.
        Arguments:
            plates (List[Plate]): List of plates of the video.
        """
        self.plates.extend(plates)

    def get_frames(self) -> List[Frame]:
        r""" Gets frames of the video.
        """
        all_frames = []
        for plate in self.plates:
            all_frames.extend(plate.frames)
        return all_frames


class ICVLP(ObjectWrapper):
    r""" Indonesian Commercial Vehicle License Plate dataset.

    This object holds data of Videos, Plates, and Frames.

    Arguments:
        videos (List[Video]): List of videos.
    """

    def __init__(self, videos: List[T]):
        super().__init__(videos=[Video(**video_data) for video_data in videos])

    @classmethod
    def from_json(cls, json_filepath: str):
        r""" Populate videos with data from json file.

        Arguments:
            json_filepath (str): Path to json file.

        Returns:
            ICVLP
        """
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        return cls(data)

    def to_dict(self) -> List[T]:
        r""" Converts the object to a dictionary.

        Returns:
            List[Dict[str, T]]
        """
        return [video.to_dict() for video in self.videos]

    def to_json(self) -> str:
        r""" Serializes data to JSON formatted string.

        Returns:
            str
        """
        return json.dumps(self.to_dict(), indent=2)

    def save(self, filepath: str, indent: int = 2) -> None:
        r""" Saves the object to a JSON file.

        Arguments:
            filepath (str): Path to json file.
            indent (int): Indentation level of the JSON file.
        """
        json.dump(self.to_dict(), open(filepath, 'w'), indent=indent)
