import configparser
import os.path

from .DBConnector import DBConnector


class ApplicationContext:
    __obj = None

    @staticmethod
    def getApplicationContext():
        if ApplicationContext.__obj == None:
            # db, db_thread = ApplicationContext.__load_config()
            config = ApplicationContext.__load_config()
            ApplicationContext(config)
        return ApplicationContext.__obj

    @staticmethod
    def __load_config():
        config_file_name = "ConfigFile.properties"
        is_file = os.path.isfile(config_file_name)
        if not is_file:
            config = ApplicationContext.__create_default_config_file(config_file_name)
        config = configparser.ConfigParser()
        config.read(config_file_name)
        print("> " + config_file_name + " loaded")
        return config

    @staticmethod
    def __create_default_config_file(config_file_name):
        print("> Config file not found")
        print("> Creating " + config_file_name)
        config = configparser.ConfigParser()
        config["db"] = {"host": "localhost", "port": "27017", "db_name": "cognitive_portal",
                        "collection_name": "counting_logs"}
        config["db_thread"] = {"time_interval": "2", "in_min": "True"}
        config["people_counter_props"] = {"prototxt": "mobilenet_ssd/MobileNetSSD_deploy.prototxt",
                                          "caffemodel": "mobilenet_ssd/MobileNetSSD_deploy.caffemodel",
                                          "confidence_level": "0.4", "skip_frames": "30"}
        with open(config_file_name, "w") as configfile:
            config.write(configfile)
        return

    def __init__(self, config):
        if ApplicationContext.__obj != None:
            raise Exception("The Class is singleton")
        else:
            ApplicationContext.__obj = self
            self.total_count = 0
            for section in config.sections():
                # self.section = config[section]
                pass
            db = config["db"]
            db_thread = config["db_thread"]
            self.people_counter_props = config["people_counter_props"]
            self.db = dict(db)
            self.db_connector = DBConnector(host=db["host"], port=int(db["port"]), db_name=db["db_name"],
                                            collection_name=db["collection_name"])
            self.db_thread = dict(db_thread)

    @staticmethod
    def test():
        obj = ApplicationContext.getApplicationContext()
        print(obj.people_counter_props['confidence_level'])


ApplicationContext.test()
