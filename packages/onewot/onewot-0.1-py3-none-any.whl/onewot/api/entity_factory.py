# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
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
"""Core interface for an object that deserializes API objects."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('EntityFactory',)

import typing
import abc

from onewot import urls

if typing.TYPE_CHECKING:
    from onewot import tournaments as tournament_models
    from onewot import clans as clan_models
    from onewot import users as user_models
    from onewot import achievements as achievement_models
    from onewot.internal import data_binding


class EntityFactory(abc.ABC):
    """Interface for components that deserialize JSON payloads."""

    @property
    def entities(self) -> dict[str, str]:
        return {
            'account_id': urls.ACCOUNT_LIST_PATH,
            'clan_id': urls.CLAN_LIST_PATH,
            'tournament_id': urls.TOURNAMENT_LIST_PATH
        }

    @abc.abstractmethod
    def deserialize_clan(self, payload: data_binding.JSONObject) -> clan_models.Clan:
        """Parse a raw payload from WotBlitz into a clan object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.clans.Clan
            The deserialized clan information object.
        """

    @abc.abstractmethod
    def deserialize_user(self, payload: data_binding.JSONObject) -> user_models.User:
        """Parse a raw payload from WotBlitz into a user object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.users.User
            The deserialized user information object.
        """

    @abc.abstractmethod
    def deserialize_achievement(self, payload: data_binding.JSONObject) -> achievement_models.Achievement:
        """Parse a raw payload from WotBlitz into an achivement object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.achivements.Achievement
            The deserialized user achivements information object.
        """

    @abc.abstractmethod
    def deserialize_base_clan(self, payload: data_binding.JSONObject) -> clan_models.BaseClan:
        """Parse a raw payload from WotBlitz into a base clan object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.clans.BaseClan
            The deserialized base clan information object.
        """

    @abc.abstractmethod
    def deserialize_clan_member(self, payload: data_binding.JSONObject) -> user_models.ClanMember:
        """Parse a raw payload from WotBlitz into a clan member object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.users.ClanMember
            The deserialized clan member information object.
        """

    @abc.abstractmethod
    def deserialize_recruiting_options(self, payload: data_binding.JSONObject) -> clan_models.RecruitingOptions:
        """Parse a raw payload from WotBlitz into a recruiting clan options object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.clans.RecruitingOptions
            The deserialized recruiting options information object.
        """

    @abc.abstractmethod
    def deserialize_tournament(self, payload: data_binding.JSONObject) -> tournament_models.Tournament:
        """Parse a raw payload from WotBlitz into a tournament object.

        Parameters
        ----------
        payload : onewot.internal.data_binding.JSONObject
            The JSON payload to deserialize.

        Returns
        -------
        onewot.tournaments.Tournament
            The deserialized tournament information object.
        """
