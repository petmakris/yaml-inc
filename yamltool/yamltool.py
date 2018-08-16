from os.path import basename
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import exists

import re
import logging
import yaml

logger = logging.getLogger(__name__)

IMPORT_STATEMENT = r'\s*#\s*!include\s*\'([a-zA-Z0-9_.\-/]+)\'\s*'
VARDEC_STATEMENT = r'\s*#\s*!define\s*([a-zA-Z0-9_.\-]+)\s*=\s*([^ \t\n\r\f\v]+)\s*'

VALID_KEY_STATEMENT = r'\^.*'

def _get_lines(filename):
    res = []
    with open(filename, 'rU') as f:
        for line in f.readlines():
            res.append(line)
    return res


################################################################################
# read_yaml_config_string
################################################################################

def preprocess_yaml_file(filename):
    
    base = dirname(abspath(filename))
    fname = basename(filename)
    yamlfiles = []

    def _preprocess_yaml_file(__base, __filename):

        _base = join(__base, dirname(__filename))
        wfname = join(__base, _base, basename(__filename))
        logger.debug('YAML preprocessor: [%s]', wfname)

        if wfname not in yamlfiles:
            yamlfiles.append(wfname)
        else:
            raise Exception('Tried to import twice [%s]' % wfname)

        lines = _get_lines(wfname)
        res = []
        for line in lines:
            match = re.match(IMPORT_STATEMENT, line)
            if match is not None:
                fn = match.group(1)
                for c in _preprocess_yaml_file(join(__base, _base), fn):
                    res.append(c.rstrip('\n'))
            else:
                res.append(line.rstrip('\n'))
        return res

    return _preprocess_yaml_file(base, fname)


################################################################################
# read_yaml_config_string
################################################################################

def read_yaml_config_string(string_value):

    def valid(string_val):
        return re.match(VALID_KEY_STATEMENT, string_val) is None

    try:
        conf = {}
        for k, v in yaml.load(string_value).iteritems():
            conf[k] = v
        res = {}
        for k, v in conf.iteritems():
            if valid(k):
                res[k] = v

        return res
    except Exception as e:
        raise Exception(e)


################################################################################
# YAMLTemplater
################################################################################

class YAMLTemplater(object):

    def __init__(self):
        self._const_templates = {}
        self._function_templates = {}

    def template(self, lines):

        for l in lines:
            r1 = re.match(VARDEC_STATEMENT, l)
            if r1 is not None:
                cmd = r1.group(1)
                matched = r1.group(2)
                logger.info('Configuring variable [%s] with value [%s]' % (cmd, matched))
                self.add_const_template(cmd, matched)

        # Search of matches and replace based on _const_template and _function_templates.
        # but first preprocess the file and add to const_templates custom variables.
        output = []
        for l in lines:
            r1 = re.match(r'.*({{(\w+)}}).*', l)
            if r1 is not None:
                exact_match = r1.group(1)
                match_value = r1.group(2)
                l = l.replace(exact_match, self.get_const_templates(match_value))

            r2 = re.match(r'.*({{(\w+)::(\w+)}}).*', l)
            if r2 is not None:
                exact_match = r2.group(1)
                cmd = r2.group(2)
                val = r2.group(3)
                l = l.replace(exact_match, self.get_function_templates(cmd, val))
            output.append(l)

        return output

    def add_const_template(self, cmd, value):
        self._const_templates[cmd] = value

    def add_function_template(self, cmd, function):
        self._function_templates[cmd] = function

    def get_const_templates(self, cmd):
        return self._const_templates[cmd]

    def get_function_templates(self, cmd, val):
        return self._function_templates[cmd](val)


################################################################################
# read_configuration
################################################################################

def parse_configuration(config_file, yaml_templater=None):

    if not exists(config_file):
        raise RuntimeError('[%s] file does not exist', config_file)

    logger.debug('Trying to load configuration from [%s]', config_file)
    lines = preprocess_yaml_file(config_file)

    logger.debug('Loaded [%s] lines of configuration', len(lines))

    if yaml_templater is not None:
        config_text = '\n'.join(yaml_templater.template(lines))
    else:
        config_text = '\n'.join(lines)

    configuration = read_yaml_config_string(config_text)
    return configuration, config_text
