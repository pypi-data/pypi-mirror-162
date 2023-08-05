"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import os
import pathlib
from nanosurf._version import __version__
from nanosurf.lib.spm import *
from nanosurf.lib.spm.studio import *


class Studio(StudioScriptSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SPM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("SPM.Application", *args, **kwargs)

class USPM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("USPM.Application", *args, **kwargs)

class CX(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("CX.Application", *args, **kwargs)

class C3000(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("C3000.Application", *args, **kwargs)

class Naio(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("Naio.Application", *args, **kwargs)

class CoreAFM(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("CoreAFM.Application", *args, **kwargs)

class Easyscan2(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("Easyscan2.Application", *args, **kwargs)

class MobileS(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("MobileS.Application", *args, **kwargs)

class SPM_S(Spm):
    def __init__(self, *args, **kwargs):
        super().__init__("SPM_S.Application", *args, **kwargs)

def package_path() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

def doc_path() -> pathlib.Path:
    return package_path() / "doc"

def lib_path() -> pathlib.Path:
    return package_path() / "lib"

def app_path() -> pathlib.Path:
    return package_path() / "app"

def help(): 
    print("Nanosurf python script package:")
    print("-------------------------------")
    print(f"Installed version: {__version__}")
    print("\nThe library documentation is here:")
    print(doc_path())
    for doc in os.listdir(doc_path()):
        print(f"  {doc}")
    print("\nThe demos and apps are stored here:")
    print(app_path())
    for demo in os.listdir(app_path()):
        print(f"  {demo}")


