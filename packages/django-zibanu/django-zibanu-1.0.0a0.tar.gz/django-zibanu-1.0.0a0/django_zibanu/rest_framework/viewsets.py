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
# Date:         10/08/22 4:48 PM
# Project:      djangoPlugin
# Module Name:  viewsets
# ****************************************************************
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet as SourceViewSet
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication


class ModelViewSet(SourceViewSet):
    """
    Override vlass ModelViewSet to load default permissions and other features
    """
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication]
    msgs = {
        "id_required", _("ID field is required.")
    }

    if settings.DEBUG:
        # If debug, allow TokenAuthentication to run ViewSet
        authentication_classes.append(authentication.TokenAuthentication)

