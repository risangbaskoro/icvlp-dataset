import os

import cv2
from tqdm import tqdm, trange

from icvlp import ICVLP, Plate, Video


class FramesExtractor:
    def __init__(self, dataset_path: str, video_path: str, extract_path: str):
        here = os.path.dirname(os.path.abspath(__file__))
        self.dataset_path: str = os.path.join(here, dataset_path)
        self.dataset: ICVLP = ICVLP.from_json(self.dataset_path)

        self.original_dataset_string: str = self.dataset.to_json()

        self.video_path: str = os.path.join(here, video_path)
        self.extract_path: str = extract_path
        if not os.path.exists(extract_path):
            os.makedirs(extract_path, exist_ok=True)

    def extract(self):
        plates_processed = []
        video_processed = 0
        plate_processed = 0
        images_extracted = 0

        for video in tqdm(
                self.dataset.videos,
                desc="Video",
                unit="video",
                leave=True,
                position=0
        ):
            video: Video
            video_id = video.video_id
            video_filename = os.path.join(self.video_path, f"{video_id}.mp4")
            if not os.path.exists(video_filename):
                print(f"Video {video_id} not found. Skipping.")
                continue
            cap = cv2.VideoCapture(video_filename)
            video_fps: float = cap.get(cv2.CAP_PROP_FPS)
            fps: int = video.fps
            step: int = int(video_fps // fps)
            video_processed += 1

            for plate in tqdm(
                    video.plates,
                    desc="Plate",
                    unit="plate",
                    position=1,
                    leave=False,
            ):
                plate: Plate
                label: str = plate.label
                frame_start: int = plate.frame_start
                frame_end: int = plate.frame_end

                if label not in plates_processed:
                    plates_processed.append(label)

                plate_processed = len(plates_processed)

                for frame_number in trange(
                        frame_start,
                        frame_end + 1,
                        step,
                        desc=f"{video_id} {label}",
                        unit="image",
                        position=2,
                        leave=False
                ):
                    images_extracted += 1
                    frame_filename: str = f"{video_id}_{frame_number}_{label}.jpeg"
                    if os.path.exists(os.path.join(self.extract_path, frame_filename)):
                        continue
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
                    _, frame = cap.read()

                    frame_path: str = os.path.join(self.extract_path, frame_filename)
                    cv2.imwrite(frame_path, frame)

        print(f"Processed {video_processed} videos: {plate_processed} plates, {images_extracted} images.")


if __name__ == '__main__':
    handler = FramesExtractor(
        '../icvlp_v0.1.json',
        '../videos',
        'frames'
    )
    handler.extract()
