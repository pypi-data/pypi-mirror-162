# xmlexportfile
#########################################################################################################
# Imports
from ..__native.exportfile import exportfile
from .xmlexportstr import xmlexportstr
import xml.etree.ElementTree as __xml_etree
from ..error import SfcparseError

# Exception for Module
class XmlExportFile(SfcparseError): __module__ = SfcparseError.set_module_name()

#########################################################################################################
# Export xml file
def xmlexportfile(filename: str, data: __xml_etree.Element) -> None:
    """
    Exports a new file from xml Element obj as xml data
    
    Enter new filename as str. Pass ElementTree data for output to file
    
    [Example Use]

    xmlexportfile('path/to/filename.xml', Element_data)

    This is using the native xml library via etree shipped with the python standard library.
    For more information on the xml.etree api, visit: https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
    """
    # Check for Error
    __err_msg_str = f"Only str is allowed for filename"
    __err_msg_etree = f"Only Element is allowed for data"

    if not isinstance(filename, str): raise XmlExportFile(__err_msg_str, f'\nFILE: "{filename}"')
    if not isinstance(data, __xml_etree.Element): raise XmlExportFile(__err_msg_etree, f"\nDATA: {data}")

    # Export Data
    try:
        data = xmlexportstr(data)
        exportfile(filename, data)
    except FileNotFoundError as __err_msg: raise XmlExportFile(__err_msg, f'\nFILE: "{filename}"')
