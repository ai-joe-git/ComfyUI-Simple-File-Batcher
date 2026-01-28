import os
import folder_paths
from pathlib import Path

class SimpleFileBatcher:
    """
    A simple file batcher that lists files from a folder with filtering and sorting options
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "file_filter": (["all", "images", "videos", "text"],),
                "sort_by": (["name_asc", "name_desc", "date_asc", "date_desc", "size_asc", "size_desc"],),
            },
            "optional": {
                "file_extension": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Comma-separated extensions (e.g., .png,.jpg). Leave empty to use file_filter"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("file_list", "file_path_list")
    FUNCTION = "batch_files"
    CATEGORY = "utils"

    def get_file_extensions(self, file_filter, custom_extension=""):
        """Get file extensions based on filter type"""
        if custom_extension.strip():
            # User provided custom extensions
            exts = [ext.strip() for ext in custom_extension.split(",")]
            return [ext if ext.startswith(".") else f".{ext}" for ext in exts]

        # Predefined filters
        filters = {
            "images": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"],
            "videos": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"],
            "text": [".txt", ".md", ".json", ".yaml", ".yml", ".csv", ".log"]
        }

        return filters.get(file_filter, [])

    def list_files(self, folder_path, extensions):
        """List all files in folder with given extensions"""
        files = []

        try:
            # Handle relative paths or use ComfyUI input directory
            if not folder_path or not os.path.isabs(folder_path):
                base_path = folder_paths.get_input_directory()
                folder_path = os.path.join(base_path, folder_path) if folder_path else base_path

            if not os.path.exists(folder_path):
                return []

            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                if not os.path.isfile(file_path):
                    continue

                # Check if file matches extensions
                if extensions:
                    if any(file.lower().endswith(ext.lower()) for ext in extensions):
                        files.append(file_path)
                else:
                    # No filter, include all files
                    files.append(file_path)

        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

        return files

    def sort_files(self, files, sort_by):
        """Sort files based on sort_by parameter"""
        if not files:
            return files

        if sort_by == "name_asc":
            return sorted(files, key=lambda x: os.path.basename(x).lower())
        elif sort_by == "name_desc":
            return sorted(files, key=lambda x: os.path.basename(x).lower(), reverse=True)
        elif sort_by == "date_asc":
            return sorted(files, key=lambda x: os.path.getmtime(x))
        elif sort_by == "date_desc":
            return sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
        elif sort_by == "size_asc":
            return sorted(files, key=lambda x: os.path.getsize(x))
        elif sort_by == "size_desc":
            return sorted(files, key=lambda x: os.path.getsize(x), reverse=True)

        return files

    def batch_files(self, folder_path, file_filter, sort_by, file_extension=""):
        """Process files in batch"""
        # Get extensions to filter
        extensions = self.get_file_extensions(file_filter, file_extension)

        # List and filter files
        files = self.list_files(folder_path, extensions)

        # Sort files
        files = self.sort_files(files, sort_by)

        if len(files) == 0:
            return ("No files found", "")

        # Create file list with numbered filenames
        file_list = "\n".join([f"{i}: {os.path.basename(f)}" for i, f in enumerate(files)])

        # Create file path list with full paths only (no spaces between lines)
        file_path_list = "\n".join(files)

        return (file_list, file_path_list)


NODE_CLASS_MAPPINGS = {
    "SimpleFileBatcher": SimpleFileBatcher
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleFileBatcher": "Simple File Batcher"
}
