import os
import shutil
import string
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class DesktopImageOrganizer:
    """
    Organizes image files from multiple drives into a centralized folder structure.
    """
    
    # Common image file extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', 
                       '.tif', '.webp', '.svg', '.ico', '.heic', '.raw', 
                       '.cr2', '.nef', '.orf', '.sr2'}
    
    def __init__(self, destination_folder_name="Photos to Clean", custom_exclusions=None, rename_by_date=False):
        """
        Initialize the organizer.
        
        Args:
            destination_folder_name: Name of the folder to create on desktop
            custom_exclusions: List of additional directory names to exclude (case-insensitive)
            rename_by_date: If True, rename files with date prefix for chronological sorting
        """
        self.destination_folder_name = destination_folder_name
        
        # Try OneDrive Desktop first, fall back to regular Desktop
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        regular_desktop = Path.home() / "Desktop"
        
        if onedrive_desktop.exists():
            self.desktop_path = onedrive_desktop
        else:
            self.desktop_path = regular_desktop
        
        self.destination_path = self.desktop_path / destination_folder_name
        self.custom_exclusions = [exc.lower() for exc in (custom_exclusions or [])]
        self.rename_by_date = rename_by_date
        self.log_messages = []
        self.stats = {
            'total_found': 0,
            'total_moved': 0,
            'total_errors': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'space_saved': 0,
            'by_drive': {}
        }
    
    def log(self, message):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.log_messages.append(log_entry)
    
    def get_available_drives(self):
        """
        Get all available drive letters on Windows.
        
        Returns:
            list: List of available drive paths (e.g., ['C:\\', 'D:\\'])
        """
        drives = []
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append(drive_path)
        return drives
    
    def is_image_file(self, file_path):
        """
        Check if a file is an image based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file is an image
        """
        return file_path.suffix.lower() in self.IMAGE_EXTENSIONS
    
    def should_skip_path(self, path):
        """
        Determine if a path should be skipped during scanning.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path should be skipped
        """
        path_str = str(path).lower()
        
        # Skip if already in destination folder (primary protection)
        if str(self.destination_path).lower() in path_str:
            return True
        
        # Skip system, program, and game directories
        skip_dirs = [
            # Destination folder (secondary protection - by folder name)
            self.destination_folder_name.lower(),
            # Windows system folders
            'windows', 'program files', 'program files (x86)',
            'programdata', '$recycle.bin', 'system volume information',
            'recovery', 'perflogs', 'boot', 'appdata',
            # Game launchers and stores
            'steam', 'steamapps', 'steamlibrary', 'epic games', 'epicgames',
            'origin games', 'ea games', 'ubisoft', 'ubisoft game launcher',
            'gog games', 'gog galaxy', 'xbox games', 'riot games',
            'battle.net', 'blizzard', 'bethesda',
            # Common game install locations
            'games', 'my games',
            # Development and software
            'node_modules', '.git', 'vendor', '.venv', 'venv',
            # Other programs
            'microsoft', 'adobe', 'nvidia', 'intel'
        ]
        
        # Add user's custom exclusions
        all_skip_dirs = skip_dirs + self.custom_exclusions
        
        for skip_dir in all_skip_dirs:
            if f'\\{skip_dir}\\' in path_str or path_str.endswith(f'\\{skip_dir}'):
                return True
        
        return False
    
    def find_images_on_drive(self, drive_path):
        """
        Recursively find all image files on a drive.
        
        Args:
            drive_path: Root path of the drive to scan
            
        Returns:
            list: List of Path objects for found images
        """
        images = []
        self.log(f"Scanning drive: {drive_path}")
        
        try:
            for root, dirs, files in os.walk(drive_path):
                # Filter out directories to skip
                dirs[:] = [d for d in dirs if not self.should_skip_path(Path(root) / d)]
                
                current_path = Path(root)
                if self.should_skip_path(current_path):
                    continue
                
                for file in files:
                    file_path = current_path / file
                    if self.is_image_file(file_path):
                        images.append(file_path)
                        
        except PermissionError as e:
            self.log(f"  Permission denied: {root}")
        except Exception as e:
            self.log(f"  Error scanning {root}: {str(e)}")
        
        return images
    
    def create_destination_structure(self, drive_letter):
        """
        Create destination folder structure for a drive.
        
        Args:
            drive_letter: Letter of the drive (e.g., 'C')
            
        Returns:
            Path: Path to the drive's subfolder
        """
        drive_folder = self.destination_path / f"Images from Drive {drive_letter}"
        drive_folder.mkdir(parents=True, exist_ok=True)
        return drive_folder
    
    def get_image_date(self, image_path):
        """
        Get the date of an image from EXIF data or file metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            datetime: Date of the image, or None if not available
        """
        # Try to get EXIF date taken (most accurate for photos)
        if PIL_AVAILABLE:
            try:
                img = Image.open(image_path)
                exif_data = img._getexif()
                
                if exif_data:
                    # Look for DateTimeOriginal (when photo was taken)
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == "DateTimeOriginal":
                            # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            except Exception:
                pass  # If EXIF reading fails, fall back to file dates
        
        # Fall back to file creation/modification date
        try:
            # Use creation time on Windows, modification time as fallback
            stat = image_path.stat()
            # Try creation time first (st_ctime on Windows is creation time)
            if hasattr(stat, 'st_birthtime'):
                return datetime.fromtimestamp(stat.st_birthtime)
            else:
                # On Windows, st_ctime is creation time
                return datetime.fromtimestamp(stat.st_ctime)
        except Exception:
            return None
    
    def generate_dated_filename(self, source_path):
        """
        Generate a filename with date prefix for chronological sorting.
        
        Args:
            source_path: Original file path
            
        Returns:
            str: New filename with date prefix (YYYYMMDD_originalname.ext)
        """
        filename = source_path.name
        
        # Remove existing date prefix if present (to avoid stacking)
        if len(filename) >= 9 and filename[:8].isdigit() and filename[8] == '_':
            filename = filename[9:]  # Remove YYYYMMDD_ prefix
        
        image_date = self.get_image_date(source_path)
        
        if image_date:
            date_prefix = image_date.strftime("%Y%m%d")
            return f"{date_prefix}_{filename}"
        else:
            # If no date found, use current date as fallback
            date_prefix = datetime.now().strftime("%Y%m%d")
            return f"{date_prefix}_{filename}"
    
    def move_image(self, source_path, destination_folder):
        """
        Move an image file to the destination folder.
        
        Args:
            source_path: Source path of the image
            destination_folder: Destination folder path
            
        Returns:
            bool: True if successfully moved
        """
        try:
            # Determine the destination filename
            if self.rename_by_date:
                new_filename = self.generate_dated_filename(source_path)
            else:
                new_filename = source_path.name
            
            # Handle filename conflicts
            destination_file = destination_folder / new_filename
            if destination_file.exists():
                # Add extra timestamp to filename if conflict exists
                stem = Path(new_filename).stem
                suffix = Path(new_filename).suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")  # Added microseconds for uniqueness
                destination_file = destination_folder / f"{stem}_{timestamp}{suffix}"
            
            shutil.move(str(source_path), str(destination_file))
            return True
            
        except PermissionError:
            self.log(f"  Permission denied: {source_path}")
            return False
        except Exception as e:
            self.log(f"  Error moving {source_path}: {str(e)}")
            return False
    
    def organize_images(self, drives=None, dry_run=False):
        """
        Main method to organize images across drives.
        
        Args:
            drives: List of drive paths to scan (None = all drives)
            dry_run: If True, only report what would be done without moving files
        """
        self.log("=" * 70)
        self.log("Desktop Image Organizer Started")
        self.log("=" * 70)
        
        if dry_run:
            self.log("DRY RUN MODE - No files will be moved")
        
        # Get drives to scan
        if drives is None:
            drives = self.get_available_drives()
        
        self.log(f"Drives to scan: {', '.join(drives)}")
        self.log("")
        
        # Create main destination folder
        if not dry_run:
            self.destination_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Destination folder created: {self.destination_path}")
        
        # Process each drive
        for drive in drives:
            drive_letter = drive[0]  # Extract letter (e.g., 'C' from 'C:\\')
            
            self.log("")
            self.log(f"Processing Drive {drive_letter}:")
            self.log("-" * 70)
            
            # Find images
            images = self.find_images_on_drive(drive)
            self.stats['total_found'] += len(images)
            self.stats['by_drive'][drive_letter] = {'found': len(images), 'moved': 0}
            
            self.log(f"Found {len(images)} image(s) on Drive {drive_letter}")
            
            if not images:
                continue
            
            # Create drive subfolder
            if not dry_run:
                drive_folder = self.create_destination_structure(drive_letter)
                self.log(f"Destination: {drive_folder}")
            
            # Move images
            self.log("Moving images...")
            for i, image_path in enumerate(images, 1):
                if dry_run:
                    self.log(f"  [{i}/{len(images)}] Would move: {image_path}")
                else:
                    if self.move_image(image_path, drive_folder):
                        self.stats['total_moved'] += 1
                        self.stats['by_drive'][drive_letter]['moved'] += 1
                        if i % 10 == 0 or i == len(images):
                            self.log(f"  Progress: {i}/{len(images)} images moved")
                    else:
                        self.stats['total_errors'] += 1
        
        # Print summary
        self.print_summary(dry_run)
        
        # Save log file
        if not dry_run:
            self.save_log()
    
    def print_summary(self, dry_run=False):
        """Print summary statistics."""
        self.log("")
        self.log("=" * 70)
        self.log("SUMMARY")
        self.log("=" * 70)
        self.log(f"Total images found: {self.stats['total_found']}")
        
        if not dry_run:
            self.log(f"Total images moved: {self.stats['total_moved']}")
            self.log(f"Total errors: {self.stats['total_errors']}")
        
        self.log("")
        self.log("By Drive:")
        for drive, stats in self.stats['by_drive'].items():
            if dry_run:
                self.log(f"  Drive {drive}: {stats['found']} images found")
            else:
                self.log(f"  Drive {drive}: {stats['moved']}/{stats['found']} moved")
        
        self.log("=" * 70)
    
    def calculate_file_hash(self, file_path):
        """
        Calculate MD5 hash of a file for duplicate detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: MD5 hash of the file
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.log(f"  Error hashing {file_path}: {str(e)}")
            return None
    
    def find_duplicates(self):
        """
        Find duplicate images in the destination folder.
        
        Returns:
            dict: Dictionary mapping hash to list of file paths with that hash
        """
        self.log("")
        self.log("=" * 70)
        self.log("SCANNING FOR DUPLICATES")
        self.log("=" * 70)
        
        hash_dict = defaultdict(list)
        file_count = 0
        
        # Scan all files in destination folder
        for root, dirs, files in os.walk(self.destination_path):
            for file in files:
                file_path = Path(root) / file
                
                # Only process image files, skip log files
                if self.is_image_file(file_path):
                    file_count += 1
                    if file_count % 50 == 0:
                        self.log(f"  Scanned {file_count} images...")
                    
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        hash_dict[file_hash].append(file_path)
        
        # Filter to only duplicates (hash appears more than once)
        duplicates = {h: paths for h, paths in hash_dict.items() if len(paths) > 1}
        
        duplicate_count = sum(len(paths) - 1 for paths in duplicates.values())
        self.stats['duplicates_found'] = duplicate_count
        
        self.log(f"Scanned {file_count} total images")
        self.log(f"Found {len(duplicates)} unique images with duplicates")
        self.log(f"Total duplicate files: {duplicate_count}")
        
        return duplicates
    
    def remove_duplicates(self, duplicates, dry_run=False):
        """
        Remove duplicate images, keeping the first occurrence.
        
        Args:
            duplicates: Dictionary of hash to file paths
            dry_run: If True, only report what would be done
        """
        if not duplicates:
            self.log("No duplicates to remove.")
            return
        
        self.log("")
        self.log("=" * 70)
        if dry_run:
            self.log("DUPLICATE REMOVAL - DRY RUN")
        else:
            self.log("REMOVING DUPLICATES")
        self.log("=" * 70)
        
        for file_hash, file_paths in duplicates.items():
            # Sort by path to keep the first one consistently
            file_paths.sort()
            keeper = file_paths[0]
            duplicates_to_remove = file_paths[1:]
            
            self.log(f"\nKeeping: {keeper.name}")
            
            for dup_path in duplicates_to_remove:
                try:
                    file_size = dup_path.stat().st_size
                    
                    if dry_run:
                        self.log(f"  Would remove: {dup_path.name} ({self.format_size(file_size)})")
                        self.stats['space_saved'] += file_size
                    else:
                        dup_path.unlink()
                        self.stats['duplicates_removed'] += 1
                        self.stats['space_saved'] += file_size
                        self.log(f"  ✓ Removed: {dup_path.name} ({self.format_size(file_size)})")
                        
                except Exception as e:
                    self.log(f"  ✗ Error removing {dup_path.name}: {str(e)}")
        
        self.log("")
        self.log("=" * 70)
        self.log("DUPLICATE REMOVAL SUMMARY")
        self.log("=" * 70)
        
        if dry_run:
            self.log(f"Would remove: {self.stats['duplicates_found']} duplicate files")
            self.log(f"Would save: {self.format_size(self.stats['space_saved'])}")
        else:
            self.log(f"Removed: {self.stats['duplicates_removed']} duplicate files")
            self.log(f"Space saved: {self.format_size(self.stats['space_saved'])}")
        
        self.log("=" * 70)
    
    def format_size(self, bytes_size):
        """
        Format byte size into human-readable format.
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            str: Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def save_log(self):
        """Save log messages to a file in the destination folder's logs subfolder."""
        # Create logs subfolder if it doesn't exist
        logs_folder = self.destination_path / "logs"
        logs_folder.mkdir(exist_ok=True)
        
        log_file = logs_folder / f"organize_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_messages))
            self.log(f"Log saved to: {log_file}")
        except Exception as e:
            print(f"Error saving log: {str(e)}")


