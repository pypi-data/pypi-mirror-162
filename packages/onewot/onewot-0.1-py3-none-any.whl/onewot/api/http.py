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
"""Provides an interface for HTTP-client implementations to follow."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('HTTPClient',)

import typing
import abc

if typing.TYPE_CHECKING:
    from onewot import users
    from onewot import clans
    from onewot import achievements
    from onewot import tournaments
    from onewot import snowflakes
    from onewot import urls
    from onewot.internal import data_binding


class HTTPClient(abc.ABC):
    """Interface for functionality that a HTTP-client implementation provides."""

    @abc.abstractmethod
    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, typing.Any] = None
    ) -> data_binding.JSONObject:
        """Method for making HTTP-requests.

        Parameters
        ----------
        method : builins.str
            One of HTTP request methods.
        path : builins.str
            Path to API method.
        params : builtins.dict[builtins.str, typing.Any]
            Dict of specified parameters for request.

        Returns
        -------
        onewot.internal.data_binding.JSONObject
            JSON-object with recieved data.
        """

    @abc.abstractmethod
    def _create_params(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        """Create parameters for HTTP-request.

        Parameters
        ----------
        kwargs : typing.Any
            Parameters for HTTP request body.

        Returns
        -------
        builtins.dict[builtins.str, typing.Any]
            Dict of specified keyword arguments for request params.
        """

    @abc.abstractmethod
    def _get_entity_id(self, entity_type: str, entity_name: str) -> snowflakes.Snowflake:
        """Fetch entity by his name.

        Parameters
        ----------
        entity_type : builtins.str
            One of entities of entity factory.
        entity_name : builtins.str
            Specified entity name.

        Returns
        -------
        onewot.snowflakes.Snowflake
            Entity identificator.
        """

    @abc.abstractmethod
    def _get_payload(
        self,
        entity_id: snowflakes.Snowflake,
        api_method: typing.Union[urls.API_METHODS],
        get_achievements: typing.Optional[bool] = None,
        **params: typing.Any
    ) -> data_binding.JSONObject:
        """Get payload data of entity from API.

        Parameters
        ----------
        entity_id : snowflakes.Snowflake
            Entity to fetch.
        api_method : typing.Union[urls.API_METHODS]
            Api method to use.
        get_achievements : typing.Optional[builtins.bool]
            Fetch user achievements or not. Defaults to `builtins.False`
        params : typing.Any
            Parameters for HTTP request body.

        Returns
        -------
        onewot.internal.data_binding.JSONObject
            JSON response from API request.

        Raises
        ------
        onewot.errors.EntityNotFound
            If provided entity does not exists.
        """

    @abc.abstractmethod
    def fetch_user(self, user: typing.Union[str, snowflakes.Snowflake]) -> users.User:
        """Fetch user by his ID or name.

        Parameters
        ----------
        user : typing.Union[builtins.str, onewot.snowflakes.Snowflake]
            User to fetch.

        Returns
        -------
        onewot.users.User
            Deserialized user object.
        """

    @abc.abstractmethod
    def fetch_clan(self, clan: typing.Union[str, snowflakes.Snowflake]) -> clans.Clan:
        """Fetch clan by his ID or name.

        Parameters
        ----------
        clan : typing.Union[builtins.str, onewot.snowflakes.Snowflake]
            Clan to fetch.

        Returns
        -------
        onewot.clans.Clan
            Deserialized clan object.
        """

    @abc.abstractmethod
    def fetch_user_achievements(self, user: typing.Union[str, snowflakes.Snowflake]) -> achievements.Achievement:
        """Fetch user achievements.

        Parameters
        ----------
        user : typing.Union[builtins.str, snowflakes.Snowflake]
            User to fetch achievements.

        Returns
        -------
        onewot.achievements.Achievement
            Deserialized achievement object.
        """

    @abc.abstractmethod
    def fetch_clan_member(self, user: typing.Union[str, snowflakes.Snowflake]) -> users.ClanMember:
        """Fetch clan member by his ID or name.

        Parameters
        ----------
        user : typing.Union[builtins.str, onewot.snowflakes.Snowflake]
            User to fetch.

        Returns
        -------
        onewot.users.ClanMember
            Deserialized clan member object.
        """

    @abc.abstractmethod
    def fetch_tournaments(
        self,
        tournament_name: typing.Optional[str] = None,
        page_number: typing.Optional[int] = None,
        limit: typing.Optional[int] = None
    ) -> typing.Optional[tuple[tournaments.Tournament]]:
        """Fetch tournaments.

        Parameters
        ----------
        tournament_name : typing.Optional[builtins.str]
            Tournament to fetch. Defaults to `builtins.None`.
        page_number : typing.Optional[builtins.int]
            Page for search. Defaults to `builtins.None`.
        limit : typing.Optional[builtins.int]
            Tournament search limit. Defaults to `builtins.None`.

        Returns
        -------
        typing.Optional[builtins.tuple[onewot.tournaments.Tournament]]
            Deserialized tournament objects. If no tournaments found,
            returns empty `builtins.tuple`.
        """

    @abc.abstractmethod
    def fetch_users_by_id(self, user_ids: typing.Iterable[snowflakes.Snowflake]) -> tuple[users.User]:
        """Fetch users by their ID.

        Parameters
        ----------
        user_ids : typing.Iterable[onewot.snowflake.Snowflake]
            An iterable object of user IDs.

        Returns
        -------
        builtins.tuple[onewot.users.User]
            Deserialized user objects.
        """

    @abc.abstractmethod
    def fetch_tournament(self, tournament: typing.Union[str, snowflakes.Snowflake]) -> tournaments.Tournament:
        """Fetch tournament by his ID or name.

        Parameters
        ----------
        tournament : typing.Union[builtins.str, onewot.snowflakes.Snowflake]
            Tournament to fetch.

        Returns
        -------
        onewot.tournaments.Tournament
            Deserialized tournament object.
        """
