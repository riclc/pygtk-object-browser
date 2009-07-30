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


import gtk



class DocAnalyser:


    def reset(self):
        self.var_builder = None
        self.builder_file = None
        self.last_line_for_get_object = None
        self.list_for_get_object = []


    def __init__(self):
        self.doc = None
        self.view = None
        self.reset()


    def re_inspect(self):
        self.inspect( self.doc, self.view )


    def inspect(self, doc, view):
        self.doc = doc
        self.view = view

        self.reset()

        bounds = self.doc.get_bounds()
        lines = range( bounds[0].get_line(), bounds[1].get_line()+1 )


        pre_line = ""

        for i in lines:
            line_start = self.doc.get_iter_at_line( i )

            # without this, empty lines will make for repeated lines
            if line_start.ends_line():
                continue

            line_end = line_start.copy()
            line_end.forward_to_line_end()

            line_text = self.doc.get_text( line_start, line_end ).strip()

            if line_text[-1:] == '\\':
                pre_line = line_text[:-1]
            elif pre_line:
                line_text = pre_line + line_text
                pre_line = ""

            if not pre_line:
                self.inspect_line( line_text, i )




    def find_string(self, lin):

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
                return lin[ :pos_end ]

        return None




    def inspect_line(self, lin, lin_num ):

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

                        self.builder_file = self.find_string( lin )
                        if self.builder_file:
                            print( "Found gtk.Builder file: <%s>" % self.builder_file )

        else:
            s_get_object = self.var_builder + ".get_object("

            pos = lin.find( s_get_object )
            if pos != -1:

                pos += len( s_get_object )
                lin = lin[ pos: ]

                sobj = self.find_string( lin )
                self.list_for_get_object.append( [sobj, lin_num] )

                self.last_line_for_get_object = lin_num




    def code_add(self, code, insert_at_line = -1):

        if insert_at_line == -1:
            it = self.doc.get_end_iter()
        else:
            it = self.doc.get_iter_at_line( insert_at_line )

        self.doc.insert( it, code )


        while gtk.events_pending():
            gtk.main_iteration( block=False )


        if insert_at_line == -1:
            it = self.doc.get_end_iter()
        else:
            it = self.doc.get_iter_at_line( insert_at_line )

        self.view.scroll_to_iter( it, within_margin = 0.05, \
            use_align = True, xalign = 0.0, yalign = 1.0 )

        self.re_inspect()


    def code_add_for_get_object(self, sobj):

        for obj, lin in self.list_for_get_object:
            if obj == sobj:
                return # do not add the same object again

        code = "        self.%s = %s.get_object( \"%s\" )\n" % \
                (sobj, self.var_builder, sobj)

        line_num = self.last_line_for_get_object+1

        self.code_add( code, line_num )
