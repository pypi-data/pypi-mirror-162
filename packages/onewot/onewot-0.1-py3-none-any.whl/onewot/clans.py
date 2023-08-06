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
"""Entities that are used to describe clans on WotBlitz."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('Clan', 'BaseClan', 'RecruitingOptions')

import abc
import typing

import attr

if typing.TYPE_CHECKING:
    from onewot.internal.data_binding import OPEN, RESTRICTED
    from onewot.internal import unix
    from onewot import snowflakes


@attr.define(slots=True, frozen=True)
class BaseClan(abc.ABC):
    """Basic interface of clan information."""

    id: snowflakes.Snowflake = attr.field()
    created_at: typing.Optional[unix.UnixTime] = attr.field()
    emblem_set_id: typing.Optional[snowflakes.Snowflake] = attr.field()
    members_count: typing.Optional[int] = attr.field()
    name: typing.Optional[str] = attr.field()
    tag: typing.Optional[str] = attr.field()


@attr.define(slots=True, frozen=True)
class Clan(BaseClan):
    """Interface of clan information."""

    creator_id: typing.Optional[snowflakes.Snowflake] = attr.field()
    creator_name: typing.Optional[str] = attr.field()
    description: typing.Optional[str] = attr.field()
    is_clan_disbanded: bool = attr.field()
    leader_id: typing.Optional[snowflakes.Snowflake] = attr.field()
    leader_name: typing.Optional[str] = attr.field()
    members_ids: typing.Optional[list[snowflakes.Snowflake]] = attr.field()
    motto: typing.Optional[str] = attr.field()
    old_name: typing.Optional[str] = attr.field()
    old_tag: typing.Optional[str] = attr.field()
    recruiting_policy: typing.Optional[OPEN | RESTRICTED] = attr.field()
    renamed_at: typing.Optional[unix.UnixTime] = attr.field()
    updated_at: typing.Optional[unix.UnixTime] = attr.field()
    recruiting_options: typing.Optional[RecruitingOptions] = attr.field()


@attr.define(slots=True, frozen=True)
class RecruitingOptions:
    """Interface of clan recruiting optins information."""

    vehicles_level: int = attr.field()
    wins_ratio: int = attr.field()
    average_battles_per_day: int = attr.field()
    battles: int = attr.field()
    average_damage: int = attr.field()
