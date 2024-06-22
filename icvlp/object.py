import json
from typing import TypeVar

T = TypeVar('T', bound="DataObject")


class DataObject:
    children_type: T
    children: list[T]

    def __init__(self, children: list[T]):
        self.children = [self.children_type.__init__(child) for child in children] if children else []

    def as_dict(self) -> dict:
        r""" Returns the object as a dictionary

        Returns:
            dict: The object as a dictionary
        """
        ret = {}
        for key, value in self.__dict__.items():
            if key == "children":
                continue
            if isinstance(value, list):
                ret[key] = [v.as_dict() if isinstance(v, DataObject) else v for v in value]
            else:
                ret[key] = value
        return ret

    def append(self, item: T):
        if self.children_type is not None and not isinstance(type(item), type(self.children_type)):
            raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        self.children.append(item)
        return self

    def extend(self, other: list[T]):
        for item in other:
            if self.children_type is not None and not isinstance(type(item), type(self.children_type)):
                raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        self.children.extend(other)
        return self


class Frame(DataObject):
    r""" Data object of a video frame with bounding box.

    Arguments:
        frame (int): Frame number of the video.
        bbox (list): Bounding box of the frame. Configured in [``x_min``, ``y_min``, ``x_max``, ``y_max``].
    """
    children_type = None

    frame: int
    bbox: list[int]

    def __init__(self, frame: int = None, bbox: list[int] = None):
        super().__init__([])
        self.frame: int = frame
        self.__check_bbox(bbox)
        self.bbox: list[int] = bbox

    @staticmethod
    def __check_bbox(bbox: list[int]):
        if len(bbox) != 4:
            raise ValueError(f"bbox must be length 4. Got {len(bbox)}.")
        for i, x in enumerate(bbox):
            try:
                bbox[i] = int(x)
            except Exception:
                raise TypeError(f"Item in bbox must be of type {int}. Got {type(x)}.")
        if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
            raise ValueError(f"bbox must be in shape (`x_min`, `y_min`, `x_max`, `y_max`). Got{bbox}.")


class Plate(DataObject):
    r""" Data object of a plate with labels and frames.

    Arguments:
        label (str): Label of the plate.
        vehicle_type (str): Type of the vehicle.
        frame_start (int): First occurred frame of the plate.
        frame_end (int): Second occurred frame of the plate.
        frames (List[Frame]): List of frames of the plate.
    """
    children_type = Frame

    label: str
    vehicle_type: str
    frame_start: int
    frame_end: int
    frames: list[children_type]

    def __init__(self,
                 label: str = None,
                 vehicle_type: str = None,
                 frame_start: int = None,
                 frame_end: int = None,
                 frames: list[Frame] = None):
        super().__init__(frames)
        self.label: str = label
        self.vehicle_type: str = vehicle_type
        self.frame_start: int = frame_start
        self.frame_end: int = frame_end
        self.frames = self.children

    def append(self, item: T):
        if not isinstance(item, self.children_type):
            raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        return super().append(item)

    def extend(self, other: list[T]):
        for item in other:
            if not isinstance(item, self.children_type):
                raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        return super().extend(other)


class Video(DataObject):
    r""" Data object of a video with its URL, source, and plates.

    Arguments:
        video_id (str): Unique video identifier.
        source (str): Owner or source of the video.
        url (str): URL of the video.
        fps (int): Frame to get per second when extracting frames from video.
        plates (List[Plate]): List of plates of the video.
    """
    children_type = Plate

    video_id: str
    source: str
    url: str
    fps: int
    plates: list[children_type]

    def __init__(self,
                 video_id: str = None,
                 source: str = None,
                 url: str = None,
                 fps: int = None,
                 plates: list[Plate] = None):
        super().__init__(plates or [])
        self.video_id = video_id
        self.source: str = source
        self.url: str = url
        self.fps: int = fps
        self.plates: list[Plate] = self.children

    def append(self, item: T):
        if not isinstance(item, self.children_type):
            raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        return super().append(item)

    def extend(self, other: list[T]):
        for item in other:
            if not isinstance(item, self.children_type):
                raise TypeError(f"Item must be of type {self.children_type}. Got {type(item)}.")
        return super().extend(other)


class ICVLP:
    r""" Indonesian Commercial Vehicle License Plate dataset.

    Collection of Videos that has license plates in their frames.
    """
    children_type = Video

    videos: list[children_type]

    def __init__(self, data):
        self.videos = [self.children_type(video) for video in data]
        self.children = self.videos

    def append(self, item: children_type):
        self.videos.append(item)
        return self

    def extend(self, other: list[children_type]):
        self.videos.extend(other)
        return self

    @classmethod
    def from_json(cls, json_filepath: str):
        r""" Populate videos with data from JSON file.

        Arguments:
            json_filepath (str): Path to JSON file.

        Returns:
            ICVLP
        """
        with open(json_filepath, 'r') as f:
            data = json.load(f)
        return cls(data)

    def to_json(self):
        return json.dumps([video.__dict__ for video in self.videos], indent=2)
