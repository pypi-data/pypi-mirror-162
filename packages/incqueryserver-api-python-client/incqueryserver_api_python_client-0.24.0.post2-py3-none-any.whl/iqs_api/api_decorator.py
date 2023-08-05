import collections
import importlib
from copy import copy

ApiClientModule = collections.namedtuple(
    "ApiClientModule",
    ['endpoint_path',
     'root_module_name',
     'api_names_to_class']
)

# TODO auto-generate from dir(iqs_client.api) + name mangling ? 
_api_client_modules = [
    ApiClientModule('api', 'iqs_client', {
        'acquisition'       : "AcquisitionApi",
        'async'             : "AsyncApi",
        'analysis'          : 'AnalysisApi',
        'impact_analysis'   : "ImpactAnalysisApi",
        'in_memory_index'   : "InMemoryIndexApi",
        'persistent_index'  : "PersistentIndexApi",
        'queries'           : "QueriesApi",
        'query_execution'   : "QueryExecutionApi",
        'repository'        : "RepositoryApi",
        'server_management' : "ServerManagementApi",
        'validation'        : "ValidationApi",
        'integration'       : "IntegrationApi",
        'mms_repository'    : "MmsRepositoryApi",
        'experimental'      : "ExperimentalApi",
        'demo'              : "DemoApi"
    }),
]


def decorate_iqs_client(iqs_client_object, root_configuration, endpoint_class):
    for api_client_module in _api_client_modules:
        try:  # if client lib is missing, simply skip
            endpoint_specific_config = copy(root_configuration)
            endpoint_specific_config.host = "{}/{}".format(root_configuration.host, api_client_module.endpoint_path)
            endpoint_specific_client = endpoint_class(endpoint_specific_config)

            # If session header is set in configuration, we set a default header in ApiClient
            if hasattr(root_configuration, 'auth_header_name') and hasattr(root_configuration, 'auth_header_value'):
                endpoint_specific_client.set_default_header(root_configuration.auth_header_name, root_configuration.auth_header_value)

            for api_field_name, api_class_name in api_client_module.api_names_to_class.items():
                api_module_name = "{}.api.{}_api".format(api_client_module.root_module_name, api_field_name)
                try:
                    api_module = importlib.import_module(api_module_name)
                    if api_class_name in dir(api_module):  # there might be api classes presently missing / disabled
                        api_class = getattr(api_module, api_class_name)
                        api_object = api_class(endpoint_specific_client)
                        setattr(iqs_client_object, api_field_name, api_object)
                except ImportError:
                    pass
        except ImportError:
            pass
