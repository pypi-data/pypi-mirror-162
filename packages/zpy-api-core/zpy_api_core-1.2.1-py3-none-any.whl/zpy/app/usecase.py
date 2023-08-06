from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Union, Any

from zpy.utils.values import if_null_get

T = TypeVar("T")
S = TypeVar("S")


class UCMeta:
    def __init__(self, identifier: str, key_identifier: str = None) -> None:
        self.id = identifier
        if key_identifier:
            setattr(self, key_identifier, identifier)


class UseCase(ABC, Generic[T, S]):
    @abstractmethod
    def execute(self, input_data: T, *args, **kwargs) -> S:
        """Execute use case"""
        pass


class UseCaseSelector(UseCase, UCMeta):

    def __init__(self, use_cases: List[Union[UseCase, UCMeta, Any]], action_keys: List[str] = None,
                 key_uc_identifier: str = 'id', selector_id='default', payload_keys: List[str] = None):
        UCMeta.__init__(self, identifier=selector_id)
        self.cases = {getattr(x, key_uc_identifier): x for x in use_cases}
        self.action_keys = if_null_get(action_keys, ['action'])
        self.key_identifier = key_uc_identifier
        self.payload_keys = if_null_get(payload_keys, ['payload'])

    def execute(self, data: dict, context: Any = None, *args, **kwargs) -> dict:
        action = None
        for key_action in self.action_keys:
            if key_action in data:
                action = key_action
                break
        if action is None:
            raise ValueError(f'Request provided is malformed. Missing {action} key!')

        operation: Union[UseCase, UCMeta] = self.cases.get(data[action], None)

        if not operation:
            raise ValueError(f"Use case for action: {data['action']} not registered in selector.")

        payload_key = None
        for pk in self.payload_keys:
            if pk in data:
                payload_key = pk
                break

        payload = data.get(payload_key, data)
        return operation.execute(payload, context=context)
