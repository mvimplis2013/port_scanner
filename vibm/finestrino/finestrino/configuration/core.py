import logging
import os 
import warnings

from .cfg_parser import FinestrinoConfigParser
from .toml_parser import FinestrinoTomlParser;

logger = logging.getLogger('finestrino-interface')

DEFAULT_PARSER = 'cfg'

PARSERS = {
    'cfg': FinestrinoConfigParser,
    'conf': FinestrinoConfigParser,
    'ini': FinestrinoConfigParser,
    'toml': FinestrinoTomlParser,
}

# Select parser via env var
DEFAULT_PARSER = 'cfg'
PARSER = os.environ.get('FINESTRINO_CONFIG_PARSER', DEFAULT_PARSER)
if PARSER not in PARSERS:
    warnings.warn("Invalid parser: {parser}".format(parser=PARSER))
    PARSER = DEFAULT_PARSER

def _check_parser(parser_class, parser):
    if not parser_class.enabled:
        msg = (
            "Parser not installed yet. "
            "Please, isntall finestrino with required parser:\n"
            "pip install finestrino[{parser}]"           
        )

        raise ImportError(msg.format(parser=parser))

def get_config(parser = PARSER):
    """Get configs singleton for parser
    
    Keyword Arguments:
        parser {[type]} -- [description] (default: {PARSER})
    """
    parser_class = PARSERS[parser]
    _check_parser(parser_class, parser)

    return parser_class.instance()

def add_config_path(path):
    """Select config parser by file extension and add path into parser.
    
    Arguments:
        path {[type]} -- [description]
    """
    if not os.path.isfile(path):
        warnings.warn("Config file does not exist: {path}".format(path=path))
        return False

    # select parser by file extension
    _base, ext = os.path.splitext(path)
    if ext and ext[1:] in PARSERS:
        parser = ext[1:]
    else:
        parser = PARSER

    parser_class = PARSERS[parser]

    _check_parser(parser_class, parser)

    if parser != PARSER:
        msg = (
            "Config for {added} parser added, but used {used} parser. "
            "Set up right parser via env var: "
            "export FINESTRINO_CONFIG_PARSER={added}"
        )
        warnings.warn(msg.format(added=parser, used=PARSER))

    # add config path to parser
    parser_class.add_config_path(path)

    return True

if 'FINESTRINO_CONFIG_PATH' in os.environ:
    add_config_path(os.environ['FINESTRINO_CONFIG_PATH'])