import sys
import os

def oxygen_install():
    print("Downloading Nitrogen (installer for Oxygen)...")
    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/arjunj132/oxygen/main/nitrogen.py", "nitrogen.py")
    print("Run this command:\n      python3 nitrogen.py\n      py nitrogen.py")