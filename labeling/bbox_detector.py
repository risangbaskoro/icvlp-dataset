import os

import cv2
import numpy as np

from ultralytics import YOLO
from ultralytics.engine.results import Results

from icvlp import ICVLP, Video, Plate, Frame


class BoundingBoxDetector:
    def __init__(self,
                 model_path: str,
                 dataset_path: str,
                 video_path: str,
                 annotations_dir: str):
        here = os.path.dirname(os.path.abspath(__file__))
        self.detector_path: str = os.path.join(here, model_path)
        self.dataset_path: str = os.path.join(here, dataset_path)
        self.detector: YOLO = YOLO(self.detector_path)
        self.dataset: ICVLP = ICVLP.from_json(self.dataset_path)

        self.original_dataset_string: str = self.dataset.to_json()

        self.video_path: str = os.path.join(here, video_path)
        self.annotations_dir: str = os.path.join(here, annotations_dir)
        if not os.path.exists(self.annotations_dir):
            os.makedirs(self.annotations_dir, exist_ok=True)

    def label(self):
        for video in self.dataset.videos:
            video: Video
            video_id = video.video_id
            video_filename = os.path.join(self.video_path, f"{video_id}.mp4")
            if not os.path.exists(video_filename):
                print(f"Video {video_id} not found. Skipping.")
                continue
            cap = cv2.VideoCapture(video_filename)
            fps: int = video.fps
            video_fps: int = int(cap.get(cv2.CAP_PROP_FPS))
            step: int = video_fps // fps

            for plate in video.plates:
                plate: Plate
                label: str = plate.label
                frame_start: int = plate.frame_start
                frame_end: int = plate.frame_end

                for frame_number in range(frame_start, frame_end + 1, step):
                    if plate.check_frame_number_exists_in_children(frame_number):
                        print(f"Skipping frame {frame_number} for {label} as it is already labelled.")
                        continue
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
                    _, true_frame = cap.read()
                    self.show_frame_window(true_frame, f"{video_id} {frame_number} {label}")

                    object_name: str = f"plate-{plate.vehicle_type}"
                    results: list[Results] = self.detector(true_frame)
                    for result in results:
                        result: Results
                        shape, orig_bbox, bbox = self._get_result_metadata(result)
                        frame_filename: str = f"{video_id}_{frame_number}_{label}.jpeg"
                        for orig_box, box in zip(orig_bbox, bbox):
                            plate_frame: np.ndarray = true_frame[box[1]:box[3], box[0]:box[2]]
                            window_name: str = f"{video_id} {plate.vehicle_type} {frame_number} {label}"
                            self.show_plate_window(box, plate_frame, window_name)
                            key: int = cv2.waitKey(0)

                            if chr(key) == 'y':
                                self.create_xml_annotation(frame_filename, object_name, shape, orig_box)
                                self.append_frame_to_plate(plate, frame_number, box)
                                cv2.destroyWindow(window_name)
                                break
                            cv2.destroyWindow(window_name)
                    cv2.destroyAllWindows()

    @staticmethod
    def show_frame_window(true_frame, window_name):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, true_frame)
        shape = true_frame.shape
        zoom = 1
        window_width, window_height = zoom * (shape[1]), zoom * (shape[0])
        cv2.resizeWindow(window_name, int(window_width), int(window_height))

    @staticmethod
    def show_plate_window(box, plate_frame, window_name):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, plate_frame)
        zoom = 1
        window_width, window_height = zoom * (box[2] - box[0]), zoom * (box[3] - box[1])
        cv2.resizeWindow(window_name, int(window_width), int(window_height))
        cv2.moveWindow(window_name, int(box[0] - 10), int(box[1] - 10))

    def append_frame_to_plate(self, plate: Plate, frame_number, bbox):
        frame = Frame(frame=frame_number, bbox=bbox.tolist())
        plate.append(frame)
        with open(self.dataset_path, 'w') as f:
            f.write(self.dataset.to_json())

    def create_xml_annotation(self, image_filename: str, object_name: str, shape: tuple, orig_bbox: list):
        annotation_filename = image_filename.split('.')[0] + '.xml'
        annotation_file = os.path.join(self.annotations_dir, annotation_filename)
        with open(os.path.join(self.annotations_dir, annotation_file), 'w') as xml_file:
            xml_file.write(self.xml_annotation_string(image_filename, shape, object_name, orig_bbox))

    @staticmethod
    def xml_annotation_string(image_filename: str, image_shape, object_name: str, bbox: list[int]):
        height, width, depth = image_shape
        x_min, y_min, x_max, y_max = bbox

        return f"""<annotation>
    <folder>frames</folder>
    <filename>{image_filename}</filename>
    <size>
        <width>{width}</width>
        <height>{height}</height>
        <depth>{depth}</depth>
    </size>
    <object>
        <name>{object_name}</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <occluded>0</occluded>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{x_min}</xmin>
            <ymin>{y_min}</ymin>
            <xmax>{x_max}</xmax>
            <ymax>{y_max}</ymax>
        </bndbox>
    </object>
</annotation>
        """

    @staticmethod
    def _get_result_metadata(result: Results):
        shape = result.orig_img.shape
        orig_bbox = result.boxes.xyxy
        orig_box = orig_bbox.detach().numpy()
        bbox = orig_bbox.int().detach().numpy()
        return shape, orig_box, bbox


if __name__ == '__main__':
    handler = BoundingBoxDetector(
        model_path='../license-plate-detector.pt',
        dataset_path='../icvlp_v0.1.json',
        video_path='../videos',
        annotations_dir='../annotations',
    )

    handler.label()
