"""
Objectives:
    
    Add or edit two xml files.
    
0)  Load a rhinoToolbarsConfig.json

1)  Add the path to our hdm.rui to a rhino version specific xml file.
    Rhino will load whatever rui's are specified in the xml.
    In Rhino:
        File>Properties>Toolbars>Files

2)  Add the path to our hdmrhinolib to a rhino-version specific xml file.
    Rhino will load the specified module and make it availabe in the python execution environment (or python editor) - make more precise.
    In Rhino:
        EditPythonScript>Tools>Options>Modules Search Paths
        
Step by step:

    PC has rhino installed. You start your Rhino for the first time and this script will create the lib xml file.
    No standard xml files (the one for toolbars) exist at this time, so the toolbars installer skips.
    You open Rhino.
    When Rhino is closed for the first time it creates all it's other standard xml files.
    You restart your PC and this time the toolbar installer recognizes it's xml and modifies it.
"""
