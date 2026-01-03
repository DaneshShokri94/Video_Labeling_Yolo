# AnnotateX - Video Annotation Tool

A professional video annotation tool for creating object detection datasets. Built with Python, OpenCV, and Tkinter.

## Features

- Load and navigate video files (MP4, AVI, MOV, MKV)
- Draw bounding boxes with click and drag
- 80+ pre-defined COCO classes + custom classes
- Export annotations in multiple formats:
  - YOLO
  - Pascal VOC
  - COCO JSON
- Frame-by-frame navigation
- Copy annotations from previous frame
- Zoom and pan support
- Keyboard shortcuts for efficient workflow

## Requirements

- Python 3.8+
- OpenCV
- Pillow
- NumPy
- Tkinter

## Installation

```bash
pip install opencv-python pillow numpy
```

## Usage

```bash
python video_annotating.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Left/Right Arrow | Navigate frames |
| Space | Next frame |
| Delete | Delete selected box |
| Ctrl+Z | Undo |
| Ctrl+C | Copy from previous frame |
| Scroll | Zoom in/out |
| Escape | Deselect |

## Export Formats

- **YOLO**: Normalized coordinates (class_id, x_center, y_center, width, height)
- **VOC**: Pascal VOC XML format
- **COCO**: COCO JSON format with annotations

## License

MIT License
