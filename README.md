# Desktop Image Organizer

A comprehensive Python tool to locate, organize, and manage image files scattered across multiple drives on Windows. Features a menu-driven interface with duplicate detection, EXIF-based date renaming, and smart filtering.

## Features

- 🎯 **Menu-Driven Interface**: Choose from 5 different operations
- 🔍 **Multi-Drive Scanning**: Automatically detects and scans all available drives
- 📁 **Organized Structure**: Creates drive-specific subfolders to track where images came from
- 🔄 **Duplicate Detection**: Find and remove duplicate images using content-based hashing
- 📅 **Date-Based Renaming**: Rename files using EXIF date taken (or file creation date)
- 🛡️ **Safe Operation**: 
  - Dry run mode to preview changes before moving files
  - Skips system directories, program files, and game folders automatically
  - **Custom exclusions** - easily add your own folders to skip
  - Dual-layer protection prevents rescanning its own output folder
  - Handles filename conflicts intelligently
  - Comprehensive error handling and logging
- 📊 **Progress Tracking**: Real-time progress updates and detailed summary statistics
- 📝 **Detailed Logging**: Saves a complete log file of all operations
- 🎮 **Smart Filtering**: Won't move game assets, program images, or application files
- ☁️ **OneDrive Support**: Automatically detects OneDrive Desktop folder

## Supported Image Formats

`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.svg`, `.ico`, `.heic`, `.raw`, `.cr2`, `.nef`, `.orf`, `.sr2`

## Installation

### Required
- Python 3.6 or higher

```bash
# Check your Python version
python --version
```

### Optional (Recommended for Photo EXIF Data)
For best results with photo date extraction, install Pillow:

```bash
pip install Pillow
```

**Without Pillow:** The script will still work but will use file creation dates instead of EXIF "date taken" metadata.

## Usage

### Quick Start

```bash
python image_organizer.py
```

### Menu Options

```
======================================================================
                    DESKTOP IMAGE ORGANIZER
======================================================================

MENU:
1. Organize Images - Scan drives and move images to desktop
2. Remove Duplicates - Find and remove duplicate images
3. Rename by Date - Rename images with date prefix
4. Run All Functions - Organize, remove duplicates, and rename
5. Exit
```

### Option 1: Organize Images
- Scans all drives for image files
- Moves them to `Desktop/Photos to Clean/` (or OneDrive Desktop)
- Organizes into drive-specific subfolders
- Allows custom folder exclusions

### Option 2: Remove Duplicates
- Scans existing "Photos to Clean" folder
- Uses content-based hashing to find true duplicates
- Shows potential space savings
- Dry-run available before removal

### Option 3: Rename by Date
- Renames images with `YYYYMMDD_filename.ext` format
- Uses EXIF "date taken" if Pillow is installed
- Falls back to file creation date
- Option to override existing dated filenames

### Option 4: Run All Functions
- Executes all operations in sequence
- Confirmation prompts between each step
- Complete workflow for new image collections

### Folder Structure

```
Photos to Clean/
├── Images from Drive C/
│   ├── 20231225_vacation.jpg
│   └── 20240101_newyear.png
├── Images from Drive D/
│   └── 20231120_photo.jpg
└── organize_log_20251001_143025.txt
```

## Safety Features

### Directories Automatically Skipped

**System Folders:**
- Windows, Program Files, Program Files (x86)
- ProgramData, AppData
- $Recycle.Bin, System Volume Information
- Recovery, PerfLogs, Boot

**Game Launchers & Stores:**
- Steam, SteamApps, SteamLibrary
- Epic Games, Origin, EA Games
- Ubisoft, GOG Galaxy
- Xbox Games, Riot Games
- Battle.net, Blizzard, Bethesda

**Development & Software:**
- node_modules, .git, .venv, venv, vendor
- Microsoft, Adobe, NVIDIA, Intel

**User Safety:**
- The destination folder itself (dual-layer protection)
- Any custom folders you specify

### File Conflict Handling
If a file with the same name already exists in the destination, the script automatically adds a timestamp to the filename.

Example: `photo.jpg` → `photo_20251001_143025.jpg`

## Example Workflows

### First Time Setup
```
Select option 1 → Organize Images
- Add custom exclusions if needed
- Run dry-run to preview
- Confirm and organize

Select option 2 → Remove Duplicates  
- Scan for duplicates
- Preview removals in dry-run
- Confirm to free up space

Select option 3 → Rename by Date
- Choose to override existing dates (if using Pillow)
- Rename all images with YYYYMMDD format
```

### Maintenance Mode
Already have organized photos? Just run cleanup operations:

```
Select option 2 → Remove newly added duplicates
Select option 3 → Rename any new files
```

### Quick Example Output

**Duplicate Removal:**
```
Scanning for duplicates...
Scanned 3247 images
Found 45 unique images with duplicates
Total duplicate files: 89

Would remove: 89 duplicate files
Would save: 245.67 MB
```

**Date Renaming:**
```
Pillow detected! Will use EXIF data from photos when available.

Renaming images...
  Processing Images from Drive C: 127 images
  Processing Images from Drive G: 3247 images
  Renamed 10 images...
  Renamed 20 images...

Renaming complete!
Total images found: 3374
Renamed: 3200
Skipped (already dated): 174
```

## Advanced Features

### Date-Based File Naming
Files are renamed with format: `YYYYMMDD_originalname.ext`

**Examples:**
- `IMG_1234.jpg` → `20231225_IMG_1234.jpg`
- `vacation.png` → `20240715_vacation.png`

**Date Sources (in priority order):**
1. EXIF "DateTimeOriginal" (if Pillow installed)
2. File creation date (fallback)

### Duplicate Detection
Uses MD5 content hashing to identify true duplicates:
- Scans all images in destination folder
- Compares file content (not just names)
- Keeps first occurrence, removes rest
- Shows space savings before removal

### Desktop Location Detection
Automatically finds your desktop:
1. Checks `OneDrive\Desktop` first
2. Falls back to regular `Desktop`
3. Works seamlessly on OneDrive-synced systems

## Customization

### Programmatic Usage

```python
from image_organizer import DesktopImageOrganizer

# Custom destination and exclusions
organizer = DesktopImageOrganizer(
    destination_folder_name="My Photos",
    custom_exclusions=['my_game', 'work_files']
)

# Organize images
organizer.organize_images(dry_run=False)

# Find duplicates
duplicates = organizer.find_duplicates()
organizer.remove_duplicates(duplicates, dry_run=False)
```

## Important Notes

⚠️ **Warning**: Option 1 MOVES files (not copies them). Files will be removed from their original locations.

💡 **Tip**: Always use dry run mode to preview changes before committing.

🔒 **Permissions**: Administrator privileges may be needed for some directories.

📸 **EXIF Data**: Install Pillow for accurate photo dates. Without it, file creation dates are used.

☁️ **OneDrive**: The script automatically detects and uses OneDrive Desktop if available.

## Troubleshooting

**"Permission denied" errors**: Some folders require administrator access. The script will skip these and continue.

**Script runs slowly**: Large drives take time to scan. Progress updates keep you informed.

**Files not found**: Check if files are in excluded directories or already moved.

**Pillow not detected**: Make sure Pillow is installed in your Python environment (not just globally). Run: `pip install Pillow`

**OneDrive Desktop not found**: If using OneDrive, make sure `C:\Users\YourName\OneDrive\Desktop` exists.

## License

This script is provided as-is for personal use.

