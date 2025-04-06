"""This file imports modules in other dirs"""

import sys
import os

module_path_a = os.path.abspath(os.path.join(os.pardir, '../Analysis/Scripts'))
if module_path_a not in sys.path:
    sys.path.append(module_path_a)
