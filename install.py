"""
Objectives:
    
    Add or edit two xml files.
    
0)  Load a rhinoToolbarsConfig.json that contains libs and ruis previously added to xmls with this installer.

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
import json
import logging


def load_config(directory):
    config_path = os.path.join(directory, 'rhinoToolbarsConfig.json')
    config = dict()
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                logging.error("install.load_config / JSONDecodeError / Using default config.")

    config[ "rhinoVersionPaths"] =  [
        {
        "toolbarsXMLdir": "McNeel/Rhinoceros/7.0/Plug-ins/Toolbars (dc297053-96c0-4883-a688-8326b4e024a8)/settings",
        "ironPythonXMLdir": "McNeel/Rhinoceros/7.0/Plug-ins/IronPython (814d908a-e25c-493d-97e9-ee3861957f49)/settings"
        }
    ]
    return config

def write_config(directory, config):
    config_path = os.path.join(directory, 'rhinoToolbarsConfig.json')
    with open(config_path, 'w') as f:
        f.write(json.dumps(config))

def collect_ruis(search_dir):
    """
    Searches for all files ending with '.rui' in give directory tree.

    Args:
        search_dir (str): The root directory to start searching from.

    Returns:
        list[str]: A list of file paths.
    """
    ruis = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".rui"):
                ruis.append(os.path.join(root, file))

    return ruis

def collect_libs(search_dir):
    """
    Searches for all 'lib' folders in given directory tree.
    Ignores directories that to not have 'rhino' in their path.

    Args:
        search_dir (str): The root dir to start searching from.

    Returns:
        list[str]: A list of directories.
    """
    libs = []
    for root, dirs, files in os.walk(search_dir):
        for directory in dirs:
            if 'rhino' in root.lower() and directory == 'lib':
                libs.append(os.path.join(root, directory))
    
    return libs

def xml_add_settings_toolbar(filepath, new_ruis, remove_ruis):
    """
    Add new values to an xml file under a specific tag.
    Performs boolean operations on the remove_ruis vs new_ruis to figure out which entries to keep, remove or add.

    Args:
        filepath (str): The path to the xml file.
        new_ruis (list[str]): The values to be added to the xml file.
        remove_ruis (list[str]): The values to remove before adding new ones to the xml file.

    Returns:
        bool: Return True if the new value is added successfully and False otherwise.
    """
    #enter xml file
    try:
        xmlTree = ET.parse(filepath)
    except:
        logging.info("install.xml_add_settings_toolbar / Parse error!")
        return False

    # get RuiFiles entry
    xmlRoot = xmlTree.getroot()
    entryMatch = xmlRoot.find(".//entry[@key='RuiFiles']")
    
    if entryMatch != None:
        ruis = set(value.text for value in entryMatch[0])
        if remove_ruis:
            ruis = ruis - set(remove_ruis)
        ruis = ruis | set(new_ruis)
    else:
        logging.info("install.xml_add_settings_toolbar / No entry '{}' found. No changes made to toolbar xml.".format(tag))
        return

    entryMatch[0].clear()
    # add new value to xml file
    for rui in ruis:
        newValue = ET.Element("value")
        newValue.text = rui
        newValue = entryMatch[0].append(newValue)

    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    return

def xml_add_settings_lib(filepath, new_paths, remove_paths=None):
    """
    Add new values to an xml file under a specific tag or create a new tag if it doesn't exist.
    Performs boolean operations on the remove_paths vs new_paths to figure out which entries to keep, remove or add.

    Args:
        filepath (str): The path to the xml file.
        new_paths (list[str]): The values to be added to the xml file.
        remove_paths (list[str], optional): The values to be removed from the xml file before adding new ones.

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
    entryMatch = xmlRoot.find(".//entry[@key='SearchPaths']")

    # if the xml entry is not found, creates new xml entry
    if entryMatch == None:
        settings = xmlRoot.find("./settings")
        settings.append(ET.Element("entry", {"key":"SearchPaths"}))
        logging.info("install.xml_add_settings_lib / 'SearchPaths' entry created")

        # get newly created SearchPath entry. Not sure if this is needed of of new entry could be used directly.
        entryMatch = xmlRoot.find(".//entry[@key='SearchPaths']")

    # write lib path to xml file
    if entryMatch.text != None:
        search_paths = set(entryMatch.text.split(';'))
        if remove_paths:
            search_paths = search_paths - set(remove_paths)
        search_paths = search_paths | set(new_paths)
    else:
        search_paths = new_paths

    entryMatch.text = ';'.join(search_paths)
    xmlTree.write(filepath, encoding='utf-8', xml_declaration=True)
    logging.info("install.xml_add_settings_lib / SearchPaths modified")
    return
    
def xml_write_lib(ironPythonXML, default_search_path):
    """
    Writes a new xml file with specific values.

    Args:
        ironPythonXML (str): The path of the xml file to be written.
        default_search_path (str): The value to be written in the xml file.
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

def install(config, search_dir):
    """
    Installs RhinoToolbars by modifying xml files.
    See this repo's README for further information. 
    
    Args:
        config (dict): A dictionary containing the version paths, libs and toolbars information.
    """
    logging.info("install.install / Installing RhinoToolbar...")
    new_libs = collect_libs(search_dir)
    logging.info("install.install / New Libs: {}".format(new_libs))

    remove_libs = config.get('libs', None)
    if remove_libs:
        logging.info("install.install / Remove Libs: {}".format(remove_libs))

    new_ruis = collect_ruis(search_dir)
    logging.info("install.install / New Ruis: {}".format(new_ruis))
    remove_ruis = config.get('ruis', None)
    if remove_ruis:
        logging.info("install.install / Remove Ruis: {}".format(remove_ruis))

    for version in config['rhinoVersionPaths']:
        toolbarsXMLdir = os.path.join(os.getenv('APPDATA'), version['toolbarsXMLdir'])
        toolbarsXML = os.path.expandvars(toolbarsXMLdir + '/settings-Scheme__Default.xml')

        ironPythonXMLdir = os.path.join(os.getenv('APPDATA'), version['ironPythonXMLdir'])
        ironPythonXML = os.path.expandvars(ironPythonXMLdir + '/settings-Scheme__Default.xml')

        if not os.path.isfile(toolbarsXML):
            logging.warning("No toolbar xml detected, Rhino never started. Toolbar not installed.")
        else:
            xml_add_settings_toolbar(toolbarsXML, new_ruis, remove_ruis)

        if os.path.exists(ironPythonXMLdir):
            logging.info("install.install / IronPython xml folder path already exists.")
        else:
            os.makedirs(ironPythonXMLdir)
            logging.info("install.install / Added ironPython xml folder.")

        if not os.path.isfile(ironPythonXML):
            xml_write_lib(ironPythonXML, default_search_path=new_libs[0])

        xml_add_settings_lib(ironPythonXML, new_libs, remove_libs)
    
    config['libs'] = new_libs
    config['ruis'] = new_ruis

    return config


if __name__ == "__main__":
    currentFile = os.path.abspath(__file__)
    directory = os.path.dirname(currentFile)
    logfile = os.path.join(directory, 'install.log')
    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    logging.info('=====================')
    config = load_config(directory)
    config = install(config, 'C:\\HdM-DT')
    write_config(directory, config)
