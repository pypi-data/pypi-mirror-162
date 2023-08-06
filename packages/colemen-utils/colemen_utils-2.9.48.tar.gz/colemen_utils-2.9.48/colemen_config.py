# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-import
# pylint: disable=invalid-name

import platform
import os
from typing import TypeVar as _TypeVar
from typing import TYPE_CHECKING
from typing import Iterable as _Iterable
from typing import Union as _Union


from colorama import Fore as _Fore
from colorama import Style as _Style


INFLECT_ENGINE = None
_os_platform = platform.system()
_os_divider = os.path.sep
_drawing_type = None
_diagram_type = None
_nodebase_type = None
_connector_type = None
_onode_type = None
_mxcell_type = None
_element_type = None
_inflect_engine_type = None

# ================================================== database_utils.drawio - types
_db_dio_parser_type = None
_db_dio_row_type = None
_db_dio_table = None
_db_dio_foreign_key_type = None
_db_dio_schema_type = None
# ================================================== database_utils.drawio - types



if TYPE_CHECKING:
    import colemen_utilities.database_utils.drawio.Parser as _db_parser
    _db_dio_parser_type = _TypeVar('_db_dio_parser_type', bound=_db_parser.Parser)

    import colemen_utilities.database_utils.drawio.Row as _db_drw_row
    _db_dio_row_type = _TypeVar('_db_dio_row_type', bound=_db_drw_row.Row)

    import colemen_utilities.database_utils.drawio.Schema as _db_drw_sch
    _db_dio_schema_type = _TypeVar('_db_dio_schema_type', bound=_db_drw_sch.Schema)

    from colemen_utilities.database_utils.drawio.Table import Table as _drwtable
    _db_dio_table = _TypeVar('_db_dio_table', bound=_drwtable)

    from colemen_utilities.database_utils.drawio.ForeignKey import ForeignKey as _fkEnt
    _db_dio_foreign_key_type = _TypeVar('_db_dio_foreign_key_type', bound=_fkEnt)

    import colemen_utilities.drawio.Drawing as _drawing
    _drawing_type = _TypeVar('_drawing_type', bound=_drawing.Drawing)

    import colemen_utilities.drawio.Diagram as _dia
    _diagram_type = _TypeVar('_diagram_type', bound=_dia.Diagram)

    import colemen_utilities.drawio.NodeBase as _nodebase
    _nodebase_type = _TypeVar('_nodebase_type', bound=_nodebase)

    import colemen_utilities.drawio.Connector as _connector
    _connector_type = _TypeVar('_connector_type', bound=_connector.Connector)

    import colemen_utilities.drawio.Onode as _onode
    _onode_type = _TypeVar('_onode_type', bound=_onode.Onode)

    import colemen_utilities.drawio.Mxcell as _mxCell
    _mxcell_type = _TypeVar('_mxcell_type', bound=_mxCell.Mxcell)

    from lxml import etree as _etree
    _element_type = _TypeVar('_element_type', bound=_etree.Element)



    import inflect as _inflect
    _inflect_engine_type = _TypeVar('_inflect_engine_type', bound=_inflect.engine)



_CONFIG = {
    "verbose":True,
}

def get(key,default_value=None):
    if key in _CONFIG:
        return _CONFIG[key]
    return default_value


def log(message,style=None):
    if get("verbose",False):
        if style is None:
            print(message)
        if style == "error":
            print(_Fore.RED + message + _Style.RESET_ALL)
        if style == "success":
            print(_Fore.GREEN + message + _Style.RESET_ALL)
        if style == "cyan":
            print(_Fore.CYAN + message + _Style.RESET_ALL)
        if style == "magenta":
            print(_Fore.MAGENTA + message + _Style.RESET_ALL)
        if style == "yellow":
            print(_Fore.YELLOW + message + _Style.RESET_ALL)



def inflect_engine()->_inflect_engine_type:
    '''
        Create a singleton instance of the inflect engine.

        ----------

        Return {type}
        ----------------------
        The instance of the inflect engine.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-05-2022 08:42:21
        `memberOf`: colemen_config
        `version`: 1.0
        `method_name`: inflect_engine
        * @xxx [07-05-2022 08:44:27]: documentation for inflect_engine
    '''
    global INFLECT_ENGINE

    if INFLECT_ENGINE is None:
        import inflect
        INFLECT_ENGINE = inflect.engine()

    return INFLECT_ENGINE

