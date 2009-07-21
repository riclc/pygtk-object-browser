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

class ObjectDetails:

    def __init__(self):

        builder = gtk.Builder()
        builder.add_from_file( \
            os.path.join( os.path.dirname(__file__), "objectDetails.glade" ) )

        self.type_images = TypeImages()
        self.selected_obj = None

        self.window = builder.get_object( "window" )
        self.imgObject = builder.get_object( "imgObject" )
        self.labObject = builder.get_object( "labObject" )

        self.listProps = builder.get_object( "listProps" )
        self.storeProps = builder.get_object( "storeProps" )

        self.listSignals = builder.get_object( "listSignals" )
        self.storeSignals = builder.get_object( "storeSignals" )

        self.textInfo = builder.get_object( "textInfo" )
        self.textInfo.modify_base( gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffbd") )
        self.textInfo.modify_font( pango.FontDescription("8") )

        self.listProps.connect( "cursor-changed", self.on_select_prop )
        self.listSignals.connect( "cursor-changed", self.on_select_signal )
        self.listProps.connect( "row-activated", self.on_exec_prop )
        self.listSignals.connect( "row-activated", self.on_exec_signal )
        self.window.connect( "delete-event", self.on_close )

        self.prepare_columns()

        screen = gtk.gdk.Screen()
        self.window.move( 20, screen.get_height() / 8 )

        self.last_configuration = None

        self.code_add = None



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
        self.listProps.append_column( self.column_new_img() )
        self.listProps.append_column( self.column_new_text(1) )
        self.listProps.append_column( self.column_new_text(2) )
        self.listSignals.append_column( self.column_new_img() )
        self.listSignals.append_column( self.column_new_text(1) )


    def run_for(self, obj, parentWindow = None):
        self.selected_obj = obj

        self.labObject.set_markup( "<b><big>" + obj.get_name() + "</big></b>\n" + \
            "gtk." + type(obj).__name__ )

        self.read_props( obj )
        self.read_signals( obj )

        if self.last_configuration:
            self.set_configuration( self.last_configuration )

        self.window.show()

        self.parentWindow = parentWindow
        if self.parentWindow:
            self.window.set_transient_for( parentWindow )
        else:
            gtk.main()


    def read_props(self, obj):

        self.storeProps.clear()

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
                img = self.type_images.by_name( 'prop_int' )
            elif ptipo == 'gboolean':
                img = self.type_images.by_name( 'prop_bool' )
            elif ptipo == 'gchararray':
                img = self.type_images.by_name( 'prop_string' )
            elif ptipo == 'gfloat':
                img = self.type_images.by_name( 'prop_float' )
            elif ptipo == 'GdkColor':
                img = self.type_images.by_name( 'prop_color' )
            else:
                img = self.type_images.by_name( 'prop_default' )

            self.storeProps.append( [img, pname, ptipo, pdefault, pdesc] )


    def read_signals(self, obj):

        self.storeSignals.clear()

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
                sig_ret = "return None"
            else:
                sig_ret = "return " + details[4].name

            sig_params = details[5]
            if len(sig_params) > 0:

                sparams = ["GtkWidget"]
                for sig_param in sig_params:
                    sparams.append( sig_param.name )

                s_sig_params = ", ".join( sparams )
            else:
                s_sig_params = "GtkWidget"

            s_sig_params = "(" + s_sig_params + ")"

            img = self.type_images.by_name( 'signal_default' )

            if details[2].pytype != type(obj):
                img = self.type_images.by_name( 'signal_parent' )

            if "-event" in sig:
                img = self.type_images.by_name( 'signal_event' )

            self.storeSignals.append( [img, sig, s_sig_params, sig_ret] )



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
        event_name = self.storeSignals.get_value( \
            signal_it, 1 ).replace("-", "_")

        callback = "on_" + self.selected_obj.get_name() + "_" + event_name

        if not only_name:
            callback += self.storeSignals.get_value( signal_it, 2 )

        return callback



    def signal_callback_full(self, signal_it):
        return \
            "def " + self.signal_callback( signal_it ) + ":\n" + \
            "    " + self.storeSignals.get_value( signal_it, 3 )




    def on_select_prop(self, treeview):

        path, col = self.listProps.get_cursor()
        if path == None:
            return

        it = self.storeProps.get_iter( path )

        self.textInfo.get_buffer().set_text( "Default: " + \
            self.storeProps.get_value( it, 3 ) + "\n\n" + \
            self.storeProps.get_value( it, 4 ) )


    def on_select_signal(self, treeview):

        path, col = self.listSignals.get_cursor()
        if path == None:
            return

        it = self.storeSignals.get_iter( path )
        self.textInfo.get_buffer().set_text( self.signal_callback_full(it) )


    def on_exec_prop(self, treeview, path, col):

        it = self.storeProps.get_iter( path )

        prop = self.storeProps.get_value( it, 1 )
        prop_type = self.storeProps.get_value( it, 2 )
        prop_default = self.storeProps.get_value( it, 3 )

        code =  self.selected_obj.get_name() + ".set_property( " + \
            '"' + prop + '"' + ", " + prop_default + " )"

        if self.code_add:
            self.code_add( code )
        else:
            print( code )


    def on_exec_signal(self, treeview, path, col):

        it = self.storeSignals.get_iter( path )
        event_name = self.storeSignals.get_value( it, 1 )

        code = "\n" + \
            self.selected_obj.get_name() + ".connect( " + \
            '"' + event_name + '"' + ", " + self.signal_callback( it, True ) + " )\n" + \
            "\n" + \
            self.signal_callback_full(it) + "\n" + \
            "\n"

        if self.code_add:
            self.code_add( code )
        else:
            print( code )



    def on_close(self, *args):

        self.last_configuration = self.get_configuration()

        if self.parentWindow:
            self.window.hide()
            return True
        else:
            gtk.main_quit()
            return False



    def get_configuration(self):
        x, y = self.window.get_position()
        w, h = self.window.get_size()
        return (x, y, w, h)


    def set_configuration(self, config_tuple ):
        x = config_tuple[0]
        y = config_tuple[1]
        w = config_tuple[2]
        h = config_tuple[3]

        self.window.move( x, y )
        self.window.resize( w, h )





class TypeImages:

    img_names = ( \
        'signal_default', \
        'signal_event', \
        'signal_parent', \

        'prop_default', \
        'prop_int', \
        'prop_bool', \
        'prop_string', \
        'prop_float', \
        'prop_color' \
    )


    def __init__(self):
        self.imgs = {}

        for f in TypeImages.img_names:
            filename = os.path.join( os.path.dirname(__file__), \
                "imgs", "etc", f + ".png" )
            self.imgs[f] = gtk.gdk.pixbuf_new_from_file( filename )


    def by_name(self, image_name):
        return self.imgs[ image_name ]


if __name__ == '__main__':
    ObjectDetails().run_for( gtk.Button("test") )
