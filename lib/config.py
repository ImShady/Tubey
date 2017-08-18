import configparser
from os import environ

class Config():

    @staticmethod
    def config_name():
        file = ""
        try:
            config = environ['TUBEY_CONFIG_PATH']
            if config is not None and config != "":
                file = config
            else:
                print("Environmental variable is set but empty!")
        except KeyError as e:
            print("Config file path not set in environment!")
            pass

        return file

    @staticmethod
    def get_section(section):
        config = configparser.ConfigParser()
        config.read(Config.config_name())
        sec = config._sections[section]
        return sec

    @staticmethod
    def get_variable(section, key):
        sec = Config.get_section(section)
        return sec[key]
