import yaml

from zipfile import ZipFile


def get_data_directory(plugin_jar):
    with ZipFile(plugin_jar, 'r') as jar:
        with jar.open('plugin.yml', 'r') as plugin_yml:
            yml = yaml.load(plugin_yml)
            return yml['name']
