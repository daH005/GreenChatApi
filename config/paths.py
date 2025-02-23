from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

__all__ = (
    'BASE_DIR',
    'STATIC_FOLDER',
    'MEDIA_FOLDER',
)

BASE_DIR: Path = Path(__file__).resolve().parent.parent  # '.../api'
STATIC_FOLDER: Path = BASE_DIR.joinpath('static')
MEDIA_FOLDER: Path = BASE_DIR.joinpath('media')
