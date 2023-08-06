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
"""Entities that are used to describe users on WotBlitz."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('User', 'ClanMember')

import abc
import typing
import enum

import attr

if typing.TYPE_CHECKING:
    from onewot.internal import unix
    from onewot import clans
    from onewot import achievements as achievement_models
    from onewot import snowflakes


@attr.define(slots=True, frozen=True)
class BaseUser(abc.ABC):
    """Basic interface of user information."""

    id: snowflakes.Snowflake = attr.field()


@attr.define(slots=True, frozen=True)
class ClanMember(BaseUser):
    """Interface of clan member information."""

    clan_id: snowflakes.Snowflake = attr.field()
    joined_at: unix.UnixTime = attr.field()
    role: MemberClanRole = attr.field()
    clan: clans.BaseClan = attr.field()


class MemberClanRole(enum.Enum):
    """Member clan roles interface."""

    PRIVATE: typing.Final[str] = 'private'
    COMMANDER: typing.Final[str] = 'commander'
    DIPLOMAT: typing.Final[str] = 'diplomat'
    VICE_LEADER: typing.Final[str] = 'vice_leader'
    LEADER: typing.Final[str] = 'leader'
    RECRUITER: typing.Final[str] = 'recruiter'
    TREASURER: typing.Final[str] = 'treasurer'

    def __repr__(self) -> str:
        return self.value


@attr.define(slots=True, frozen=True)
class User(BaseUser):
    """Interface of user information."""

    nickname: str = attr.field()
    created_at: unix.UnixTime = attr.field()
    last_battle_time: typing.Optional[unix.UnixTime] = attr.field()
    updated_at: unix.UnixTime = attr.field()
    spotted: int = attr.field()
    max_frags_tank_id: int = attr.field()
    hits: int = attr.field()
    frags: int = attr.field()
    max_xp: int = attr.field()
    max_xp_tank_id: int = attr.field()
    wins: int = attr.field()
    losses: int = attr.field()
    capture_points: int = attr.field()
    battles: int = attr.field()
    damage_dealt: int = attr.field()
    damage_received: int = attr.field()
    max_frags: int = attr.field()
    shots: int = attr.field()
    frags8p: int = attr.field()
    xp: int = attr.field()
    win_and_survived: int = attr.field()
    survived_battles: int = attr.field()
    dropped_capture_points: int = attr.field()
    win_percent: float = attr.field()
    achievements: achievement_models.Achievement = attr.field()
