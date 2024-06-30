import os

from extract_frames import FramesExtractor


class AnnotationRemover:
    def __init__(self, annotation_dir: str, image_dir: str, backup_dir: str):
        handler = FramesExtractor(
            '../icvlp_v0.1.json',
            '../videos',
            'frames'
        )
        handler.extract()

        here = os.path.dirname(__file__)
        self.annotation_dir: str = os.path.join(here, annotation_dir)
        self.image_dir: str = os.path.join(here, image_dir)
        self.backup_dir: str = os.path.join(here, backup_dir)
        self.images: list[str] = os.listdir(self.image_dir)
        self.annotations: list[str] = os.listdir(self.annotation_dir)

        for annotation in self.annotations:
            if annotation.replace('.xml', '.jpeg') not in self.images:
                os.remove(os.path.join(self.annotation_dir, annotation))


if __name__ == '__main__':
    AnnotationRemover(
        '../annotations',
        '../frames',
        '../backup_annotations',
    )
