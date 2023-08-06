# -*- coding: utf-8 -*-

#      Copyright (C)  2022. CQ Inversiones SAS.
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/08/22 3:57 PM
# Project:      djangoPlugin
# Module Name:  handlers
# ****************************************************************
from rest_framework.views import exception_handler
from rest_framework.views import Response
from typing import Any


def rest_exception_handler(exc: Exception, context: dict[str: Any]) -> Response:
    """
    Custom API Exception handler implementation
    :param exc: Source exception
    :param context: Context variable
    :return: Response
    """
    response = exception_handler(exc. exc, context)
    # TODO: Implement log handler.

    return response