def display_menu(folder_exists):
    """Display the main menu and get user choice."""
    print("\n" + "=" * 70)
    print("                    DESKTOP IMAGE ORGANIZER")
    print("=" * 70)
    print()
    
    if folder_exists:
        print("✓ 'Photos to Clean' folder found on desktop")
        print()
    else:
        print("Note: 'Photos to Clean' folder not found on desktop")
        print()
    
    print("MENU:")
    print("1. Organize Images - Scan drives and move images to desktop")
    print("2. Remove Duplicates - Find and remove duplicate images")
    print("3. Rename by Date - Rename images with date prefix")
    print("4. Run All Functions - Organize, remove duplicates, and rename")
    print("5. Exit")
    print()
    
    if not folder_exists:
        print("Note: Options 2 and 3 require 'Photos to Clean' folder to exist.")
        print("      Run option 1 first to organize images.")
        print()
    
    while True:
        choice = input("Select an option (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")


def organize_images_workflow(custom_exclusions=None):
    """Run the image organization workflow."""
    print("\n" + "=" * 70)
    print("                    ORGANIZE IMAGES")
    print("=" * 70)
    print()
    print("This will:")
    print("• Scan all drives on your computer for image files")
    print("• Move them to 'Photos to Clean' folder on your desktop")
    print("• Organize them into subfolders by drive")
    print()
    print("NOTE: Automatically excludes system folders, program files,")
    print("      and common game directories (Steam, Epic Games, etc.)")
    print()
    print("WARNING: This will move files from their current locations!")
    print()
    
    # Ask about custom exclusions
    if custom_exclusions is None:
        custom_exclusions = []
        response = input("Do you want to add custom folder exclusions? (y/n): ").strip().lower()
        if response == 'y':
            print()
            print("Enter folder names to exclude, one per line.")
            print("Examples: 'MyGame', 'work projects', 'important images'")
            print("Press Enter on an empty line when done.")
            print()
            while True:
                exclusion = input("Folder name to exclude (or Enter to finish): ").strip()
                if not exclusion:
                    break
                custom_exclusions.append(exclusion)
                print(f"  ✓ Will exclude folders containing: '{exclusion}'")
        
        if custom_exclusions:
            print(f"\nCustom exclusions added: {', '.join(custom_exclusions)}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to run a DRY RUN first? (y/n): ").strip().lower()
    
    # Don't rename by date in this workflow - that's for option 3 or 4
    organizer = DesktopImageOrganizer(custom_exclusions=custom_exclusions, rename_by_date=False)
    
    if response == 'y':
        print("\nRunning DRY RUN (no files will be moved)...\n")
        organizer.organize_images(dry_run=True)
        print()
        response = input("Do you want to proceed with the actual move? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation cancelled.")
            return None
        
        # Create new organizer instance for actual run with same settings
        organizer = DesktopImageOrganizer(custom_exclusions=custom_exclusions, rename_by_date=False)
    
    print("\nStarting image organization...\n")
    organizer.organize_images(dry_run=False)
    print("\nImage organization complete!")
    
    return organizer


