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
# Date:         10/08/22 3:50 PM
# Project:      djangoPlugin
# Module Name:  decorators
# ****************************************************************
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.models import TokenUser


def permission_required(perm, raise_exception=True):
    """
    Decorator to validate permissions from django auth structure, including JWT authentication
    :param perm: permission string or tuple with permissions list.
    :param raise_exception: True if you want to raise exception (default), False if not.
    :return: True if successfully
    """
    def check_perms(user):
        b_return = False
        local_user = user
        # If local user is instance of TokenUser, convert.
        if isinstance(local_user, TokenUser):
            local_user = User.objects.get(pk=local_user.id)
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm

        if local_user.has_perm(perms) or local_user.is_superuser:
            b_return = True
        elif raise_exception:
            raise PermissionDenied
        return b_return
    return user_passes_test(check_perms)
