
from typing import TYPE_CHECKING, Any, Dict, List

class BaseHook():
    """
    Abstract base class for hooks, hooks are meant as an interface to
    interact with external systems. MySqlHook, HiveHook, PigHook return
    object that can handle the connection and interaction to specific
    instances of these systems, and expose consistent methods to interact
    with them.
    """

    @classmethod
    def get_connection(cls, request_type: str):
        """
        Get connection, given connection id.

        :param conn_id: connection id
        :return: connection
        """
        request_info = {}

        return request_info


    def get_conn(self) -> Any:
        """Returns connection for the hook."""
        raise NotImplementedError()

    @classmethod
    def get_connection_form_widgets(cls) -> Dict[str, Any]:
        ...

    @classmethod
    def get_ui_field_behaviour(cls) -> Dict[str, Any]:
        ...
