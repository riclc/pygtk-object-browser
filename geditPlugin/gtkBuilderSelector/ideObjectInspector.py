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
import gobject
import pango
import os.path

from images import Images



class ObjectInspector:

    def __init__(self, ide):

        self.ide = ide
        self.prepare_columns()



    def column_new_img(self):
        imgRenderer = gtk.CellRendererPixbuf()

        col = gtk.TreeViewColumn()
        col.set_spacing( 3 )
        col.pack_start( imgRenderer, expand=False )
        col.add_attribute( imgRenderer, "pixbuf", 0 )
        return col


    def column_new_text(self, src):
        textRenderer = gtk.CellRendererText()

        col = gtk.TreeViewColumn()
        col.set_spacing( 3 )
        col.pack_start( textRenderer, expand=False )
        col.add_attribute( textRenderer, "text", src )
        return col


    def prepare_columns(self):
        self.ide.listProps.append_column( self.column_new_img() )
        self.ide.listProps.append_column( self.column_new_text(1) )
        self.ide.listProps.append_column( self.column_new_text(2) )
        self.ide.listSignals.append_column( self.column_new_img() )
        self.ide.listSignals.append_column( self.column_new_text(1) )


    def select_obj(self, obj):

        sobj = obj.get_name()

        self.selected_obj = obj

        self.ide.labObject.set_markup( \
            "<b><big>" + sobj + "</big></b>\n" + \
            "gtk." + type(obj).__name__ )

        self.read_props( obj )
        self.read_signals( obj )


        self.ide.labAccess.set_markup( \
            "<small><b>%s</b> is not declared in the code.</small>" % sobj )

        if self.ide.analyser:
            aobjs = self.ide.analyser.list_for_get_object

            for aobj, aline in aobjs:
                if aobj == obj.get_name():
                    lin = aline+1

                    self.ide.labAccess.set_markup( \
                        "<small><b>%s</b> is declared in the code (<b>line %d</b>)</small>" % \
                        (sobj, lin) )
                    break



    def read_props(self, obj):

        self.ide.storeProps.clear()

        try:
            props = gobject.list_properties( type(obj) )
        except:
            props = []

        for prop in props:
            pname = prop.name
            ptipo = prop.value_type.name
            pdefault = str( prop.default_value )
            pdesc = prop.blurb

            if ptipo == 'gint' or ptipo == 'guint':
                img = self.ide.images.by_name( 'prop_int' )
            elif ptipo == 'gboolean':
                img = self.ide.images.by_name( 'prop_bool' )
            elif ptipo == 'gchararray':
                img = self.ide.images.by_name( 'prop_string' )
            elif ptipo == 'gfloat':
                img = self.ide.images.by_name( 'prop_float' )
            elif ptipo == 'GdkColor':
                img = self.ide.images.by_name( 'prop_color' )
            else:
                img = self.ide.images.by_name( 'prop_default' )

            self.ide.storeProps.append( [img, pname, ptipo, pdefault, pdesc] )



    def read_signals(self, obj):

        self.ide.storeSignals.clear()

        try:
            sigs = gobject.signal_list_names( type(obj) )
        except:
            sigs = []


        parents = self.get_parent_list( obj )
        for parent in parents:
            try:
                sigs += gobject.signal_list_names( parent )
            except:
                pass


        for sig in sigs:
            details = gobject.signal_query( sig, type(obj) )

            if details[4].name == 'void':
                sig_ret = "return"
            else:
                sig_ret = "return " + details[4].name

            sig_params = details[5]
            if len(sig_params) > 0:

                sparams = ["self", "widget"]
                for sig_param in sig_params:
                    sp = sig_param.name

                    if sp[:3] == 'Gtk' or sp[:3] == 'Gdk':
                        sp = sp[3:]

                    sp = sp[0].lower() + sp[1:]
                    sparams.append( sp )

                s_sig_params = ", ".join( sparams )
            else:
                s_sig_params = "self, widget"

            s_sig_params = "(" + s_sig_params + ")"

            img = self.ide.images.by_name( 'signal_default' )

            if details[2].pytype != type(obj):
                img = self.ide.images.by_name( 'signal_parent' )

            if "-event" in sig:
                img = self.ide.images.by_name( 'signal_event' )

            self.ide.storeSignals.append( [img, sig, s_sig_params, sig_ret] )




    def get_parent_list(self, obj):

        tobj = type(obj)

        ancs = []
        while True:
            try:
                anc = gobject.type_parent( tobj )
            except:
                anc = None

            if anc == None:
                break
            else:
                tobj = anc.pytype

                if not tobj:
                    continue

                ancs.append( tobj )

        return ancs





    def signal_callback(self, signal_it, only_name = False):

        event_name = self.ide.storeSignals.get_value( \
            signal_it, 1 ).replace("-", "_")

        callback = "on_" + self.selected_obj.get_name() + "_" + event_name

        if not only_name:
            callback += self.ide.storeSignals.get_value( signal_it, 2 )

        return callback




    def signal_callback_full(self, signal_it):

        return \
            "def " + self.signal_callback( signal_it ) + ":\n" + \
            "    " + self.ide.storeSignals.get_value( signal_it, 3 )




    def on_select_prop(self, treeview):

        path, col = self.ide.listProps.get_cursor()
        if path == None:
            return

        it = self.ide.storeProps.get_iter( path )

        self.ide.textInfo.get_buffer().set_text( "Default: " + \
            self.ide.storeProps.get_value( it, 3 ) + "\n\n" + \
            self.ide.storeProps.get_value( it, 4 ) )



    def on_select_signal(self, treeview):

        path, col = self.ide.listSignals.get_cursor()
        if path == None:
            return

        it = self.ide.storeSignals.get_iter( path )
        self.ide.textInfo.get_buffer().set_text( self.signal_callback_full(it) )



    def on_exec_prop(self, treeview, path, col):

        it = self.ide.storeProps.get_iter( path )

        prop = self.ide.storeProps.get_value( it, 1 )
        prop_type = self.ide.storeProps.get_value( it, 2 )
        prop_default = self.ide.storeProps.get_value( it, 3 )

        code = self.selected_obj.get_name() + ".set_property( " + \
            '"' + prop + '"' + ", " + prop_default + " )"

        self.ide.analyser.code_add( code )




    def on_exec_signal(self, treeview, path, col):

        it = self.ide.storeSignals.get_iter( path )
        event_name = self.ide.storeSignals.get_value( it, 1 )

        code = "\n" + \
            self.selected_obj.get_name() + ".connect( " + \
            '"' + event_name + '"' + ", " + self.signal_callback( it, True ) + " )\n" + \
            "\n" + \
            self.signal_callback_full(it) + "\n" + \
            "\n"

        self.ide.analyser.code_add( code )
