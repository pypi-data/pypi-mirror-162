
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
"""Implementation of an error handler for WotBlitz API"""

from __future__ import annotations

__all__: typing.Sequence[str] = ('ErrorHandlerImpl',)

import typing

from onewot.api import error_handlers
from onewot import errors

if typing.TYPE_CHECKING:
    from onewot.internal import data_binding


class ErrorHandlerImpl(error_handlers.ErrorHandler):
    """Implementation of an error handler for WotBlitz API responses."""

    __slots__: typing.Sequence[str] = ()

    def handle(
        self,
        payload: data_binding.JSONObject,
        params: dict[str, typing.Any]
    ) -> typing.Union[data_binding.JSONObject, errors.OnewotError]:
        if payload['status'] == 'error':
            return errors.OnewotError(**payload['error'])

        if not len(payload['data']):
            return errors.OnewotError('407', 'INVALID_FIELDS', 'fields', params['search'])

        return payload
