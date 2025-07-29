import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.agent_configuration_read_data import AgentConfigurationReadData


T = TypeVar("T", bound="AgentConfigurationRead")


@_attrs_define
class AgentConfigurationRead:
    """
    Attributes:
        id (UUID): Agent ID
        agent_type (Literal['search_agent']): Agent type
        created_at (datetime.datetime): Agent creation time
        updated_at (datetime.datetime): Agent update time
        data (AgentConfigurationReadData): Agent configuration data
    """

    id: UUID
    agent_type: Literal["search_agent"]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    data: "AgentConfigurationReadData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        agent_type = self.agent_type

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "agent_type": agent_type,
                "created_at": created_at,
                "updated_at": updated_at,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_configuration_read_data import AgentConfigurationReadData

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        agent_type = cast(Literal["search_agent"], d.pop("agent_type"))
        if agent_type != "search_agent":
            raise ValueError(f"agent_type must match const 'search_agent', got '{agent_type}'")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        data = AgentConfigurationReadData.from_dict(d.pop("data"))

        agent_configuration_read = cls(
            id=id,
            agent_type=agent_type,
            created_at=created_at,
            updated_at=updated_at,
            data=data,
        )

        agent_configuration_read.additional_properties = d
        return agent_configuration_read

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