def remove_duplicates_workflow(organizer=None):
    """Run the duplicate removal workflow."""
    print("\n" + "=" * 70)
    print("                    REMOVE DUPLICATES")
    print("=" * 70)
    print()
    
    if organizer is None:
        organizer = DesktopImageOrganizer()
        
        # Check if destination folder exists
        if not organizer.destination_path.exists():
            print(f"Error: '{organizer.destination_folder_name}' folder not found on desktop.")
            print("Please run 'Organize Images' first.")
            return None
    
    print("Scanning for duplicates...\n")
    duplicates = organizer.find_duplicates()
    
    if not duplicates:
        print("\nNo duplicates found!")
        return organizer
    
    print()
    response = input("Do you want to see a DRY RUN of duplicate removal first? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\nRunning DRY RUN for duplicate removal...\n")
        # Reset stats for dry run
        organizer.stats['duplicates_removed'] = 0
        organizer.stats['space_saved'] = 0
        organizer.remove_duplicates(duplicates, dry_run=True)
        print()
        response = input("Do you want to proceed with removing duplicates? (y/n): ").strip().lower()
        if response != 'y':
            print("Duplicate removal cancelled.")
            return organizer
        
        # Reset stats for actual run
        organizer.stats['duplicates_removed'] = 0
        organizer.stats['space_saved'] = 0
    
    print("\nRemoving duplicates...\n")
    organizer.remove_duplicates(duplicates, dry_run=False)
    print("\nDuplicate removal complete!")
    
    return organizer


