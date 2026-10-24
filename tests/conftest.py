"""Settings for every test.

The tests draw windows off screen: nothing appears on Ernie's screen, and
they run the same way on GitHub's computer (spec/window.md, On trust).
"""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
