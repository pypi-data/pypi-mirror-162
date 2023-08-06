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
"""API-wide URLs."""

import typing

__all__: typing.Sequence[str] = (
    'BASE_URL',
    'ACCOUNT_INFO_PATH',
    'ACCOUNT_LIST_PATH',
    'ACCOUNT_ACHIEVEMENTS_PATH',
    'CLAN_LIST_PATH',
    'CLAN_INFO_PATH',
    'CLAN_MEMBER_PATH',
    'TOURNAMENT_LIST_PATH',
    'TOURNAMENT_INFO_PATH'
)

BASE_URL: typing.Final[str] = 'https://api.wotblitz.ru/wotb'
"""Base path to wotblitz API."""

ACCOUNT_INFO_PATH: typing.Final[str] = BASE_URL + '/account/info/'
"""Path to specified account info API method."""

ACCOUNT_LIST_PATH: typing.Final[str] = BASE_URL + '/account/list/'
"""Path to accounts info API method."""

ACCOUNT_ACHIEVEMENTS_PATH: typing.Final[str] = BASE_URL + '/account/achievements/'
"""Path to specified account achievements API method."""

CLAN_LIST_PATH: typing.Final[str] = BASE_URL + '/clans/list/'
"""Path to clans info API method."""

CLAN_INFO_PATH: typing.Final[str] = BASE_URL + '/clans/info/'
"""Path to specified clan info API method."""

CLAN_MEMBER_PATH: typing.Final[str] = BASE_URL + '/clans/accountinfo/'
"""Path to specified clan member info API method."""

TOURNAMENT_LIST_PATH: typing.Final[str] = BASE_URL + '/tournaments/list/'
"""Path to tournaments info API method."""

TOURNAMENT_INFO_PATH: typing.Final[str] = BASE_URL + '/tournaments/info/'
"""Path to specified tournament info API method."""

API_METHODS: typing.Final[dict[str, str]] = {
    'account_info': ACCOUNT_INFO_PATH,
    'account_list': ACCOUNT_LIST_PATH,
    'account_achievements': ACCOUNT_ACHIEVEMENTS_PATH,
    'clan_info': CLAN_INFO_PATH,
    'clan_list': CLAN_LIST_PATH,
    'clan_member': CLAN_MEMBER_PATH,
    'tournament_info': TOURNAMENT_INFO_PATH,
    'tournament_list': TOURNAMENT_LIST_PATH
}
"""Dict of API methods."""
