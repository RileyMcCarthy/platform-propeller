"""
Bare framework for Propeller platforms.
Uses FlexCC as the default toolchain with minimal configuration.
"""

# Import FlexCC framework (does all the heavy lifting)
import os
import sys

# Add the frameworks directory to the path so we can import flexcc
frameworks_dir = os.path.dirname(__file__)
if frameworks_dir not in sys.path:
    sys.path.append(frameworks_dir)

# Import and execute flexcc framework
import flexcc
