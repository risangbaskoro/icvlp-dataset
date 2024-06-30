import os

import cv2

from icvlp import ICVLP, Plate, Video


class LabelVehicleTypes:
    def __init__(self,
                 dataset_path: str,
                 video_path: str,
                 skip_labelled: bool = False):
        here = os.path.dirname(__file__)
        self.dataset_path = os.path.join(here, dataset_path)
        self.video_path = os.path.join(here, video_path)

        self.dataset = ICVLP.from_json(self.dataset_path)

        self.skip_labelled_vehicle_type = skip_labelled

        self.vehicle_types = [
            None,
            'single_axle',
            'bus',
            'box_truck',
            'semi_trailer',
            'pickup_truck',
            'minibus'
        ]

    def _label_plate_vehicle_type(self, cap, plate: Plate):
        for i, vehicle_type in enumerate(self.vehicle_types):
            print(f"{i}: {vehicle_type}")

        cap.set(cv2.CAP_PROP_POS_FRAMES, plate.frame_start)
        _, frame = cap.read()
        cv2.namedWindow(plate.label, cv2.WINDOW_NORMAL)
        cv2.imshow(plate.label, frame)
        zoom = 1 / 2
        window_width, window_height = zoom * frame.shape[1], zoom * frame.shape[0]
        cv2.resizeWindow(plate.label, int(window_width), int(window_height))

        key: int = cv2.waitKey(0)
        key: int = int(chr(key))
        vehicle_type: str = self.vehicle_types[key]
        plate.vehicle_type = vehicle_type
        print(f"Labelled {plate.label} as {vehicle_type}", end='\n\n')
        cv2.destroyAllWindows()

    def _write_json(self):
        with open(self.dataset_path, 'w') as f:
            f.write(self.dataset.to_json())

    def label(self):
        for video in self.dataset.videos:
            video: Video
            video_filename: str = os.path.join(self.video_path, video.video_id + ".mp4")
            cap = cv2.VideoCapture(video_filename)
            for plate in video.plates:
                plate: Plate
                if self.skip_labelled_vehicle_type and plate.vehicle_type is not None:
                    continue
                self._label_plate_vehicle_type(cap, plate)

                self._write_json()


if __name__ == '__main__':
    handler = LabelVehicleTypes(
        '../icvlp_v0.1.json',
        '../videos',
        skip_labelled=True
    )
    handler.label()
