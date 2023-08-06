import datetime
import os

import pytz


def split_filepath(url: str) -> 'tuple[str, str]':
    """
    Splits an url and returns the document name and extension
    as a 2-element tuple.
    """
    docname, docext = os.path.splitext(url)
    docname = docname.rsplit('/')[-1]
    return docname, docext


def get_logpath(tz: str = 'America/Sao_Paulo') -> str:
    """
    Returns the current date formatted for logging directories.
    \nExample:\n
    * container_fullpath = 'my_container/subdir' + get_logpath() \n
    Printing 'container_fullpath' will return:
    * 'my_container/subdir/<THIS_YEAR>/<THIS_MONTH>/<THIS_DAY>'.\n
    
    :param str: timezone\n
    Default timezone is 'America/Sao_Paulo'.
    """
    tz = pytz.timezone(tz)
    return datetime.datetime.now(tz=tz).strftime('/%Y/%m/%d')
