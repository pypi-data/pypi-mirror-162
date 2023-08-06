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
"""Entities that are used to describe tournaments on WotBlitz."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('Tournament',)

import attr
import typing
import enum

if typing.TYPE_CHECKING:
    from onewot.internal import unix
    from onewot import snowflakes


@attr.define(slots=True, frozen=True)
class Tournament:
    """Interface of tournament information."""

    id: snowflakes.Snowflake = attr.field()
    description: str = attr.field()
    end_at: unix.UnixTime = attr.field()
    matches_start_at: unix.UnixTime = attr.field()
    registration_end_at: unix.UnixTime = attr.field()
    registration_start_at: unix.UnixTime = attr.field()
    start_at: unix.UnixTime = attr.field()
    status: TournamentStatus = attr.field()
    title: str = attr.field()
    award: TournamentAward = attr.field()
    fee: TournamentFee = attr.field()
    logo: TournamentLogo = attr.field()
    winner_award: TournamentWinnerAward = attr.field()


@attr.define(slots=True, frozen=True)
class TournamentEconomy:
    """Interface of tournament economy information."""

    amount: int = attr.field()
    currency: CurrencyType = attr.field()


@attr.define(slots=True, frozen=True)
class TournamentAward(TournamentEconomy):
    """Interface of tournament award information."""


@attr.define(slots=True, frozen=True)
class TournamentFee(TournamentEconomy):
    """Interface of tournament fee information."""


@attr.define(slots=True, frozen=True)
class TournamentWinnerAward(TournamentEconomy):
    """Interface of tournament winner award information."""


@attr.define(slots=True, frozen=True)
class TournamentLogo:
    """Interface of tournament logo information."""

    original: str = attr.field()
    preview: str = attr.field()


class TournamentStatus(enum.Enum):
    """Interface of tournament status information."""

    UPCOMING: typing.Final[str] = 'upcoming'
    FINISHED: typing.Final[str] = 'finished'
    RUNNING: typing.Final[str] = 'running'
    REGISTRATION_STARTED: typing.Final[str] = 'registration_started'

    def __repr__(self) -> str:
        return self.value


class CurrencyType(enum.Enum):
    """Interface of tournament currency type information."""

    GOLD: typing.Final[str] = 'gold'
    CREDITS: typing.Final[str] = 'credits'
    FREE_EXPERIENCE: typing.Final[str] = 'free_experience'

    def __repr__(self) -> str:
        return self.value
