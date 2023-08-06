import sys
from flockfysh.config import BASE_DIR
import os 
import glob 

name = "flockfysh"

sys.path.append(os.path.abspath(BASE_DIR))

for pth in [ f.name for f in os.scandir(os.path.join(BASE_DIR, 'scraper')) if f.is_dir() ]:
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, 'scraper', pth)))
for pth in [ f.name for f in os.scandir(os.path.join(BASE_DIR, 'utilities')) if f.is_dir() ]:
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, 'utilities', pth)))
