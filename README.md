# VisionFlow
Salutations to all the readers of this repository. This repository just contains the code (test and training) for the neweset version of YOLO (up to the push date). It presents the usage of YOLO26 for vehicle detection.

### Urban Traffic Vehicle Detection Dataset (YOLO Format)

#### Overview

This dataset is designed for multi-class vehicle detection in traffic scenes. The raw video source is extracted from YouTube video [`PNCJQkvALVc`](https://www.youtube.com/watch?v=PNCJQkvALVc). Due to annotation time constraints, a subset of **246 frames** was manually annotated using **Roboflow** with high-quality bounding boxes.

- **Format:** YOLOv8 / YOLO-compatible (normalized coordinates: `class x_center y_center width height`)
- **Annotation Method:** Manual (hand-labeled)
- **Dataset Source:** [Download Dataset](./data/scratch-vehdet-1k.yolo)

---

#### Classes

The dataset includes **5 common vehicle classes**:

- `bus`
- `car`
- `motorcycle`
- `truck`
- `van`

---

#### Dataset Splits

The annotated frames are partitioned as follows:

- **Train (75%):** ~184 frames
- **Validation (20%):** ~49 frames
- **Test (5%):** ~13 frames

---

#### Directory Structure

```text
scratch-vehdet-1k.yolo/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```
