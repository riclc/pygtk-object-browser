#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
#   Copyright (c) 2009, Ricardo Lenz (riclc [at] hotmail [dot] com)
#
#   This file is part of PyGtkObjectBrowser.
#
#   PyGtkObjectBrowser is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   PyGtkObjectBrowser is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PyGtkObjectBrowser; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


# Global map:
#
#
# PyGtkObjectBrowser  (YOU ARE HERE)
#        |
#        |
#        +--------- Application
#                        |
#                        |
#                        +------- Inspector
#                        |            |
#                        |            |
#                        |            +-------- Database
#                        |
#                        |
#                        +------- Settings
#                        |
#                        |
#                        +------- ObjectImages
#                        |
#                        |
#                        +------- TypeImages
#
#
#
# This file runs the "Application" class.
#

from pgobApplication import Application

Application().run()
