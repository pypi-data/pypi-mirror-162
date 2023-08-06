def oxygen_install():
    print("Downloading Nitrogen (installer for Oxygen)...")
    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/arjunj132/oxygen/main/nitrogen.py", "nitrogen.py")
    exec(open("nitrogen.py").read())

def oxygen_run():
    exec(open("nitrogen.py").read())