from os.path import join

from yamltool.yamltool import read_yaml_config_string
from yamltool.yamltool import preprocess_yaml_file
from yamltool.yamltool import parse_configuration
from yamltool.yamltool import YAMLTemplater


def test_preprocess_yaml_file():

    res = preprocess_yaml_file(join('tests', 'yaml_import', 'example.yaml'))

    expected = [
        '#!define variable=defined_value',
        '#aa.yaml',
        '#a.yaml',
        '#bb.yaml',
        '#b.yaml',
        '#example.yaml',
        'from_define: {{variable}}',
        'rootdir: {{root}}',
        'rootappend: {{root::hello}}'
        ]
    assert res == expected


def test_read_yaml_config_string():

    res = read_yaml_config_string("""
key1: value1
key2: value2
    """)

    assert res == {'key1': 'value1', 'key2': 'value2'}

    res = read_yaml_config_string("""
^key1: value1
key2: value2
    """)

    assert res == {'key2': 'value2'}

    res = read_yaml_config_string("""
^key1: &anchor_key1 value
key2: *anchor_key1
    """)

    assert res == {'key2': 'value'}


def test_read_yaml_config_file():

    yaml_templater = YAMLTemplater()
    yaml_templater.add_const_template('root', 'root_replacement')
    yaml_templater.add_function_template('root', lambda x: x)

    config, config_text = parse_configuration(
            join('tests', 'yaml_import', 'example.yaml'),
            yaml_templater)

    assert config['from_define'] == 'defined_value'
    assert config['rootdir'] == 'root_replacement'
    assert config['rootappend'] == 'hello'
