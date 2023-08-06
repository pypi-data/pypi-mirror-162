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
# Date:         10/08/22 4:08 PM
# Project:      djangoPlugin
# Module Name:  exceptions
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException as SourceException
from rest_framework import status


class APIException(SourceException):
    """
    Override class from APIException
    """
    __default_messages = {
        "304": _("Object has not been created."),
        "400": _("Generic error."),
        "401": _("You are not authorized for this resource."),
        "404": _("Object does not exists."),
        "406": _("Data validation error."),
        "412": _("Data required not found."),
        "500": _("Not controlled exception error."),
    }

    def __init__(self, msg: str = None, error: str = None, http_status: int = status.HTTP_400_BAD_REQUEST) -> None:
        """
        Override init method
        :param msg: list, dict, str: Data to show the exception detail.
        :param error: list,dict, str: Code error
        :param http_status: int: Status code
        """
        str_status = str(http_status)

        # Define default messages if args not passed
        error = error if error is not None else _("Generic error.")
        msg = msg if msg is not None else self.__default_messages.get(str_status, _("Generic error."))

        # Create detail dictionary
        detail = {
            "message": msg,
            "detail": error
        }

        if http_status is not None:
            self.status_code = http_status

        super().__init__(detail)

