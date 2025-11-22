from pathlib import Path
import zipfile

def ensure_bld_directory(base_path: Path) -> Path:
    """
    Ensure that the build (bld) directory exists in the project root.

    Parameters
    ----------
    base_path : pathlib.Path
        Path to the project root directory.

    Returns
    -------
    pathlib.Path
        Path to the existing or newly created bld directory.
    """
    bld_path = base_path / "bld"
    bld_path.mkdir(exist_ok=True)
    return bld_path


def unzip_original_data(zip_path: Path, output_dir: Path) -> None:
    """
    Unzip the contents of original_data.zip into the bld directory.

    Parameters
    ----------
    zip_path : pathlib.Path
        Path to the ZIP file located in original_data/original_data.zip.

    output_dir : pathlib.Path
        The directory where the extracted files will be written.
        Must be the bld directory.

    Returns
    -------
    None
    """
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(output_dir)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]

    zip_file = project_root / "src" / "original_data" / "original_data.zip"
    bld_dir = ensure_bld_directory(project_root)

    unzip_original_data(zip_file, bld_dir)

