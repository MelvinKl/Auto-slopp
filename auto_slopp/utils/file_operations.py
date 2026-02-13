import shutil
from pathlib import Path


def copy_file(src: Path, dst: Path) -> bool:
    """Copy a file from source to destination.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        True if successful, False otherwise.
    """
    try:
        shutil.copy2(src, dst)
        return True
    except IOError, OSError:
        return False


def move_file(src: Path, dst: Path) -> bool:
    """Move a file from source to destination.

    Args:
        src: Source file path.
        dst: Destination file path.

    Returns:
        True if successful, False otherwise.
    """
    try:
        shutil.move(src, dst)
        return True
    except IOError, OSError:
        return False


def delete_file(path: Path) -> bool:
    """Delete a file.

    Args:
        path: File path to delete.

    Returns:
        True if successful, False otherwise.
    """
    try:
        path.unlink()
        return True
    except IOError, OSError:
        return False


def ensure_directory(path: Path) -> bool:
    """Ensure a directory exists.

    Args:
        path: Directory path.

    Returns:
        True if successful, False otherwise.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False
