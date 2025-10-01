# Desktop Image Organizer

A Python script to locate and organize image files scattered across multiple hard drives on Windows.

## Features

- 🔍 **Multi-Drive Scanning**: Automatically detects and scans all available drives on your system
- 📁 **Organized Structure**: Creates drive-specific subfolders to track where images came from
- 🛡️ **Safe Operation**: 
  - Dry run mode to preview changes before moving files
  - Skips system directories to avoid breaking Windows
  - Handles filename conflicts by adding timestamps
  - Comprehensive error handling and logging
- 📊 **Progress Tracking**: Real-time progress updates and detailed summary statistics
- 📝 **Logging**: Saves a detailed log file of all operations

## Supported Image Formats

`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.svg`, `.ico`, `.heic`, `.raw`, `.cr2`, `.nef`, `.orf`, `.sr2`

## Installation

No external dependencies needed! This script uses only Python standard library.

```bash
# Just make sure you have Python 3.6+ installed
python --version
```

## Usage

1. **Run the script:**
   ```bash
   python main.py
   ```

2. **Follow the prompts:**
   - Choose whether to run a dry run first (recommended!)
   - Confirm to proceed with the actual file move

3. **Find your organized images:**
   - Location: `Desktop/Photos to Clean/`
   - Structure:
     ```
     Photos to Clean/
     ├── Images from Drive C/
     │   ├── image1.jpg
     │   └── image2.png
     ├── Images from Drive D/
     │   └── photo.jpg
     └── organize_log_YYYYMMDD_HHMMSS.txt
     ```

## Safety Features

### Directories Automatically Skipped
- Windows system folders (Windows, Program Files, etc.)
- Hidden system folders ($Recycle.Bin, System Volume Information)
- AppData folders
- The destination folder itself

### File Conflict Handling
If a file with the same name already exists in the destination, the script automatically adds a timestamp to the filename.

Example: `photo.jpg` → `photo_20251001_143025.jpg`

## Example Output

```
Desktop Image Organizer
======================================================================

This script will:
1. Scan all drives on your computer for image files
2. Move them to 'Photos to Clean' folder on your desktop
3. Organize them into subfolders by drive

Do you want to run a DRY RUN first? (y/n): y

[2025-10-01 14:30:15] Desktop Image Organizer Started
[2025-10-01 14:30:15] Drives to scan: C:\, D:\

[2025-10-01 14:30:15] Processing Drive C:
[2025-10-01 14:30:15] Scanning drive: C:\
[2025-10-01 14:30:25] Found 127 image(s) on Drive C

======================================================================
SUMMARY
======================================================================
Total images found: 127

By Drive:
  Drive C: 127 images found
======================================================================
```

## Customization

You can modify the script to:

- **Change destination folder name**: Edit the `DesktopImageOrganizer()` initialization
  ```python
  organizer = DesktopImageOrganizer("My Custom Folder Name")
  ```

- **Add/remove image extensions**: Modify the `IMAGE_EXTENSIONS` set in the class

- **Scan specific drives only**: Pass a list of drives
  ```python
  organizer.organize_images(drives=['C:\\', 'D:\\'])
  ```

## Important Notes

⚠️ **Warning**: This script MOVES files (not copies them). They will be removed from their original locations.

💡 **Tip**: Always run the dry run mode first to see what will happen before actually moving files.

🔒 **Permissions**: You may need administrator privileges to access some directories.

## Troubleshooting

**"Permission denied" errors**: Some folders require administrator access. The script will skip these and continue.

**Script runs slowly**: Large drives with many files will take time to scan. Progress updates will keep you informed.

**Files not found**: Make sure the files haven't been moved already or aren't in excluded system directories.

## License

This script is provided as-is for personal use.

