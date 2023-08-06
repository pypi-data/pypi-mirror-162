"""
Simple File Configuration Parse - by aaronater10

Version 1.3.0

The easy to use library for your data, configuration, and save files.

Import or Export custom, or industry-common, data, config, and save files easily for
your python program or script!

See tutorials and docs here for more info: https://docs.sfcparse.org

Source Code: https://github.com/aaronater10/sfcparse
"""
#########################################################################################################
# Imports

# Native Lib
from .__native.importfile import importfile
from .__native.importfileraw import importfileraw
from .__native.exportfile import exportfile
from .__native.appendfile import appendfile
from .__native.cleanformat import cleanformat

# Hash Lib
from .__hash.createfilehash import createfilehash
from .__hash.comparefilehash import comparefilehash

# JSON Lib
from .__json.jsonimportfile import jsonimportfile
from .__json.jsonimportstr import jsonimportstr
from .__json.jsonexportfile import jsonexportfile
from .__json.jsonexportstr import jsonexportstr

# YAML Lib
from .__yaml.yamlimportfile import yamlimportfile
from .__yaml.yamlimportstr import yamlimportstr
from .__yaml.yamlexportfile import yamlexportfile
from .__yaml.yamlexportstr import yamlexportstr

# INI Lib
from .__ini.iniimportfile import iniimportfile
from .__ini.iniexportfile import iniexportfile
from .__ini.inibuildauto import inibuildauto
from .__ini.inibuildmanual import inibuildmanual

# XML Lib
from .__xml.xmlimportfile import xmlimportfile
from .__xml.xmlimportstr import xmlimportstr
from .__xml.xmlexportfile import xmlexportfile
from .__xml.xmlexportstr import xmlexportstr
from .__xml.xmlbuildmanual import xmlbuildmanual
