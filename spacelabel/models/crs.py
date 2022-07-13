from pathlib import Path
from tfcat import CRS as TFCatCRS
from json import load

CRS_FILE = Path(__file__).parent / "crs.json"

with open(CRS_FILE, 'r') as f:
    crs = load(f)

CRS = TFCatCRS(crs)
