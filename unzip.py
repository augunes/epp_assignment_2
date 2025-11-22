import zipfile
from pathlib import Path
import pandas as pd

# modern pandas settings
pd.options.mode.copy_on_write = True

def unzip_original_data(zip_path: Path, target_dir: Path) -> None:
    """
    Extract the compressed original data to the specified target directory.

    This function takes the path to the source zip file and the destination
    folder. It creates the destination folder if it does not exist and
    unpacks all contents of the archive into it.
    """
    # No side effects on inputs
    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    
    # UPDATED LINE: Removed "src" to match your specific folder structure
    zip_path = project_root / "original_data" / "original_data.zip"
    bld_dir = project_root / "bld"

    unzip_original_data(zip_path, bld_dir)
