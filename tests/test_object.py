from unittest import TestCase

from icvlp import Frame, Plate, Video


class BaseTestCase(TestCase):
    def setUp(self):
        self.video = Video(
            video_id="0001",
            source="Example",
            url="https://example.id",
            plates=[]
        )

        self.videos = [
            Video(
                video_id="9999",
                source="Example",
                url="https://example.com",
                plates=[]
            ),
            Video(
                video_id="9998",
                source="Example",
                url="https://example.org",
                plates=[]
            )
        ]

        self.plate = Plate(
            label="N123XYZ",
            frame_start=1,
            frame_end=10,
            frames=[]
        )

        self.plates = [
            Plate(
                label="X123BCA",
                frame_start=1000,
                frame_end=2000,
                frames=[]
            ),
            Plate(
                label="Y321ABC",
                frame_start=2000,
                frame_end=3000,
                frames=[]
            )
        ]

        self.frames = [
            Frame(
                frame=1000,
                bbox=[1, 1, 90, 90]
            ),
            Frame(
                frame=2001,
                bbox=[1, 1, 200, 200]
            )
        ]


class TestFrame(TestCase):
    def test_bbox_shape(self):
        with self.assertRaises(ValueError):
            Frame(frame=10, bbox=[1, 200])

    def test_bbox_type(self):
        frame = Frame(frame=10, bbox=["1", 1.2, 200, 200])
        assert frame.bbox == [1, 1, 200, 200]

        with self.assertRaises(TypeError):
            Frame(frame=10, bbox=["a string", 1, 200, 200])

    def test_bbox_coordinates(self):
        with self.assertRaises(ValueError):
            Frame(frame=10, bbox=[200, 200, 100, 100])


class TestPlate(BaseTestCase):
    def test_can_append_frame(self):
        for frame in self.frames:
            self.plate.append(frame)
            assert self.plate.frames[0] == self.frames[0]
            assert self.plate.frames[-1] == frame
            assert isinstance(self.plate.frames[-1], Frame)

    def test_can_extend_frames(self):
        self.plate.extend(self.frames)
        assert self.plate.frames == self.frames
        for frame in self.plate.frames:
            assert isinstance(frame, Frame)

    def test_can_only_append_frame(self):
        with self.assertRaises(TypeError):
            self.plate.append(self.videos[0])
        with self.assertRaises(TypeError):
            self.plate.append(self.plates[0])

    def test_can_only_extend_frames(self):
        with self.assertRaises(TypeError):
            self.plate.extend(self.videos)
        with self.assertRaises(TypeError):
            self.plate.extend(self.plates)


class TestVideo(BaseTestCase):
    def test_can_append_plate(self):
        for plate in self.plates:
            self.video.append(plate)
            assert self.video.plates[0] == self.plates[0]
            assert self.video.plates[-1] == plate
            assert isinstance(self.video.plates[-1], Plate)

    def test_can_extend_plates(self):
        self.video.extend(self.plates)
        assert self.video.plates == self.plates

    def test_can_only_append_plate(self):
        with self.assertRaises(TypeError):
            self.video.append(self.videos[0])
        with self.assertRaises(TypeError):
            self.video.append(self.frames[0])

    def test_can_only_extend_plates(self):
        with self.assertRaises(TypeError):
            self.video.extend(self.videos)
        with self.assertRaises(TypeError):
            self.video.extend(self.frames)
