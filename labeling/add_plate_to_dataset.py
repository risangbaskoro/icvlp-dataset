import os

from icvlp import ICVLP, Video, Plate


class PlateAdder:
    def __init__(self, dataset_path: str):
        here: str = os.path.dirname(__file__)
        self.dataset_path: str = os.path.join(here, dataset_path)
        self.dataset: ICVLP = ICVLP.from_json(self.dataset_path)
        self.target_video_id: str = str(input('Enter video id: '))
        self.target_video: Video = self.dataset.get_video_by_id(self.target_video_id)
        if self.target_video is None:
            raise ValueError(f"Video with ID {self.target_video_id} not found in dataset.")

        continue_adding: bool = True
        while continue_adding:
            os.system('clear')
            self.add_plate()
            continue_adding: bool = input('Add another plate? (y/n) ').lower() == 'y'

    @property
    def vehicle_types(self):
        return [
            None,
            'single_axle',
            'bus',
            'box_truck',
            'semi_trailer',
            'pickup_truck',
            'minibus'
        ]

    def print_vehicle_types(self):
        for i, vehicle_type in enumerate(self.vehicle_types):
            print(f"{i}: {vehicle_type}")

    def add_plate(self):
        self.print_vehicle_types()
        label: str = str(input('Enter plate label: ')).upper()
        vehicle_type: str = self.vehicle_types[int(input('Enter vehicle type: '))]
        frame_start: int = int(input('Enter frame start: '))
        frame_end: int = int(input('Enter frame end: '))
        plate: Plate = Plate(
            label=label,
            vehicle_type=vehicle_type,
            frame_start=frame_start,
            frame_end=frame_end,
        )
        self.target_video.append(plate)
        self.save()

    def save(self):
        with open(self.dataset_path, 'w') as f:
            f.write(self.dataset.to_json())


if __name__ == '__main__':
    adder = PlateAdder('../icvlp_v0.1.json')
