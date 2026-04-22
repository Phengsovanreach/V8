import os

def clean_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass