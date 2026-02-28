"""
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
