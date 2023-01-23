# rhino-toolbar-installer
*Generic installer for adding repository-based toolbars to Rhino. It collects all 'lib' folders and all '.rui' files in it's parent directory and all subdirectories thereof and adds their paths to the respective xml file in the Rhino plug-ins folder.*

**How to use:**

Clone this repo into C:\HdM-DT\RhinoToolbarExtensions. This is the mandatory location for all HdM Rhino repositories. RUI files rely on absolute paths to call python scripts.

Place a 'rhinoToolbarsConfig.json' in the parent directory of this repo. See the 'rhinoToolbarsConfig_example.json' for reference. Pay attention to the use for '/' vs. '\\'.

Edit the 'rhinoToolbarsConfig.json:
  * Set the 'rhinoVersionPaths for the toolbarXML and ironPythonXML according to the paths on your machine.

Run the install.py manually or by any other automated method.

In Rhino: Right-click on any toolbar>Show Toolbar>Check toolbar you want to show. All HdM toolbars on GibHub are hidden by default.