def rename_by_date_workflow(organizer=None):
    """Rename existing images in the destination folder by date."""
    print("\n" + "=" * 70)
    print("                    RENAME BY DATE")
    print("=" * 70)
    print()
    
    if organizer is None:
        organizer = DesktopImageOrganizer()
        
        # Check if destination folder exists
        if not organizer.destination_path.exists():
            print(f"Error: '{organizer.destination_folder_name}' folder not found on desktop.")
            print("Please run 'Organize Images' first.")
            return None
    
    if not PIL_AVAILABLE:
        print("Note: Pillow library not installed. Will use file creation dates only.")
        print("      For best results with photos, install Pillow: pip install Pillow")
        print()
        print("Files that already have date prefixes (YYYYMMDD_filename) will be skipped.")
        print()
    else:
        print("Pillow detected! Will use EXIF data from photos when available.")
        print()
    
    print("This will rename all images in the folder with date prefixes.")
    print("Format: YYYYMMDD_originalname.ext")
    print()
    
    # Ask about overriding already-dated files (only if Pillow is available)
    force_rename = False
    if PIL_AVAILABLE:
        print("Files that already have date prefixes (YYYYMMDD_filename) will be skipped by default.")
        response = input("Do you want to override existing dated filenames with EXIF dates? (y/n): ").strip().lower()
        if response == 'y':
            force_rename = True
            print("  ✓ Will rename ALL files, including those with existing date prefixes")
        else:
            print("  ✓ Will skip files that already have date prefixes")
        print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return organizer
    
    # Count images to rename
    image_count = 0
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    print("\nRenaming images...\n")
    organizer.log("=" * 70)
    organizer.log("RENAMING IMAGES BY DATE")
    organizer.log("=" * 70)
    organizer.log(f"Scanning directory: {organizer.destination_path}")
    
    # Debug: Show directory structure
    print(f"Scanning: {organizer.destination_path}")
    for root, dirs, files in os.walk(organizer.destination_path):
        # Debug output for directories
        if dirs:
            organizer.log(f"Found subdirectories in {root}: {dirs}")
            print(f"  Found {len(dirs)} subdirectories in: {Path(root).name}")
        
        # Debug output for images in this directory
        image_files_in_dir = [f for f in files if Path(root, f).suffix.lower() in organizer.IMAGE_EXTENSIONS]
        if image_files_in_dir:
            print(f"  Processing {Path(root).name}: {len(image_files_in_dir)} images")
        
        for file in files:
            file_path = Path(root) / file
            
            # Only process image files, skip log files
            if organizer.is_image_file(file_path):
                image_count += 1
                
                # Check if already has date prefix (safely handle short filenames)
                # Skip if file already has date prefix, unless force_rename is True
                if not force_rename and len(file) >= 9 and file[:8].isdigit() and file[8] == '_':
                    skipped_count += 1
                    organizer.log(f"Skipped (already has date prefix): {file}")
                    continue  # Skip already renamed files
                
                try:
                    new_filename = organizer.generate_dated_filename(file_path)
                    new_path = file_path.parent / new_filename
                    
                    # Handle conflicts
                    if new_path.exists():
                        stem = Path(new_filename).stem
                        suffix = Path(new_filename).suffix
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                        new_path = file_path.parent / f"{stem}_{timestamp}{suffix}"
                    
                    file_path.rename(new_path)
                    renamed_count += 1
                    
                    if renamed_count % 10 == 0:
                        print(f"  Renamed {renamed_count} images...")
                    
                    organizer.log(f"Renamed: {file} → {new_path.name}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Error renaming {file}: {str(e)}"
                    organizer.log(error_msg)
                    print(f"  ⚠ {error_msg}")
    
    print(f"\nRenaming complete!")
    print(f"Total images found: {image_count}")
    print(f"Renamed: {renamed_count}")
    print(f"Skipped (already dated): {skipped_count}")
    if error_count > 0:
        print(f"Errors: {error_count}")
    
    organizer.log(f"\nTotal images found: {image_count}")
    organizer.log(f"Renamed: {renamed_count}")
    organizer.log(f"Skipped (already dated): {skipped_count}")
    organizer.log(f"Errors: {error_count}")
    organizer.log("=" * 70)
    
    return organizer


def main():
    """Main entry point with menu system."""
    organizer = None
    
    while True:
        # Check if destination folder exists
        temp_organizer = DesktopImageOrganizer()
        folder_exists = temp_organizer.destination_path.exists()
        
        # Display menu and get choice
        choice = display_menu(folder_exists)
        
        if choice == '1':
            # Organize Images
            organizer = organize_images_workflow()
            if organizer:
                organizer.save_log()
                print("\nPress Enter to return to menu...")
                input()
        
        elif choice == '2':
            # Remove Duplicates
            if not folder_exists:
                print("\nError: 'Photos to Clean' folder not found on desktop.")
                print("Please run 'Organize Images' first.")
                print("\nPress Enter to return to menu...")
                input()
            else:
                organizer = remove_duplicates_workflow(organizer)
                if organizer:
                    organizer.save_log()
                print("\nPress Enter to return to menu...")
                input()
        
        elif choice == '3':
            # Rename by Date
            if not folder_exists:
                print("\nError: 'Photos to Clean' folder not found on desktop.")
                print("Please run 'Organize Images' first.")
                print("\nPress Enter to return to menu...")
                input()
            else:
                organizer = rename_by_date_workflow(organizer)
                if organizer:
                    organizer.save_log()
                print("\nPress Enter to return to menu...")
                input()
        
        elif choice == '4':
            # Run All Functions
            print("\n" + "=" * 70)
            print("                    RUN ALL FUNCTIONS")
            print("=" * 70)
            print()
            print("This will run all operations in sequence:")
            print("1. Organize Images")
            print("2. Remove Duplicates")
            print("3. Rename by Date")
            print()
            
            response = input("Continue? (y/n): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                print("\nPress Enter to return to menu...")
                input()
                continue
            
            # Step 1: Organize Images
            organizer = organize_images_workflow()
            
            if organizer:
                # Step 2: Remove Duplicates
                print()
                response = input("Continue to duplicate removal? (y/n): ").strip().lower()
                if response == 'y':
                    organizer = remove_duplicates_workflow(organizer)
                
                # Step 3: Rename by Date
                if organizer:
                    print()
                    response = input("Continue to date-based renaming? (y/n): ").strip().lower()
                    if response == 'y':
                        organizer = rename_by_date_workflow(organizer)
                
                if organizer:
                    organizer.save_log()
                    print("\nAll operations complete!")
            
            print("\nPress Enter to return to menu...")
            input()
        
        elif choice == '5':
            # Exit
            print("\nThank you for using Desktop Image Organizer!")
            break


if __name__ == "__main__":
    main()

