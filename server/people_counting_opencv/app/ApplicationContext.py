import configparser
import os.path

from .DBConnector import DBConnector

# TODO: changes in class design, staticmethod and private functions variables should be avoided
class ApplicationContext:
    __obj = None
    __props = {}

    @staticmethod
    def getApplicationContext():
        if ApplicationContext.__obj is None:
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
        print("[INFO] " + config_file_name + " loaded")
        return config

    @staticmethod
    def __create_default_config_file(config_file_name):
        # TODO: Convert print statements to logger statements
        print("[INFO] Config file not found")
        print("[INFO] Creating " + config_file_name + " with DEFAULTS")
        config = configparser.ConfigParser()
        config["db"] = {"host": "localhost", "port": "27017", "db_name": "cognitive_portal",
                        "collection_name": "counting_logs"}
        config["db_thread"] = {"time_interval": "2", "in_min": "True"}
        config["people_counter_props"] = {"prototxt": "mobilenet_ssd/MobileNetSSD_deploy.prototxt",
                                          "caffemodel": "mobilenet_ssd/MobileNetSSD_deploy.caffemodel",
                                          "confidence_level": "0.4", "skip_frames": "30"}
        config["query"] = {"date_time_format_str": "%Y-%m-%dT%H:%M:%SZ"}
        with open(config_file_name, "w") as configfile:
            config.write(configfile)
        return config

    def get_props(self):
        return self.__props

    def __init__(self, config):
        if ApplicationContext.__obj is not None:
            # TODO: find appropriate exception class
            raise Exception("The Class is singleton")
        else:
            ApplicationContext.__obj = self
            self.total_count = 0
            self.pc_obj_map = {}
            for section in config.sections():
                ApplicationContext.__props.update({section: dict(config[section])})

            db = config["db"]
            # db_thread = config["db_thread"]
            # self.people_counter_props = config["people_counter_props"]
            self.db = dict(db)
            self.db_connector = DBConnector(host=db["host"], port=int(db["port"]), db_name=db["db_name"],
                                            collection_name=db["collection_name"])
            # self.db_thread = dict(db_thread)
    # TODO: convert this to __name__ == '__main__'
    @staticmethod
    def test():
        obj = ApplicationContext.getApplicationContext()
        props = obj.getProps()
        # print(props)
        input_source_list = str(props["people_counter_props"]['input_source']).split(" ")
        # print(input_source_list)
        return input_source_list

# ApplicationContext.test()
