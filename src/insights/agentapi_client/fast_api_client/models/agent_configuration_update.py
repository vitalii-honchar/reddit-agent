from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.agent_configuration_update_data import AgentConfigurationUpdateData


T = TypeVar("T", bound="AgentConfigurationUpdate")


@_attrs_define
class AgentConfigurationUpdate:
    """
    Attributes:
        id (UUID): Agent ID
        agent_type (Literal['search_agent']): Agent type
        data (AgentConfigurationUpdateData): Agent configuration data
    """

    id: UUID
    agent_type: Literal["search_agent"]
    data: "AgentConfigurationUpdateData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        agent_type = self.agent_type

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "agent_type": agent_type,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_configuration_update_data import AgentConfigurationUpdateData

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        agent_type = cast(Literal["search_agent"], d.pop("agent_type"))
        if agent_type != "search_agent":
            raise ValueError(f"agent_type must match const 'search_agent', got '{agent_type}'")

        data = AgentConfigurationUpdateData.from_dict(d.pop("data"))

        agent_configuration_update = cls(
            id=id,
            agent_type=agent_type,
            data=data,
        )

        agent_configuration_update.additional_properties = d
        return agent_configuration_update

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
