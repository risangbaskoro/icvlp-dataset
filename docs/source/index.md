# Indonesian Commercial Vehicle License Plate Dataset

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   object
   downloader
 
```

ICVLP is a dataset of license plates that is collected
from YouTube videos. This dataset is picked and labeled
manually.

## How it works?

First, we download videos from our json file.

Then, for each video, we get to the given frame and crop the frame according to bounding box, also defined in the json
file.

We then save the cropped image as a file.


