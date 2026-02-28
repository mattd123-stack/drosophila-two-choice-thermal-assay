[3_combine_coordinates.py](https://github.com/user-attachments/files/25621319/3_combine_coordinates.py)[2_extract_timestamps.py](https://github.com/user-attachments/files/25621318/2_extract_timestamps.py)[1_delete_every_other_bmp.py](https://github.com/user-attachments/files/25621312/1_delete_every_other_bmp.py)
# Drosophila Thermal Preference Analysis

Analysis scripts and template for quantifying temperature preference behaviour in *Drosophila yakuba* and *D. santomea* using two-choice thermal assays and YOLO-based fly tracking.

---

## Repository Structure

```
Drosophila-thermal-preference/
├── scripts/
│   ├── 1_delete_every_other_bmp.py   # Reduce dataset size before YOLO processing
│   ├── 2_extract_timestamps.py        # Extract frame timestamps from BMP filenames
│   └── 3_combine_coordinates.py       # Combine YOLO detection outputs into Excel
└── templates/
    └── ANALYSIS_FOR_TRIALS_TEMPLATE1.xlsx   # Excel analysis template
```

---

## Workflow Overview

```
Raw BMP frames from arena camera
        │
        ▼
[Script 1] Delete every other BMP  →  ~50% fewer frames
        │
        ▼
[YOLO Train and Detect App]         →  .txt detection files per frame
        │
        ├──▶ [Script 2] Extract timestamps  →  timestamps.xlsx
        │
        └──▶ [Script 3] Combine coordinates →  coordinates.xlsx
                │
                ▼
        [Excel template] Paste coordinates + timestamps,
                         calculate preference index
```

---

## Scripts

### Script 1 — Delete Every Other BMP (`1_delete_every_other_bmp.py`)

Removes every second BMP file from each trial folder to halve the dataset size before running YOLO detection. Files are sorted alphabetically; even-indexed frames are kept, odd-indexed frames are deleted.

**Setup:** Open the script and edit `TRIAL_FOLDERS` to list your trial folder paths.

```python
TRIAL_FOLDERS = [
    r"D:\Data\trial 1-santomea control 22-22",
    r"D:\Data\trial 2-santomea 12-21",
]
```

**Run:**
```
python 1_delete_every_other_bmp.py"""
Script 1: Delete Every Other BMP
=================================
Reduces dataset size by removing every second BMP file from each trial folder,
leaving approximately half the frames for YOLO processing.

Files are sorted alphabetically before deletion, so even-indexed files (0, 2, 4...)
are kept and odd-indexed files (1, 3, 5...) are deleted.

USAGE
-----
1. Edit TRIAL_FOLDERS below to include all your trial folders.
2. Run: python 1_delete_every_other_bmp.py
"""

import os

# =============================================================================
# CONFIGURATION — edit these paths before running
# =============================================================================

TRIAL_FOLDERS = [
    r"D:\All files for santomea and Yakuba\trial 1-santomea control 22-22",
    r"D:\All files for santomea and Yakuba\trial 2-santomea 12-21",
    # Add more folders here, one per line
]

# =============================================================================
# PROCESSING — do not edit below this line
# =============================================================================

def delete_every_other_bmp(folder_path):
    if not os.path.isdir(folder_path):
        print(f"  [ERROR] Folder not found: {folder_path}")
        return 0, 0

    bmp_files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith('.bmp'))
    to_delete = bmp_files[1::2]  # odd-indexed files

    for file_name in to_delete:
        os.remove(os.path.join(folder_path, file_name))

    return len(bmp_files), len(to_delete)


for folder in TRIAL_FOLDERS:
    print(f"\nProcessing: {folder}")
    total, deleted = delete_every_other_bmp(folder)
    if total > 0:
        print(f"  {total} BMP files found — {deleted} deleted, {total - deleted} kept.")

print("\nDone.")
 1_delete_every_other_bmp.py…]()

```

> ⚠️ This permanently deletes files. Make a backup of your raw data first.

---

### Script 2 — Extract Timestamps (`2_extract_timestamps.py`)

Reads BMP filenames from each trial folder and extracts the embedded timestamp (format `YYYYMMDDHHMMSS`). Calculates elapsed minutes from the first frame of each trial. Outputs one Excel sheet per trial.

If no timestamp is found in the filename, the script falls back to the file's modification time.

**Setup:** Edit `TRIAL_FOLDERS` and `OUTPUT_FILE`.

```python
TRIAL_FOLDERS = [
    r"D:\Data\trial 1-santomea control 22-22",
]
OUTPUT_FILE = r"D:\Data\timestamps.xlsx"
```

**Run:**
```
["""
Script 2: Extract Timestamps from BMP Filenames
================================================
Reads BMP filenames from each trial folder, extracts timestamps embedded in the
filename (format: YYYYMMDDHHMMSS), and calculates elapsed minutes from the start
of each trial. Results are saved to a single Excel workbook with one sheet per trial.

If a filename does not contain a recognisable timestamp, the script falls back to
the file's modification time.

USAGE
-----
1. Edit TRIAL_FOLDERS and OUTPUT_FILE below.
2. Run: python 2_extract_timestamps.py

Dependencies: openpyxl (install with: pip install openpyxl)
"""

import os
import re
from datetime import datetime
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

# =============================================================================
# CONFIGURATION — edit these paths before running
# =============================================================================

TRIAL_FOLDERS = [
    r"D:\All files for santomea and Yakuba\trial 1-santomea control 22-22",
    r"D:\All files for santomea and Yakuba\trial 2-santomea 12-21",
    # Add more folders here, one per line
]

OUTPUT_FILE = r"D:\All files for santomea and Yakuba\timestamps.xlsx"

# =============================================================================
# PROCESSING — do not edit below this line
# =============================================================================

TIMESTAMP_PATTERN = re.compile(r'(\d{14})')  # 14-digit: YYYYMMDDHHMMSS

HEADER = ["File", "Timestamp", "Time_Minutes_From_Start"]
HEADER_FILL = PatternFill("solid", start_color="4F81BD")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def extract_timestamp(filepath):
    filename = os.path.basename(filepath)
    match = TIMESTAMP_PATTERN.search(filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
        except ValueError:
            pass
    return datetime.fromtimestamp(os.path.getmtime(filepath))


def process_folder(folder_path):
    bmp_files = sorted(
        f for f in os.listdir(folder_path) if f.lower().endswith('.bmp')
    )
    if not bmp_files:
        return []

    rows = []
    timestamps = [extract_timestamp(os.path.join(folder_path, f)) for f in bmp_files]
    start = timestamps[0]

    for filename, ts in zip(bmp_files, timestamps):
        elapsed = (ts - start).total_seconds() / 60
        rows.append([filename, ts.strftime("%Y-%m-%d %H:%M:%S"), round(elapsed, 4)])

    return rows


wb = openpyxl.Workbook()
wb.remove(wb.active)  # remove default sheet

for folder in TRIAL_FOLDERS:
    sheet_name = os.path.basename(folder)[:31]  # Excel sheet name limit
    print(f"\nProcessing: {folder}")

    if not os.path.isdir(folder):
        print(f"  [ERROR] Folder not found.")
        continue

    rows = process_folder(folder)
    if not rows:
        print(f"  [WARNING] No BMP files found.")
        continue

    ws = wb.create_sheet(title=sheet_name)

    for col_idx, header in enumerate(HEADER, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(rows, start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 25

    print(f"  {len(rows)} BMP files processed.")

wb.save(OUTPUT_FILE)
print(f"\nSaved to: {OUTPUT_FILE}")
Uploading 2_extract_timestamps.py…]()


**Output columns:** `File` | `Timestamp` | `Time_Minutes_From_Start`

---
```

**Output columns:** `File` | `Timestamp` | `Time_Minutes_From_Start`

---

### Script 3 — Combine Coordinates (`3_combine_coordinates.py`)

Reads all YOLO output `.txt` files from each trial folder (one per frame) and extracts the bounding box coordinates. Outputs one Excel sheet per trial.

Expected YOLO `.txt` format per line: `<class> <x_center> <y_center> <width> <height>`

**Setup:** Edit `TRIAL_FOLDERS` and `OUTPUT_FILE`.

```python
TRIAL_FOLDERS = [
    r"D:\Data\trial 1-santomea control 22-22",
]
OUTPUT_FILE = r"D:\Data\coordinates.xlsx"
```

**Run:**
```
["""
Script 3: Combine YOLO Detection Coordinates
=============================================
Searches each trial folder for YOLO output .txt files, extracts the detection
coordinates (bounding box centre X, centre Y, width, height), and writes all
results to a single Excel workbook with one sheet per trial.

Expected .txt file format (YOLO standard):
    <class> <x_center> <y_center> <width> <height>

USAGE
-----
1. Edit TRIAL_FOLDERS and OUTPUT_FILE below.
2. Run: python 3_combine_coordinates.py

Dependencies: openpyxl (install with: pip install openpyxl)
"""

import os
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

# =============================================================================
# CONFIGURATION — edit these paths before running
# =============================================================================

TRIAL_FOLDERS = [
    r"D:\All files for santomea and Yakuba\trial 1-santomea control 22-22",
    r"D:\All files for santomea and Yakuba\trial 2-santomea 12-21",
    # Add more folders here, one per line
]

OUTPUT_FILE = r"D:\All files for santomea and Yakuba\coordinates.xlsx"

# =============================================================================
# PROCESSING — do not edit below this line
# =============================================================================

HEADER = ["File", "X-center", "Y-center", "Width", "Height"]
HEADER_FILL = PatternFill("solid", start_color="4F81BD")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def parse_txt_file(filepath):
    detections = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    detections.append([float(p) for p in parts[1:5]])
                except ValueError:
                    pass
    return detections


def process_folder(folder_path):
    txt_files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith('.txt'))
    rows = []
    for filename in txt_files:
        filepath = os.path.join(folder_path, filename)
        detections = parse_txt_file(filepath)
        for det in detections:
            rows.append([filename] + det)
        if not detections:
            rows.append([filename, None, None, None, None])
    return rows


wb = openpyxl.Workbook()
wb.remove(wb.active)

for folder in TRIAL_FOLDERS:
    sheet_name = os.path.basename(folder)[:31]
    print(f"\nProcessing: {folder}")

    if not os.path.isdir(folder):
        print(f"  [ERROR] Folder not found.")
        continue

    rows = process_folder(folder)
    if not rows:
        print(f"  [WARNING] No .txt files found.")
        continue

    ws = wb.create_sheet(title=sheet_name)

    for col_idx, header in enumerate(HEADER, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(rows, start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    ws.column_dimensions["A"].width = 35
    for col in ["B", "C", "D", "E"]:
        ws.column_dimensions[col].width = 14

    print(f"  {len(rows)} detections written.")

wb.save(OUTPUT_FILE)
print(f"\nSaved to: {OUTPUT_FILE}")
Uploading 3_combine_coordinates.py…]()
```


**Output columns:** `File` | `X-center` | `Y-center` | `Width` | `Height`

---

## Excel Analysis Template

`templates/ANALYSIS_FOR_TRIALS_TEMPLATE1.xlsx` contains pre-built formulas for calculating the preference index from YOLO coordinates and timestamps.
[ANALYSIS_FOR_TRIALS_TEMPLATE1.xlsx](https://github.com/user-attachments/files/25621333/ANALYSIS_FOR_TRIALS_TEMPLATE1.xlsx)


**Columns:**

| Column | Content |
|--------|---------|
| A–C | File, Timestamp, Time_Minutes_From_Start (paste from scripts 2) |
| D | Trial number (auto-calculated) drag down goes up by 2 from 0 |
| E–G | Coordinate filename (highlight coordinate files and paste location, extracted trial number, keep/delete helper (drag down and if extracted file number matches file name of timestamp then it will say keep. Otherwise select the drop down to show delete and delete columns a-c|
| H–K | X-center, Y-center, Width, Height (paste from script 3) delete class number (0) at the start|
| M–N | Slope and intercept of the thermal boundary line (make sure this is normalised to match YOLO coordinates|
| O | Zone classification: Top (cool side) or Bottom (warm side) |
| P | Delta_t (time elapsed between frames) |
| Q–R | Time above / below boundary |
| S–T | Total time on top / bottom |
| U | **Preference index:** `(top − bottom) / (top + bottom)` |

The slope (M) and intercept (N) values define the boundary line dividing the cool and warm halves of the arena. Update these values to match your arena calibration. Drag down all columns D, F, G, M, N, O, P, Q, R to complete analysis and calculate preference index.

---

## Dependencies

All scripts use only the Python standard library plus **openpyxl**, which is auto-installed on first run. Python 3.7 or later is required.

To install manually:
```
pip install openpyxl
```

---

## Naming Convention

Trial folders should follow this format for script 3's sheet naming:

```
trial [number]-[species] [temp pair]
```

Example: `trial 1-santomea control 22-22`

---

## Citation

If you use these scripts in published work, please cite this repository:

> [Author surname(s)] ([year]). *Drosophila thermal preference analysis scripts*. GitHub. https://github.com/[username]/Drosophila-thermal-preference
