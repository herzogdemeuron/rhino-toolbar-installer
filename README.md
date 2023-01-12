# rhino-toolbar-installer
Generic installer for adding toolbars to Rhino

---

**How to use:**

Place a 'rhinoToolbarsConfig.json' in the parent directory of this repo. See the 'rhinoToolbarsConfig_example.json' for reference. Pay attention to the use for / vs. \.

Edit the 'rhinoToolbarsConfig.json:
  * Set the 'rhinoVersionPaths for the toolbarXML and ironPythonXML according to the paths on your machine.
  * Add the paths to the 'lib' and 'rui' for all toolbars you want to install.

Run the install.py manually or by any other automated method.
