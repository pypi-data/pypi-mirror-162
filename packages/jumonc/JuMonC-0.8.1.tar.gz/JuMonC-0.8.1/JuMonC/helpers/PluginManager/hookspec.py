import pluggy
from typing import List, Dict, Union, Any

hookspec = pluggy.HookspecMarker("JuMonC")


# Defining empty functions for plugins, therefore parameters will not be used here
#pylint: disable=unused-argument


@hookspec
def plugin_arguments(aruments: str) -> None:
    """
    Get a string of user supplied arguments for this plugin.
    
    JuMonC will pass on arguments for plugins, to let them evealute their own arguments.
    """

    
@hookspec
def needed_REST_paths() -> List[str]:
    """
    Return a list of paths that this plugin wants to add to the REST-API.
    
    :return: a list of REST API paths
    """


@hookspec
def register_REST_path(requested_path: str, approved_path:str) -> Dict[str, Union[bool, str, List[Dict[str, str]]]]:
    """
    Register the requested path with the REST-API.

    :param requested_path: the path that was requested
    :param approved_path: the path that that was approved
    :return: if the approved path was added, return a dictonary, explaining the path,
    as a dictonary with entries for the link, a description and parameters. 
    
    note::
    A dictonary for the link description could look like this:
    {
        "link": "/v" + str(version) + gpu_path + "/config",
        "isOptional": True,
        "description": "Gather information concerning the memory config",
        "parameters": [
            {"name": "token",
             "description": "Supply a token that shows you are allowed to access this link (or login once using /login)"}]
    }
    
    """


@hookspec
def register_startup_parameter() -> List[Dict[str, Union[bool, int, float, str, type]]]:
    """
    Register the wanted startup parameter for this plugin.

    :return: a list of dictonaries, one dictonary for each parameter.
    """


@hookspec
def startup_parameter(parameter_name: str, value:Any) -> None:
    """
    Use the user supplied value for start parameter.

    :param parameter_name: the name of the parameter
    :param value: the value set for this parameter
    """


@hookspec
def register_MPI(MPI_ID_min:int, MPI_ID_max:int) -> None:
    """
    Let the plugin handle all necessary steps for it's MPI communication.
    
    Let the plugin register callback options for MPI_IDs used in JuMonC's communication.
    This plugin can use all MPI_IDs between min and max for all it's internal needs.
    """


#pylint: enable=unused-argument