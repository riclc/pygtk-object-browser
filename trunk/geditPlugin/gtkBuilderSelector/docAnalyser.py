#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2009 Ricardo Lenz
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.



class DocAnalyser:

    def __init__(self):
        self.doc = None
        self.var_builder = None
        self.builder_file = None


    def inspect(self, doc):
        self.doc = doc
        self.var_builder = None
        self.builder_file = None

        bounds = self.doc.get_bounds()
        lines = range( bounds[0].get_line(), bounds[1].get_line()+1 )

        for i in lines:
            line_start = self.doc.get_iter_at_line( i )
            line_end = line_start.copy()
            line_end.forward_to_line_end()

            line_text = self.doc.get_text( line_start, line_end )
            self.inspect_line( line_text )


    def inspect_line(self, lin):
        if self.var_builder == None:
            pos = lin.find( "gtk.Builder(" )
            if pos != -1:
                pos = lin.find( "=" )
                if pos != -1:
                    self.var_builder = lin[: pos].strip()
                    print( "Found gtk.Builder variable: <%s>" % self.var_builder )

        elif self.builder_file == None:
            pos = lin.find( "add_from_file" )
            if pos != -1:
                pos += len( "add_from_file" )
                if self.var_builder in lin:

                    lin = lin[ pos: ]

                    pos = lin.find( "(" )
                    if pos != -1:

                        lin = lin[ pos+1: ]

                        p1 = lin.find( "\"" )
                        p2 = lin.find( "\'" )

                        if p1 != -1 and p2 == -1:
                            pos = p1
                            ch = "\""
                        elif p1 == -1 and p2 != -1:
                            pos = p2
                            ch = "\'"
                        elif p1 != -1 and p2 != -1:
                            if p1 < p2:
                                pos = p1
                                ch = "\""
                            else:
                                pos = p2
                                ch = "\'"
                        else:
                            pos = -1

                        if pos != -1:
                            lin = lin[ pos+1: ]
                            pos_end = lin.find( ch )

                            if pos_end != -1:
                                self.builder_file = lin[ :pos_end ]
                                print( "Found gtk.Builder file: <%s>" % self.builder_file )
