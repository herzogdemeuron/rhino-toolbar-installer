"""
Objectives:
    
    Add or edit two xml files.
    
0)  Load a rhinoToolbarsConfig.json

1)  Add the path to a .rui to a rhino version specific xml file.
    Rhino will load whatever rui's are specified in the xml.
    In Rhino:
        File>Properties>Toolbars>Files

2)  Add the path to a lib to a rhino-version specific xml file.
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
import os
import xml.etree.ElementTree as ET 
from pathlib import Path
import json


def load_config():
    path = Path(os.getcwd())
    parent_dir = path.parent.absolute()
    with open(os.path.join(parent_dir, 'rhinoToolbarsConfig.json'), 'r') as f:
        config = json.load(f)

    return config

def xml_add_settings_toolbar(tag, filepath, new_path):
    #enter xml file
    try:
        xmlTree = ET.parse(filepath)
    except:
        print ("install.xml_add_settings_toolbar / ERROR: Parse error! Contact DT")
        return False
    xmlRoot = xmlTree.getroot()
    newitems = []

    #test if tag exists in xml file
    entryMatch = None
    for element in xmlRoot.findall("./settings"):
        childs = list(element)
        for child in childs:
            entries = list(child)
            for entry in entries:
                if entry.items()[0][1] == tag:
                    entryMatch = entry
    
    # return false if not found
    if entryMatch == None:
        print ("install.xml_add_settings_toolbar / INFO: " + tag + " not found in xml file.")
        return False
    
    # enter list and values of tag entry

    values = list(entryMatch[0])
    for value in values:
        # check if path already exists in xml file
        if value.text == new_path:
            print ("install.xml_add_settings_toolbar / SUCCESS: Xml toolbar already installed.")
            return False

    # add new value to xml file
    newValue = ET.Element("value")
    newValue.text = new_path
        
    newValue = entryMatch[0].append(newValue)

    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    return True

def xml_add_settings_lib(tag, filepath, new_path):
    #enter xml file
    try:
        xmlTree = ET.parse(filepath)
    except:
        print ("install.xml_add_settings_lib / ERROR: Parse error! Contact DT")
        return False
    xmlRoot = xmlTree.getroot()
    newitems = []

    #test if tag exists in xml file
    entryMatch = None
    for element in xmlRoot.findall("./settings"):
        entries = list(element)
        for entry in entries:
            if entry.items()[0][1] == tag:
                entryMatch = entry
    # if the xml entry is not found, creates new xml entry
    if entryMatch == None:
        print ("install.xml_add_settings_lib / INFO: " + tag + " not found in xml file")
        newValue = ET.Element("entry", {"key":tag})
        newValue.text = new_path
        element.append(newValue)
        print ("install.xml_add_settings_lib / INFO: " + tag + " entry created")
        xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
        return True
    
    # write lib path to xml file
    if entryMatch.text == None:
        entryMatch.text = new_path
    
    elif new_path in entryMatch.text:
        print ("install.xml_add_settings_lib / SUCCESS: Xml lib already installed.")
        return False
    else:
        entryMatch.text += ";" + new_path

    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    return True
    
def xml_write_lib(ironPythonXML, default_search_path):
    # Default pythonlib xml
    pythonlib_xml = '<?xml version="1.0" encoding="utf-8"?>\n\
    <settings id="2.0">\n\t\
        <settings>\n\t\t\
            <entry key="SearchPaths">{}</entry>\n\t\
        </settings>\n\
    </settings>'.format(default_search_path)

    print ("install.xml_write_lib / SUCCESS: First run. Lib xml created.")

    f = open(ironPythonXML, 'w')
    f.write(pythonlib_xml)
    f.close()

def install(config):
    print("install.install / INFO: Intalling RhinoToolbar...")
    for version in config['rhinoVersionPaths']:
        toolbars = version['toolbars']
        toolbarsXMLdir = os.path.join(os.getenv('APPDATA'), version['toolbarsXMLdir'])
        toolbarsXML = os.path.expandvars(toolbarsXMLdir + '/settings-Scheme__Default.xml')
        if not os.path.isfile(toolbarsXML):
            print ("install.install / WARNING: Rhino never started. Toolbar not installed.")
        else:
            for toolbar in toolbars:
                if xml_add_settings_toolbar(
                    "RuiFiles", toolbarsXML, toolbar['rui']):
                    print("install.install_toolbar / SUCCESS: Modified rhino rui xml.")
                else:
                    print("install.install_toolbar / INFO: No changes made to toolbar xml.")

        ironPythonXMLdir = os.path.join(os.getenv('APPDATA'), version['ironPythonXMLdir'])
        ironPythonXML = os.path.expandvars(ironPythonXMLdir + '/settings-Scheme__Default.xml')
        if os.path.exists(ironPythonXMLdir):
            print("install.install_lib / INFO: xml folder path exists.")
        else:
            os.makedirs(ironPythonXMLdir)

        if not os.path.isfile(ironPythonXML):
            xml_write_lib(ironPythonXML, default_search_path=toolbars[0]['lib'])

        for toolbar in toolbars:
            lib_settings = xml_add_settings_lib(
                "SearchPaths", ironPythonXML, toolbar['lib'])
            if lib_settings:
                print ("install.install_lib / INFO: lib path added.")
                print("install.install_lib / SUCCESS: Modified rhino python xml.")
            else:
                print ("install.install_lib / INFO: No changes made to lib xml.")


if __name__ == "__main__":
    config = load_config()
    install(config)