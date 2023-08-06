"""
Tools for a metamodern web environment.

## User agent tools

Simple interface, simple automate.

## Web application framework

Simple interface, simple deploy.

"""

from dns import resolver as dns

from . import microformats as mf
from .agent import *  # noqa
from .framework import *  # noqa
from .markdown import render as mkdn
from .response import Status  # noqa
from .response import (OK, Accepted, BadRequest, Conflict, Created, Forbidden,
                       Found, Gone, MethodNotAllowed, MovedPermanently,
                       MultiStatus, NoContent, NotFound, PermanentRedirect,
                       SeeOther, Unauthorized)
from .templating import template, templates

__all__ = [
    "mf",
    "dns",
    "mkdn",
    "get",
    "ConnectionError",
    "template",
    "templates",
    "OK",
    "Accepted",
    "BadRequest",
    "Conflict",
    "Created",
    "Forbidden",
    "Found",
    "Gone",
    "MethodNotAllowed",
    "MultiStatus",
    "NoContent",
    "NotFound",
    "PermanentRedirect",
    "SeeOther",
    "Unauthorized",
]
