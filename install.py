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
import logging


def load_config():
    path = Path(os.getcwd())
    logging.info("Looking for config json in current working dir: {}".format(path))
    with open(os.path.join(path, 'rhinoToolbarsConfig.json'), 'r') as f:
        config = json.load(f)

    return config

def xml_add_settings_toolbar(tag, filepath, new_path):
    """
    Add a new value to an xml file under a specific tag.

    Args:
        tag (str): The name of the tag to add the new value to.
        filepath (str): The path to the xml file.
        new_path (str): The value to be added to the xml file.

    Returns:
        bool: Return True if the new value is added successfully and False otherwise.
    """
    #enter xml file
    try:
        xmlTree = ET.parse(filepath)
    except:
        logging.info("install.xml_add_settings_toolbar / Parse error!")
        return False

    #test if tag exists in xml file
    xmlRoot = xmlTree.getroot()
    entryMatch = None
    for element in xmlRoot.findall("./settings"):
        childs = list(element)
        for child in childs:
            entries = list(child)
            for entry in entries:
                if entry.items()[0][1] == tag:
                    entryMatch = entry
    
    # return if not found
    if entryMatch == None:
        logging.info("install.xml_add_settings_toolbar / " + tag + " not found in xml file.")
        logging.info("install.xml_add_settings_toolbar / No changes made to toolbar xml.")
        return
    
    # enter list and values of tag entry
    values = list(entryMatch[0])
    for value in values:
        # check if path already exists in xml file
        if value.text == new_path:
            logging.info("install.xml_add_settings_toolbar / '{}' already in toolbar xml.".format(new_path))
            logging.info("install.xml_add_settings_toolbar / No changes made to toolbar xml.")
            return

    # add new value to xml file
    newValue = ET.Element("value")
    newValue.text = new_path
    newValue = entryMatch[0].append(newValue)

    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    logging.info("install.xml_add_settings_toolbar / Inserted '{}' into rhino rui xml.".format(new_path))
    return

def xml_add_settings_lib(tag, filepath, new_path):
    """
    Add a new value to an xml file under a specific tag or create a new tag if it doesn't exist.

    Args:
        tag (str): The name of the tag to add the new value to or the name of the tag to be created.
        filepath (str): The path to the xml file.
        new_path (str): The value to be added to the xml file.

    Returns:
        bool: Return True if the new value is added successfully and False otherwise.
    """
    #enter xml file
    try:
        xmlTree = ET.parse(filepath)
    except:
        logging.error("install.xml_add_settings_lib / Parse error!")
        logging.info("install.xml_add_settings_lib / No changes made to lib xml.")
        return

    #test if tag exists in xml file
    xmlRoot = xmlTree.getroot()
    entryMatch = None
    for element in xmlRoot.findall("./settings"):
        entries = list(element)
        for entry in entries:
            if entry.items()[0][1] == tag:
                entryMatch = entry

    # if the xml entry is not found, creates new xml entry
    if entryMatch == None:
        logging.info("install.xml_add_settings_lib / " + tag + " not found in xml file")
        newValue = ET.Element("entry", {"key":tag})
        newValue.text = new_path
        element.append(newValue)
        xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
        logging.info("install.xml_add_settings_lib / " + tag + " entry created")
        return
    
    # write lib path to xml file
    if entryMatch.text == None:
        entryMatch.text = new_path
    elif new_path in entryMatch.text:
        logging.info("install.xml_add_settings_lib / '{}' already in ironPython libs xml.".format(new_path))
        logging.info("install.xml_add_settings_lib / No changes made to ironPython lib xml.")
        return
    else:
        entryMatch.text += ";" + new_path

    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    logging.info("install.xml_add_settings_lib / Inserted '{}' into ironPython lib xml.".format(new_path))
    return
    
def xml_write_lib(ironPythonXML, default_search_path):
    """
    Writes a new xml file with specific values.

    Args:
        ironPythonXML (str): The path of the xml file to be written.
        default_search_path (str): The value to be written in the xml file.

    Returns:
        None
    """
    # Default pythonlib xml
    pythonlib_xml = '<?xml version="1.0" encoding="utf-8"?>\n\
    <settings id="2.0">\n\t\
        <settings>\n\t\t\
            <entry key="SearchPaths">{}</entry>\n\t\
        </settings>\n\
    </settings>'.format(default_search_path)

    with open(ironPythonXML, 'w') as f:
        f.write(pythonlib_xml)
        logging.info("install.xml_write_lib / First run. Lib xml created.")

def install(config):
    """
    Installs RhinoToolbars by modifying xml files.
    Specify the toolbars and xml files in a json configuration. See this repo's README for further information. 
    
    Args:
        config (dict): A dictionary containing the version paths and toolbars information.
    
    Returns:
        None
    """
    logging.info("install.install / Installing RhinoToolbar...")

    for version in config['rhinoVersionPaths']:

        toolbars = config['toolbars']
        toolbarsXMLdir = os.path.join(os.getenv('APPDATA'), version['toolbarsXMLdir'])
        toolbarsXML = os.path.expandvars(toolbarsXMLdir + '/settings-Scheme__Default.xml')

        ironPythonXMLdir = os.path.join(os.getenv('APPDATA'), version['ironPythonXMLdir'])
        ironPythonXML = os.path.expandvars(ironPythonXMLdir + '/settings-Scheme__Default.xml')

        if not os.path.isfile(toolbarsXML):
            logging.warning("No toolbar xml detected, Rhino never started. Toolbar not installed.")
        else:
            for toolbar in toolbars:
                xml_add_settings_toolbar(
                    "RuiFiles", toolbarsXML, toolbar['rui'])

        if os.path.exists(ironPythonXMLdir):
            logging.info("install.install / IronPython xml folder path already exists.")
        else:
            os.makedirs(ironPythonXMLdir)
            logging.info("install.install / Added ironPython xml folder.")

        if not os.path.isfile(ironPythonXML):
            xml_write_lib(ironPythonXML, default_search_path=toolbars[0]['lib'])

        for toolbar in toolbars:
            xml_add_settings_lib(
                "SearchPaths", ironPythonXML, toolbar['lib'])


if __name__ == "__main__":
    logging.basicConfig(filename='install.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    logging.info('=====================')
    config = load_config()
    install(config)