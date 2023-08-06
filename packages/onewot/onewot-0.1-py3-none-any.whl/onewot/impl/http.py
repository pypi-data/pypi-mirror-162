# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2022 Crisp Crow
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Implementation of a HTTP-client for WotBliz API."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('HTTPClientImpl',)

import typing

from requests_futures import sessions

from onewot.impl import entity_factory
from onewot.impl import error_handlers
from onewot.api import http
from onewot.internal import data_binding
from onewot import urls
from onewot import snowflakes
from onewot import errors

if typing.TYPE_CHECKING:
    from onewot import users
    from onewot import clans
    from onewot import achievements
    from onewot import tournaments


class HTTPClientImpl(http.HTTPClient):
    """HTTP client for making requests to API methods.

    This manages making HTTP/1.1 requests to the API and using the entity
    factory within the passed application instance to deserialize JSON responses
    to Pythonic data classes that are used throughout this library.

    Parameters
    ----------
    application_id : builtins.str
        Application ID of WotBlitz API application.
    """

    __slots__: typing.Sequence[str] = (
        '_application_id',
        '_session',
        '_error_handler',
        '_entity_factory'
    )

    def __init__(self, application_id: str) -> None:
        self._application_id: str = application_id
        self._session: sessions.FuturesSession = sessions.FuturesSession()
        self._error_handler: error_handlers.ErrorHandler = error_handlers.ErrorHandlerImpl()
        self._entity_factory: entity_factory.EntityFactory = entity_factory.EntityFactoryImpl()

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, typing.Any]
    ) -> typing.Optional[data_binding.JSONObject]:
        payload = self._session.request(method, path, params).result().json()
        handled_payload = self._error_handler.handle(payload, params)

        if isinstance(handled_payload, errors.OnewotError):
            raise handled_payload

        return payload

    def _create_params(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        return dict(kwargs, application_id=self._application_id)

    def _get_entity_id(self, entity_type: str, entity_name: str) -> snowflakes.Snowflake:
        params = self._create_params(search=entity_name)
        path = self._entity_factory.entities[entity_type]
        payload = self._request('GET', path, params)

        return snowflakes.Snowflake(payload['data'][0][entity_type])

    def _get_payload(
        self,
        entity_id: snowflakes.Snowflake,
        api_method: typing.Union[urls.API_METHODS],
        get_achievements: typing.Optional[bool] = False,
        **params: typing.Any
    ) -> data_binding.JSONObject:
        params = self._create_params(**params)
        payload = self._request('GET', urls.API_METHODS[api_method], params)

        try:
            if get_achievements:
                achievement_payload = self._request('GET', urls.ACCOUNT_ACHIEVEMENTS_PATH, params)
                achievements = self._entity_factory.deserialize_achievement(achievement_payload['data'][str(entity_id)])
                return dict(**payload['data'][str(entity_id)], achievements=achievements)

            return dict(**payload['data'][str(entity_id)])
        except TypeError:
            raise errors.EntityNotFound('404', 'ENTITY_NOT_FOUND', entity_id)

    def fetch_user(self, user: typing.Union[str, snowflakes.Snowflake]) -> users.User:
        if isinstance(user, str):
            user = self._get_entity_id('account_id', user)

        payload = self._get_payload(
            entity_id=user,
            api_method='account_info',
            get_achievements=True,
            account_id=user
        )
        return self._entity_factory.deserialize_user(payload=payload)

    def fetch_clan(self, clan: typing.Union[str, snowflakes.Snowflake]) -> clans.Clan:
        if isinstance(clan, str):
            clan = self._get_entity_id('clan_id', clan)

        payload = self._get_payload(
            entity_id=clan,
            api_method='clan_info',
            clan_id=clan
        )
        return self._entity_factory.deserialize_clan(payload)

    def fetch_user_achievements(self, user: typing.Union[str, snowflakes.Snowflake]) -> achievements.Achievement:
        if isinstance(user, str):
            user = self._get_entity_id('account_id', user)

        payload = self._get_payload(
            entity_id=user,
            api_method='account_achievements',
            account_id=user
        )
        return self._entity_factory.deserialize_achievement(payload)

    def fetch_clan_member(self, user: typing.Union[str, snowflakes.Snowflake]) -> clans.ClanMember:
        if isinstance(user, str):
            user = self._get_entity_id('account_id', user)

        payload = self._get_payload(
            entity_id=user,
            api_method='clan_member',
            account_id=user
        )
        return self._entity_factory.deserialize_clan_member(payload)

    def fetch_tournaments(
        self,
        tournament_name: typing.Optional[str] = None,
        page_number: typing.Optional[int] = None,
        limit: typing.Optional[int] = None
    ) -> typing.Optional[tuple[tournaments.Tournament]]:
        params = self._create_params(
            search=tournament_name,
            limit=limit,
            page_no=page_number
        )
        payload = self._request('GET', urls.TOURNAMENT_LIST_PATH, params)
        return tuple(
            self._entity_factory.deserialize_tournament(data) for data in payload['data']
        )

    def fetch_users_by_id(self, user_ids: typing.Iterable[snowflakes.Snowflake]) -> tuple[users.User]:
        return tuple(
            map(
                lambda user_id: self._entity_factory.deserialize_user(
                    payload=self._get_payload(
                        entity_id=user_id,
                        api_method='account_info',
                        get_achievements=True,
                        account_id=user_id
                        ),
                ), user_ids
            )
        )

    def fetch_tournament(self, tournament: typing.Union[str, snowflakes.Snowflake]) -> tournaments.Tournament:
        if isinstance(tournament, str):
            tournament = self._get_entity_id('tournament_id', tournament)

        payload = self._get_payload(
            entity_id=tournament,
            api_method='tournament_info',
            tournament_id=tournament
        )
        return self._entity_factory.deserialize_tournament(payload)
