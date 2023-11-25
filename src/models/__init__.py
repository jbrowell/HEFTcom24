import os
import sys

from dotenv import load_dotenv

load_dotenv()

root = os.getenv("root")
src = os.path.join(root, "src")
sys.path.append(src)

import loaders
import utils
from config import *

from .base import *
