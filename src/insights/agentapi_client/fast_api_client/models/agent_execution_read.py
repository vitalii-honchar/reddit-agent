import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.agent_execution_read_error_result_type_0 import AgentExecutionReadErrorResultType0
    from ..models.agent_execution_read_success_result_type_0 import AgentExecutionReadSuccessResultType0


T = TypeVar("T", bound="AgentExecutionRead")


@_attrs_define
class AgentExecutionRead:
    """
    Attributes:
        id (UUID): Agent ID
        config_id (UUID): Agent configuration ID
        executions (int): Agent executions
        created_at (datetime.datetime): Agent execution creation time
        updated_at (datetime.datetime): Agent execution update time
        success_result (Union['AgentExecutionReadSuccessResultType0', None]): Success result
        error_result (Union['AgentExecutionReadErrorResultType0', None]): Error result
    """

    id: UUID
    config_id: UUID
    executions: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    success_result: Union["AgentExecutionReadSuccessResultType0", None]
    error_result: Union["AgentExecutionReadErrorResultType0", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.agent_execution_read_error_result_type_0 import AgentExecutionReadErrorResultType0
        from ..models.agent_execution_read_success_result_type_0 import AgentExecutionReadSuccessResultType0

        id = str(self.id)

        config_id = str(self.config_id)

        executions = self.executions

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        success_result: Union[None, dict[str, Any]]
        if isinstance(self.success_result, AgentExecutionReadSuccessResultType0):
            success_result = self.success_result.to_dict()
        else:
            success_result = self.success_result

        error_result: Union[None, dict[str, Any]]
        if isinstance(self.error_result, AgentExecutionReadErrorResultType0):
            error_result = self.error_result.to_dict()
        else:
            error_result = self.error_result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "config_id": config_id,
                "executions": executions,
                "created_at": created_at,
                "updated_at": updated_at,
                "success_result": success_result,
                "error_result": error_result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_execution_read_error_result_type_0 import AgentExecutionReadErrorResultType0
        from ..models.agent_execution_read_success_result_type_0 import AgentExecutionReadSuccessResultType0

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        config_id = UUID(d.pop("config_id"))

        executions = d.pop("executions")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_success_result(data: object) -> Union["AgentExecutionReadSuccessResultType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                success_result_type_0 = AgentExecutionReadSuccessResultType0.from_dict(data)

                return success_result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AgentExecutionReadSuccessResultType0", None], data)

        success_result = _parse_success_result(d.pop("success_result"))

        def _parse_error_result(data: object) -> Union["AgentExecutionReadErrorResultType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_result_type_0 = AgentExecutionReadErrorResultType0.from_dict(data)

                return error_result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AgentExecutionReadErrorResultType0", None], data)

        error_result = _parse_error_result(d.pop("error_result"))

        agent_execution_read = cls(
            id=id,
            config_id=config_id,
            executions=executions,
            created_at=created_at,
            updated_at=updated_at,
            success_result=success_result,
            error_result=error_result,
        )

        agent_execution_read.additional_properties = d
        return agent_execution_read

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
