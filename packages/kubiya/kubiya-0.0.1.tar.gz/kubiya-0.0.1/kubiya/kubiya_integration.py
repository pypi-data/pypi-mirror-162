from typing import List, Dict, NoReturn, Any
import inspect
from logging import getLogger


logger = getLogger(__name__)

class KubiyaIntegraion:
    """handles kubiya actions and exeution"""

    _instances = list()

    @classmethod
    def register_integration(cls, integration: "KubiyaIntegraion") -> NoReturn:
        cls._instances.append(integration)
    
    def __init__(self, integration_name: str, version: str = "testing") -> None:
        assert integration_name != "", "integration_name cannot be empty"
        self._registered_actions = {}
        self._name = integration_name
        self._version = version
        self.__class__.register_integration(self)

    @classmethod
    def validate_action(cls, action: callable) -> NoReturn:
        cls._validate_action_is_callable(action)
        cls._validate_action_signature(action)

    @classmethod
    def _validate_action_is_callable(cls, action: callable) -> NoReturn:
        assert callable(
            action
        ), f"{action} must be callable in order to be registered as an action"

    @classmethod
    def _validate_action_signature(cls, action: callable) -> NoReturn:
        sig = inspect.signature(action)
        mandatory_args = [
            nm
            for nm, par in sig.parameters.items()
            if par.default == inspect.Signature.empty
            and par.kind not in (par.VAR_KEYWORD, par.VAR_POSITIONAL)
        ]
        if len(mandatory_args) > 1:
            raise AssertionError(
                f"{action} must have at most 1 mandatory argument ({mandatory_args})"
            )

    def register_action(self, action_name: str, action: callable) -> NoReturn:
        self.validate_action(action)
        self._registered_actions[action_name] = action

    def get_registered_actions(self) -> List[str]:
        return list(self._registered_actions.keys())

    def get_registered_action_info(self, action_name: str) -> callable:
        assert (
            action_name in self._registered_actions
        ), f"`{action_name}` is not a registered action"
        return self._registered_actions[action_name]

    def get_registered_actions_info(self) -> List[callable]:
        return self._registered_actions.values()

    def execute_action(self, action_name: str, input: Dict) -> Any:
        assert (
            action_name in self._registered_actions
        ), f"`{action_name}` is not a registered action"
        action = self._registered_actions[action_name]
        try:
            return action(input)
        except Exception as e:
            logger.error(f"{action_name} failed with error: {e}")

    def get_version(self) -> str:
        return self._version

    def get_name(self) -> str:
        return self._name
