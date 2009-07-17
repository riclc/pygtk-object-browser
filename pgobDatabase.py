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
# PyGtkObjectBrowser
#        |
#        |
#        +--------- Application
#                        |
#                        |
#                        +------- Inspector
#                        |            |
#                        |            |
#                        |            +-------- Database (YOU ARE HERE)
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
# This file defines the "Database" class.
#


import os
import os.path



class Database:

    db = {}
    db_ancestry = {}
    db_ctor = {}


    def __init__(self):

        full_class_name = ""
        current_class = None
        current_method = None
        current_ctor = None

        f = open( os.path.join( "data", "db.dat" ), "r" )

        for ln in f.readlines():

            ln = ln.strip()

            if len(ln) == 0:
                continue

            elif ln[0] == "#":
                continue

            # starts a new class definition
            elif ln[0] == "C":
                full_class_name = ln[2:]

                self.db[ full_class_name ] = {}
                self.db_ancestry[ full_class_name ] = []
                self.db_ctor[ full_class_name ] = []

                current_class = self.db[ full_class_name ]


            # starts a new method definition
            elif ln[0] == "m":
                method_name = ln[2:]
                current_class[ method_name ] = []
                current_method = current_class[ method_name ]
                current_ctor = None

            # starts a new constructor definition
            elif ln[0] == "c":
                self.db_ctor[ full_class_name ].append( [] )
                current_ctor = self.db_ctor[ full_class_name ][:-1]
                current_method = None

            # appends a method parameter to the current method/constructor
            elif ln[0] == "p":
                parameter = ln[2:]
                if current_ctor == None:
                    current_method.append( parameter )
                else:
                    current_ctor.append( parameter )

            # specifies one ancestry of the current class
            elif ln[0] == "a":
                ancestry = ln[2:]
                self.db_ancestry[ full_class_name ].append( ancestry )

        f.close()



    def get_class_methods(self, full_class_name):
        return self.db[ full_class_name ]

    def get_method_params(self, full_class_name, method_name):
        return self.db[ full_class_name ][ method_name ]

    def get_class_constructors(self, full_class_name):
        return self.db_ctor[ full_class_name ]


# If you run this file, then the program will run.
if __name__ == '__main__':
    import PyGtkObjectBrowser
