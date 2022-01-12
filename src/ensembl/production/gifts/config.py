import os
import pkg_resources
from ensembl.production.core.config import load_config_yaml


config_file_path = os.environ.get('GIFTS_CONFIG_PATH')
file_config = load_config_yaml(config_file_path)


class GIFTsConfig:
    HIVE_UPDATE_ENSEMBL_ANALYSIS = os.environ.get("HIVE_UPDATE_ENSEMBL_ANALYSIS",
                                                  file_config.get('hive_update_ensembl_analysis', 'submit'))
    HIVE_PROCESS_MAPPING_ANALYSIS = os.environ.get("HIVE_PROCESS_MAPPING_ANALYSIS",
                                                   file_config.get('hive_process_mapping_analysis', 'submit'))
    HIVE_UPDATE_ENSEMBL_URI = os.environ.get("HIVE_UPDATE_ENSEMBL_URI",
                                             file_config.get('hive_update_ensembl_uri', None))
    HIVE_PROCESS_MAPPING_URI = os.environ.get("HIVE_PROCESS_MAPPING_URI",
                                              file_config.get('hive_process_mapping_uri', None))
    GIFTS_API_URIS_FILE = os.environ.get("GIFTS_APIS_URIS_FILE",
                                         file_config.get('gifts_api_uris_file', 'gifts_api_uris.json'))
    
    APP_VERSION = version = pkg_resources.require("gifts")[0].version
    
    SWAGGER = {
      'title': 'Ensembl Production: GIFTs Pipeline API',
      'uiversion': 3,
      'hide_top_bar': True,
      'ui_params': {
        'defaultModelsExpandDepth': -1
      },
      'favicon': '/static/gifts/img/gifts.png',
      'specs_route': '/api'
    }
