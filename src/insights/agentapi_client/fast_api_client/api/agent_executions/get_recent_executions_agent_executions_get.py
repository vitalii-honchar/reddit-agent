from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.agent_execution_read import AgentExecutionRead
from ...models.get_recent_executions_agent_executions_get_state import GetRecentExecutionsAgentExecutionsGetState
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Union[Unset, int] = 10,
    config_id: UUID,
    state: GetRecentExecutionsAgentExecutionsGetState,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    json_config_id = str(config_id)
    params["config_id"] = json_config_id

    json_state = state.value
    params["state"] = json_state

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agent-executions/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AgentExecutionRead.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, int] = 10,
    config_id: UUID,
    state: GetRecentExecutionsAgentExecutionsGetState,
) -> Response[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    """Get Recent Executions

    Args:
        limit (Union[Unset, int]): Maximum number of results to return Default: 10.
        config_id (UUID): Filter by configuration ID
        state (GetRecentExecutionsAgentExecutionsGetState): Filter by execution state

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['AgentExecutionRead']]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        config_id=config_id,
        state=state,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, int] = 10,
    config_id: UUID,
    state: GetRecentExecutionsAgentExecutionsGetState,
) -> Optional[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    """Get Recent Executions

    Args:
        limit (Union[Unset, int]): Maximum number of results to return Default: 10.
        config_id (UUID): Filter by configuration ID
        state (GetRecentExecutionsAgentExecutionsGetState): Filter by execution state

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['AgentExecutionRead']]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        config_id=config_id,
        state=state,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, int] = 10,
    config_id: UUID,
    state: GetRecentExecutionsAgentExecutionsGetState,
) -> Response[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    """Get Recent Executions

    Args:
        limit (Union[Unset, int]): Maximum number of results to return Default: 10.
        config_id (UUID): Filter by configuration ID
        state (GetRecentExecutionsAgentExecutionsGetState): Filter by execution state

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['AgentExecutionRead']]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        config_id=config_id,
        state=state,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    limit: Union[Unset, int] = 10,
    config_id: UUID,
    state: GetRecentExecutionsAgentExecutionsGetState,
) -> Optional[Union[HTTPValidationError, list["AgentExecutionRead"]]]:
    """Get Recent Executions

    Args:
        limit (Union[Unset, int]): Maximum number of results to return Default: 10.
        config_id (UUID): Filter by configuration ID
        state (GetRecentExecutionsAgentExecutionsGetState): Filter by execution state

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['AgentExecutionRead']]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            config_id=config_id,
            state=state,
        )
    ).parsed
