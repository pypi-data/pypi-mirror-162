import os
from accomate.aws.route53 import get_hosted_zone_id
from accomate.utils.network import get_machine_public_ip
from accomate.utils.yaml_file import read_yaml_file


class AccomateConfig(object):

    __shared_instance = 'accomate_in_the_skys'

    @staticmethod
    def get_instance():
 
        """Static Access Method"""
        if AccomateConfig.__shared_instance == 'accomate_in_the_skys':
            USER = os.environ.get("USER")
            AccomateConfig(USER, use_config=True)
        return AccomateConfig.__shared_instance

    def __init__(self, user: str, use_config: bool = False):

        if AccomateConfig.__shared_instance != 'accomate_in_the_skys':
            raise Exception ("This class is a singleton class !")
        else:
            AccomateConfig.__shared_instance = self

        self.__name = 'accomate'
        self.__version = '1.0.6'

        self.__config = None
        self.__base_path = f"/home/{user}/accomate"
        self.__config_path = f"{self.__base_path}/config.yaml"
        self.__base_domain = 'accoladez.com'
        self.__log_path = f"{self.__base_path}/logs"
        self.__base_store_path = f"{self.__base_path}/stores"
        self.__github_personal_token = ""
        self.__base_nginx_path = f"{self.__base_path}/nginx/conf"
        self.__image_host_username = "042826358439.dkr.ecr.us-east-1.amazonaws.com"

        if use_config:
            self.load_config()
        # if(not self.__machine_ip_address):
        #     self.__machine_ip_address = get_machine_public_ip().strip()
        # if(not self.__hosted_zone_id):
        #     self.__hosted_zone_id = get_hosted_zone_id(self.__base_domain)

    def get_version(self):
        return self.__version

    # @lru_cache(maxsize=10)
    def load_config(self):
        # load the config from the yaml file
        self.__config = read_yaml_file(self.__config_path)
        if self.__config is not None:
            self.__base_path = self.__config['base_path']
            self.__config_path = f"{self.__base_path}/config.yaml"
            self.__log_path = f"{self.__base_path}/logs"
            self.__base_store_path = f"{self.__base_path}/stores"
            self.__base_nginx_path = f"{self.__base_path}/nginx/conf"
            self.__base_domain = self.__config['base_domain']
            self.__image_host_username = self.__config['image_host_username']
            self.__github_personal_token = self.__config['github_personal_token']
            self.__machine_ip_address = get_machine_public_ip().strip()
            self.__hosted_zone_id = self.__config['hosted_zone_id']
            self.__aws_region = self.__config['aws']['region']
            self.__aws_access_key = self.__config['aws']['access_key']
            self.__aws_access_secret = self.__config['aws']['access_secret']
            os.environ.setdefault("GITHUB_PERSONAL_TOKEN", self.__github_personal_token)
            os.environ.setdefault("AWS_ACCESS_KEY_ID", self.__aws_access_key)
            os.environ.setdefault("AWS_SECRET_ACCESS_KEY", self.__aws_access_secret)
            os.environ.setdefault("AWS_REGION", self.__aws_region)
            

    def get_config_path(self):
        return self.__config_path

    def get_base_path(self):
        return self.__base_path

    def get_stores_path(self):
        return self.__base_store_path

    def get_domain(self):
        return self.__base_domain

    def get_store_service_image(self, version: str):
        return f"{self.__image_host_username}/accoladez-store:{version}"

    def get_auth_service_image(self, version: str):
        return f"{self.__image_host_username}/accoladez-auth:{version}"

    def get_zone_id(self):
        return self.__hosted_zone_id

    def get_public_ip(self):
        return self.__machine_ip_address

    def get_nginx_path(self):
        return self.__base_nginx_path

    def get_github_token(self):
        return self.__github_personal_token

    def set_domain(self, domain):
        self.__base_domain = domain
        self.__hosted_zone_id = get_hosted_zone_id(self.__base_domain)
        self.__machine_ip_address = get_machine_public_ip().strip()
        return True

    def get_base_db_path(self):
        return f"{self.__base_path}/database"

    def get_hosted_zone_id(self):
        return self.__hosted_zone_id