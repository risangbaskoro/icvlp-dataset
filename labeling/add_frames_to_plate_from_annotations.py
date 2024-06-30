import os

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from icvlp import ICVLP, Video, Plate, Frame


class FrameAdder:
    def __init__(self,
                 dataset_path: str,
                 annotations_dir: str
                 ):
        here = os.path.dirname(__file__)
        self.dataset_path: str = os.path.join(here, dataset_path)
        self.dataset: ICVLP = ICVLP.from_json(self.dataset_path)
        self.annotations_dir: str = os.path.join(here, annotations_dir)

    def run(self):
        for video in self.dataset.videos:
            video: Video
            video_id: str = video.video_id

            for plate in video.plates:
                plate: Plate
                label: str = plate.label
                plate.frames = []
                plate.children = []

                for frame_number in range(plate.frame_start, plate.frame_end + 1, 5):
                    annot_filename: str = f"{video_id}_{frame_number}_{label}.xml"
                    annot_filepath: str = os.path.join(self.annotations_dir, annot_filename)

                    if not os.path.exists(annot_filepath):
                        print(f"{annot_filename} doesn't exist. Continuing...")
                        continue

                    bbox: list[int] = self.read_bbox_from_xml_file(annot_filepath)

                    if bbox is None:
                        print(f"{annot_filename} has {type(bbox)} bbox. Continuing...")
                        continue

                    frame_obj: Frame = Frame(frame=frame_number, bbox=bbox)
                    plate.append(frame_obj)
                    self.write_file()

    def write_file(self):
        with open(self.dataset_path, 'w') as f:
            f.write(self.dataset.to_json())

    @staticmethod
    def read_bbox_from_xml_file(xml_path: str):
        tree: ElementTree = ElementTree.parse(xml_path)
        root: Element = tree.getroot()
        obj: Element = root.find("object")
        if obj is None:
            return

        bndbox: Element = obj.find("bndbox")

        bbox: list[int] = [
            round(float(bndbox.find('xmin').text)),
            round(float(bndbox.find('ymin').text)),
            round(float(bndbox.find('xmax').text)),
            round(float(bndbox.find('ymax').text)),
        ]

        return bbox


if __name__ == '__main__':
    handler = FrameAdder(
        dataset_path='../icvlp_v0.1.json',
        annotations_dir='../annotations'
    )
    handler.run()
