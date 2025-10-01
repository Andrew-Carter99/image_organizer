# Desktop Image Organizer

A Python script to locate and organize image files scattered across multiple hard drives on Windows.

## Features

- 🔍 **Multi-Drive Scanning**: Automatically detects and scans all available drives on your system
- 📁 **Organized Structure**: Creates drive-specific subfolders to track where images came from
- 🛡️ **Safe Operation**: 
  - Dry run mode to preview changes before moving files
  - Skips system directories, program files, and game folders automatically
  - **Custom exclusions** - easily add your own folders to skip
  - Dual-layer protection prevents rescanning its own output folder
  - Handles filename conflicts by adding timestamps
  - Comprehensive error handling and logging
- 📊 **Progress Tracking**: Real-time progress updates and detailed summary statistics
- 📝 **Logging**: Saves a detailed log file of all operations
- 🎮 **Smart Filtering**: Won't move game assets, program images, or application files

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
   python image_organizer.py
   ```

2. **Follow the prompts:**
   - Add custom folder exclusions (optional) - e.g., specific game folders, work projects
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

## Example Output

```
Desktop Image Organizer
======================================================================

This script will:
1. Scan all drives on your computer for image files
2. Move them to 'Photos to Clean' folder on your desktop
3. Organize them into subfolders by drive

NOTE: The script automatically excludes system folders, program files,
      and common game directories (Steam, Epic Games, etc.)

WARNING: This will move files from their current locations!

Do you want to add custom folder exclusions? (y/n): y

Enter folder names to exclude, one per line.
Examples: 'MyGame', 'work projects', 'important images'
Press Enter on an empty line when done.

Folder name to exclude (or Enter to finish): Baldur's Gate 3
  ✓ Will exclude folders containing: 'Baldur's Gate 3'
Folder name to exclude (or Enter to finish): 

Custom exclusions added: Baldur's Gate 3

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

### Interactive Customization
The script now includes interactive prompts for:
- Adding custom folder exclusions during runtime
- Running dry runs before moving files

### Programmatic Customization
You can also customize the script directly in code:

- **Change destination folder name**:
  ```python
  organizer = DesktopImageOrganizer("My Custom Folder Name")
  ```

- **Add custom exclusions programmatically**:
  ```python
  organizer = DesktopImageOrganizer(
      destination_folder_name="My Photos",
      custom_exclusions=['my_game', 'work_files', 'screenshots']
  )
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

