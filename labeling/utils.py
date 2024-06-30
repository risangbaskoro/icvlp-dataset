import os

from ultralytics.engine.results import Results


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


def get_result_metadata(result: Results):
    shape = result.orig_img.shape
    orig_bbox = result.boxes.xyxy
    orig_box = orig_bbox.detach().numpy()
    bbox = orig_bbox.int().detach().numpy()
    return shape, orig_box, bbox


def get_label_composition(text: str):
    num = list("1234567890")
    mid = "".join([i for i in text if i in num])
    pre, post = text.split(mid)
    return pre, mid, post
