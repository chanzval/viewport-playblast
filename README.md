# Viewport Playblast

<div align="center">

**Professional viewport tool for Autodesk Maya.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maya](https://img.shields.io/badge/Maya-2022%2B-blue)](https://www.autodesk.com/products/maya)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![Linux](https://img.shields.io/badge/Linux-Compatible-green)](https://www.linux.org)

</div>

---

## Key Features

- H.264 encoding with FFmpeg
- Resolution presets (Render, HD 1080, HD 720, HD 540, Custom)
- Frame range presets (Render, Playback, Animation, Custom)
- Any camera or active viewport
- Visibility Presets (Viewport, Geometry, Dynamics, Custom)
- Overscan (optional for compositing)
- Linux-compatible
---

## Acknowledgement
This tool is a refactored and extended version of Chris Zurbrigg's original work. 

**Original Author:** Chris Zurbrigg

**Original Website:** [zurbrigg.com](http://zurbrigg.com)

---
## My Contributions

While maintaining the core logic and functionality, I've made significant improvements:

1. **Additional Features**: Extended functionality for production pipelines
2. **Core Logic Improvements**: Improvements on temporary directory cleanup, viewport detection, camera handling, etc.
2. **Linux Compatibility**: Ported to Linux
3. **Modular Architecture**: Cleaner package structure for distribution and installation
4. **Enhanced Maintainability**: Smaller, focused modules
5. **Improved Testability**: Unit tests for core functionality


### Core Logic Improvements
- Improve viewport detection and camera handling
- Clean up temporary directories
- Skip encoding for Image sequences
- UI Improvements

### Additional Features
- **Open Output Folder**: Automatically open the output directory after playblast completes
- **Notifications**: Desktop notifications after playblast completes

---
### Requirements

- **Maya 2022+** (PySide2)  
- **FFmpeg** installed on your system
```bash
# Install FFmpeg on Linux (if Red Hat-based system, e.g., RHEL, CentOS, Fedora)
sudo yum install ffmpeg
```
---
## Quick Start

### Installation

```python
# Open Maya Script Editor
import sys
import os

# Add the module path
module_path = "/path/to/viewport-playblast/"
if module_path not in sys.path:
    sys.path.append(module_path)

# Launch the UI
from viewport_playblast import show_dialog
show_dialog()

# Click in a 3D viewport (the tool needs an active viewport to capture)
# Adjust settings and click Playblast
```
---

## Configuration

### FFmpeg Path

Set FFmpeg path via UI or programmatically:

```python
pb = ViewportPlayblast(ffmpeg_path="/usr/bin/ffmpeg")
```

### Maya Logging

```python
# Enable/disable Maya console logging
pb = ViewportPlayblast(log_to_maya=True)
pb.set_maya_logging_enabled(False)
```

---

## Usage Examples

### HD Playblast with Settings

```python
pb = ViewportPlayblast()
pb.set_camera("persp")
pb.set_resolution("HD 1080")
pb.set_frame_range("Playback")
pb.set_h264_settings("High", "fast")
pb.execute("/path/to/existing/directory", "hd_playblast", show_in_viewer=True, overwrite=True)
```

### Image Sequence

```python
pb = ViewportPlayblast()
pb.set_camera("persp")
pb.set_encoding("Image", "png")
pb.set_image_settings(100)
pb.execute("/path/to/existing/directory", "image_sequence")
```

### Custom Resolution

```python
pb = ViewportPlayblast()
pb.set_camera("persp")
pb.set_resolution((2048, 858))  # Cinemascope
pb.set_frame_range((1001, 1120))
pb.execute("/path/to/existing/directory", "custom_resolution", overwrite=True)
```

### Visibility Presets

```python
pb = ViewportPlayblast()
pb.set_camera("persp")
pb.set_visibility("Geo")  # Only show geometry
pb.execute("/path/to/existing/directory", "geo_only")
```

---

## Testing

### Run Unit Tests

```python
# In Maya Script Editor
import viewport_playblast.tests.test_core
viewport_playblast.tests.test_core.run_tests()
viewport_playblast.tests.test_ui.run_ui_tests()
viewport_playblast.tests.test_maya_integration.run_maya_tests()
```
---

## Common Troubleshooting

### FFmpeg Not Found
```
Error: ffmpeg executable path does not exist
```
**Solution**: Go to Edit > Settings and select your FFmpeg executable path.

### No Active Viewport
```
Error: An active viewport is not selected
```
**Solution**: Click inside a 3D viewport (persp, front, side, etc.) before running.

### Output File Exists
```
Error: Output file already exists
```
**Solution**: Enable "Force overwrite" checkbox  or choose a different filename.

---

##  Support

- **Email**: chanzvalmonte@gmail.com

---

## Future Plans
- Batch processing multiple cameras
- Recent output directory history
- Watermark
- Progress bar

---

<div align="center">

[⬆ Back to top](#viewport-playblast)

</div>
