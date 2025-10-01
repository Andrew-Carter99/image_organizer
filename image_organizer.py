import os
import shutil
import string
from pathlib import Path
from datetime import datetime


class DesktopImageOrganizer:
    """
    Organizes image files from multiple drives into a centralized folder structure.
    """
    
    # Common image file extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', 
                       '.tif', '.webp', '.svg', '.ico', '.heic', '.raw', 
                       '.cr2', '.nef', '.orf', '.sr2'}
    
    def __init__(self, destination_folder_name="Photos to Clean"):
        """
        Initialize the organizer.
        
        Args:
            destination_folder_name: Name of the folder to create on desktop
        """
        self.destination_folder_name = destination_folder_name
        self.desktop_path = Path.home() / "Desktop"
        self.destination_path = self.desktop_path / destination_folder_name
        self.log_messages = []
        self.stats = {
            'total_found': 0,
            'total_moved': 0,
            'total_errors': 0,
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
        
        # Skip if already in destination folder
        if str(self.destination_path).lower() in path_str:
            return True
        
        # Skip system and hidden directories
        skip_dirs = [
            'windows', 'program files', 'program files (x86)',
            'programdata', '$recycle.bin', 'system volume information',
            'recovery', 'perflogs', 'boot', 'appdata'
        ]
        
        for skip_dir in skip_dirs:
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
            # Handle filename conflicts
            destination_file = destination_folder / source_path.name
            if destination_file.exists():
                # Add timestamp to filename if conflict exists
                stem = source_path.stem
                suffix = source_path.suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
    
    def save_log(self):
        """Save log messages to a file in the destination folder."""
        log_file = self.destination_path / f"organize_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_messages))
            self.log(f"Log saved to: {log_file}")
        except Exception as e:
            print(f"Error saving log: {str(e)}")


def main():
    """Main entry point."""
    print("Desktop Image Organizer")
    print("=" * 70)
    print()
    print("This script will:")
    print("1. Scan all drives on your computer for image files")
    print("2. Move them to 'Photos to Clean' folder on your desktop")
    print("3. Organize them into subfolders by drive")
    print()
    print("WARNING: This will move files from their current locations!")
    print()
    
    # Ask for confirmation
    response = input("Do you want to run a DRY RUN first? (y/n): ").strip().lower()
    
    organizer = DesktopImageOrganizer()
    
    if response == 'y':
        print("\nRunning DRY RUN (no files will be moved)...\n")
        organizer.organize_images(dry_run=True)
        print()
        response = input("Do you want to proceed with the actual move? (y/n): ").strip().lower()
        if response != 'y':
            print("Operation cancelled.")
            return
        
        # Create new organizer instance for actual run
        organizer = DesktopImageOrganizer()
    
    print("\nStarting image organization...\n")
    organizer.organize_images(dry_run=False)
    print("\nComplete!")


if __name__ == "__main__":
    main()

