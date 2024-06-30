import json
import os

from icvlp import ICVLP, Video, Plate


class DatasetCounter:
    def __init__(self, dataset_path: str):
        here = os.path.dirname(__file__)
        self.dataset_path = os.path.join(here, dataset_path)
        self.dataset = ICVLP.from_json(self.dataset_path)

        self.video_count: int = 0
        self.plate_count: int = 0
        self.distinct_plates: list[str] = []
        self.vehicle_type_count: dict[str, int] = {}
        self.frames_count: int = 0

    def count(self):
        for video in self.dataset.videos:
            video: Video
            self.video_count += 1
            for plate in video.plates:
                plate: Plate
                self.plate_count += 1
                if plate.label not in self.distinct_plates:
                    self.distinct_plates.append(plate.label)
                    self.vehicle_type_count[plate.vehicle_type] = self.vehicle_type_count.get(plate.vehicle_type, 0) + 1
                for _ in plate.frames:
                    self.frames_count += 1

    def print(self):
        print(f'Number of videos: {self.video_count}')
        print(f'Number of plates: {self.plate_count}')
        print(f'Number of distinct plates: {len(self.distinct_plates)}')
        print(f'Number of frames: {self.frames_count}')
        print(f'Number of vehicles by type: {json.dumps(self.vehicle_type_count, indent=2)}')


if __name__ == '__main__':
    counter = DatasetCounter('../icvlp_v0.1.json')
    counter.count()
    counter.print()
