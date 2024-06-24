import json
import os
from unittest import TestCase

from icvlp import Frame, Plate, Video, ICVLP


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

        self.frames1 = [
            Frame(
                frame=2,
                bbox=[1, 1, 90, 90]
            ),
            Frame(
                frame=4,
                bbox=[1, 1, 90, 90]
            ),
        ]

        self.frames2 = [
            Frame(
                frame=2000,
                bbox=[1, 1, 200, 200]
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
        self.assertEqual(frame.bbox, [1, 1, 200, 200])

        with self.assertRaises(TypeError):
            Frame(frame=10, bbox=["a string", 1, 200, 200])

    def test_bbox_coordinates(self):
        with self.assertRaises(ValueError):
            Frame(frame=10, bbox=[200, 200, 100, 100])


class TestPlate(BaseTestCase):
    def test_can_append_frame(self):
        for frame in self.frames1:
            self.plate.append(frame)
            self.assertEqual(self.plate.frames[0], self.frames1[0])
            self.assertEqual(self.plate.frames[-1], frame)
            self.assertIsInstance(self.plate.frames[-1], Frame)

    def test_can_extend_frames(self):
        self.plate.extend(self.frames1)
        self.assertEqual(self.plate.frames, self.frames1)
        for frame in self.plate.frames:
            self.assertIsInstance(frame, Frame)

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

    def test_frame_out_of_bounds(self):
        with self.assertRaises(ValueError):
            self.plate.append(self.frames2[0])
        with self.assertRaises(ValueError):
            self.plate.extend(self.frames2)


class TestVideo(BaseTestCase):
    def test_can_append_plate(self):
        for plate in self.plates:
            self.video.append(plate)
            self.assertEqual(self.video.plates[0], self.plates[0])
            self.assertEqual(self.video.plates[-1], plate)
            self.assertIsInstance(self.video.plates[-1], Plate)

    def test_can_extend_plates(self):
        self.video.extend(self.plates)
        self.assertEqual(self.video.plates, self.plates)

    def test_can_only_append_plate(self):
        with self.assertRaises(TypeError):
            self.video.append(self.videos[0])
        with self.assertRaises(TypeError):
            self.video.append(self.frames1[0])

    def test_can_only_extend_plates(self):
        with self.assertRaises(TypeError):
            self.video.extend(self.videos)
        with self.assertRaises(TypeError):
            self.video.extend(self.frames1)


class TestICVLP(BaseTestCase):
    def setUp(self):
        super().setUp()
        dirname = os.path.dirname(__file__)
        dirname = os.path.dirname(dirname)
        test_filename = os.path.join(dirname, 'test.json')

        with open(test_filename, 'r') as f:
            self.test_data = json.load(f)
            f.close()

        self.icvlp = ICVLP.from_json(test_filename)

    def test_can_dump_json_string(self):
        self.assertEqual(self.icvlp.to_json(), json.dumps(self.test_data, indent=2))

    def test_can_append_video(self):
        self.icvlp.append(self.video)
        self.assertEqual(self.icvlp.videos[-1], self.video)

    def test_can_only_append_video(self):
        with self.assertRaises(TypeError):
            self.icvlp.append(self.plate)
        with self.assertRaises(TypeError):
            self.icvlp.append(self.frames1[0])

    def test_can_extend_videos(self):
        videos_len = len(self.videos)
        self.icvlp.extend(self.videos)
        self.assertEqual(self.icvlp.videos[videos_len:], self.videos)

    def test_can_only_extend_videos(self):
        with self.assertRaises(TypeError):
            self.icvlp.extend(self.plates)
        with self.assertRaises(TypeError):
            self.icvlp.extend(self.frames1)
