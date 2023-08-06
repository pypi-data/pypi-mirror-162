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
"""WotBlitz client module."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('WOTBClient',)

import typing

from onewot.impl import http

if typing.TYPE_CHECKING:
    from onewot import users
    from onewot import clans
    from onewot import tournaments
    from onewot import snowflakes


class WOTBClient:
    """WotBlitz API client.

    This is the class, you will want to create WotBlitz client.

    Parameters
    ----------
    application_id : builtins.str
        Application ID of WotBlitz API applications.

    Example
    -------
    Setting up client:

    ```py
    import os

    import onewot

    client = onewot.WOTBClient(os.environ["APPLICATION_ID"])
    ```
    """

    __slots__: typing.Sequence[str] = ('_application_id', '_http')

    def __init__(self, application_id: str) -> None:
        self._application_id = application_id
        self._http: http.HTTPClientImpl = http.HTTPClientImpl(application_id)

    def fetch_user(self, user: typing.Union[str, snowflakes.Snowflake]) -> users.User:
        """Fetch a user by name or identificator.

        Parameters
        ----------
        user : typing.Union[builtins.str, snowflakes.Snowflake]
            A user to fetch.

        Returns
        -------
        users.User
            User object.
        """
        return self._http.fetch_user(user)

    def fetch_clan(self, clan: typing.Union[str, snowflakes.Snowflake]) -> clans.Clan:
        """Fetch clan by name or identificator.

        Parameters
        ----------
        clan : typing.Union[builtins.str snowflakes.Snowflake]
            A clan to fetch.

        Returns
        -------
        clans.Clan
            Clan object.
        """
        return self._http.fetch_clan(clan)

    def fetch_clan_member(self, member: typing.Union[str, snowflakes.Snowflake]) -> users.ClanMember:
        """Fetch clan member by name or identificator.

        Parameters
        ----------
        member : typing.Union[builtins.str, snowflakes.Snowflake]
            A clan member to fetch.

        Returns
        -------
        users.ClanMember
            Clan member object
        """
        return self._http.fetch_clan_member(member)

    def fetch_tournaments(
        self,
        tournament_name: typing.Optional[str] = None,
        page_number: typing.Optional[int] = None,
        limit: typing.Optional[int] = None
    ) -> typing.Optional[tuple[tournaments.Tournament]]:
        """Fetch upcoming, finished and running tournaments.

        Parameters
        ----------
        tournament_name : typing.Optional[builtins.str]
            Tournament to fetch. Defaults to `builtins.None`.
        page_number : typing.Optional[builtins.int]
            Page for search. Defaults to `builtins.None`.
        limit : typing.Optional[builtins.int]
            Tournament search limit. Maximum value is 100.
            Defaults to `builtins.None`.

        Returns
        -------
        builtins.tuple[tournaments.Tournament]
            List of tournaments.
        """
        return self._http.fetch_tournaments(limit=limit)

    def fetch_users_by_id(self, user_ids: typing.Iterable[snowflakes.Snowflake]) -> tuple[users.User]:
        """Fetch users by their ID.

        Parameters
        ----------
        user_ids : typing.Iterable[snowflakes.Snowflakes]
            An iterable object of user IDs.

        Returns
        -------
        builtins.tuple[users.User]
            A tuple of user objects.
        """
        return self._http.fetch_users_by_id(user_ids)

    def fetch_tournament(self, tournament: typing.Union[str, snowflakes.Snowflake]) -> tournaments.Tournament:
        """Fetch tournament by name or identificator.

        Parameters
        ----------
        tournament : typing.Union[builtins.str, snowflakes.Snowflake]
            Tournament to fetch.

        Returns
        -------
        tournaments.Tournament
            Deserialized tournament object.
        """
        return self._http.fetch_tournament(tournament)
