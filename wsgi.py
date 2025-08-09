# This file is used by PythonAnywhere to hook into the web application.

import sys
from webapp.main import app as application

# Add the project directory to the sys.path
path = '/home/YourUserName/path/to/your/project' # Needs to be changed by the user
if path not in sys.path:
    sys.path.insert(0, path)
