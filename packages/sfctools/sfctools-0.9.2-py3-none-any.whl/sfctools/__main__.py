from sfctools.gui import Gui
import sys


if len(sys.argv) > 1 and sys.argv[1] == "attune":
    g = Gui()
    g.run()
else:
    print("""
============= WELCOME TO SFCTOOLS ============================
ver. 0.9 -
Main corresponding author: Thomas, thomas.baldauf@dlr.de
Institute of Networked Energy Systems (DLR-VE)
German Aerospace Center, 2020
==============================================================

See https://sfctools-framework.readthedocs.io/en/latest/ for the latest documentation
See https://gitlab.com/dlr-ve/esy/sfctools for the latest version on gitlab

Type 'sfctools attune' to start the graphcial user interface attune
""")
