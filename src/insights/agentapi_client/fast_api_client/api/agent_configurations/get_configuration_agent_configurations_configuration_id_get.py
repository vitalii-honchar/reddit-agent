from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_configuration_read import AgentConfigurationRead
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    configuration_id: UUID,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/agent-configurations/{configuration_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AgentConfigurationRead, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AgentConfigurationRead.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AgentConfigurationRead, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    configuration_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AgentConfigurationRead, HTTPValidationError]]:
    """Get Configuration

    Args:
        configuration_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentConfigurationRead, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        configuration_id=configuration_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    configuration_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AgentConfigurationRead, HTTPValidationError]]:
    """Get Configuration

    Args:
        configuration_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentConfigurationRead, HTTPValidationError]
    """

    return sync_detailed(
        configuration_id=configuration_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    configuration_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[AgentConfigurationRead, HTTPValidationError]]:
    """Get Configuration

    Args:
        configuration_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AgentConfigurationRead, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        configuration_id=configuration_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    configuration_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[AgentConfigurationRead, HTTPValidationError]]:
    """Get Configuration

    Args:
        configuration_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AgentConfigurationRead, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            configuration_id=configuration_id,
            client=client,
        )
    ).parsed
