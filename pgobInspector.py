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
#                        +------- Inspector  (YOU ARE HERE)
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
# This file defines the "Inspector" class.
#

import gtk
import atk
import gobject
import inspect


from pgobDatabase import Database




class Inspector:

    def __init__(self, app):

        self.app = app
        self.database = Database()



    def describe_full_class_name(self, full_class_name):

        last_dot = full_class_name.rfind(".")

        class_name = full_class_name[ last_dot + 1 : ]
        class_pak = full_class_name[ : last_dot ]
        class_module = None

        if class_pak == "gtk.gdk":
            class_module = gtk.gdk

        elif class_pak == "gobject":
            class_module = gobject

        elif class_pak == "gtk":
            class_module = gtk

        elif class_pak == "atk":
            class_module = atk

            if class_name == 'Implementor':
                class_name = 'ImplementorIface'


        if class_module == None:
            print "*** Error: no valid module for <%s>" % full_class_name
            return None


        class_type = getattr( class_module, class_name )

        return class_name, class_type, class_pak




    def analyse(self, full_class_name):

        class_name, class_type, class_pak = \
            self.describe_full_class_name( full_class_name )

        if class_name == "":
            print "*** Error: class name invalid!"
            return

        self.fill_membros( full_class_name, class_name, class_type )
        self.fill_ancestry( full_class_name, class_name, class_type )
        self.fill_interfaces( full_class_name, class_name, class_type )
        self.fill_props( full_class_name, class_name, class_type )
        self.fill_signals( full_class_name, class_name, class_type )




    def get_type_image(self, name):
        return self.app.type_images.get_image( name )



    def get_object_image(self, full_class_name ):
        return self.app.object_images.get_image( full_class_name )



    def get_method_signature(self, method, params):

        signature = method

        if len(params) > 0:
            signature += " (" + \
                reduce( lambda x,y: x + ", " + y, params ) + ")"
        else:
            signature += " ()"

        return signature



    def get_method_signature_from_database(self, full_class_name, method):
        params = self.database.get_method_params( full_class_name, method )
        return self.get_method_signature( method, params )




    def fill_membros(self, full_class_name, class_name, class_type):
        self.app.storeMembros.clear()


        # read the class documentation

        obj_doc = getattr( class_type, "__doc__" )
        if obj_doc != None:
            self.app.textDoc.get_buffer().set_text( obj_doc )
        else:
            self.app.textDoc.get_buffer().set_text( "No documentation.\n" + \
                "The __doc__ attribute for this class is null." )


        # list all constructors
        #
        for ctor in self.database.get_class_constructors( full_class_name ):
            estrela = self.get_type_image( "estrela" )
            img = self.get_type_image( "method_constructor" )

            signature = self.get_method_signature( full_class_name, ctor )
            self.app.storeMembros.append( [estrela, img, signature, "constructor"] )


        # list all that the python runtime can for the current class type
        #
        for d in dir(class_type):

            dtype = str( getattr(class_type, d) )

            # chooses the image for this type

            if type( getattr(class_type, d) ) == str:
                img = self.get_type_image( 'string' )
                dtype = "[string]"

            elif "<class" in dtype:
                img = self.get_type_image( 'class' )

            elif "<deprecated" in dtype:
                img = self.get_type_image( 'deprecated' )

            elif "<attribute" in dtype:
                img = self.get_type_image( 'attribute' )

            elif "<method 'get_" in dtype or \
                 "<method 'set_" in dtype or \
                 "<method 'is_" in dtype:

                if self.app.settings.IconForSetGet:
                    img = self.get_type_image( 'method_get_set' )
                else:
                    img = self.get_type_image( 'method' )

            elif "<method" in dtype:
                img = self.get_type_image( 'method' )

            elif "<built-in function" in dtype or \
                 "<built-in method" in dtype or \
                 "<slot wrapper" in dtype:
                img = self.get_type_image( 'method_special' )

            else:
                img = self.get_type_image( 'default' )


            # is this member in the database? if so, adds a 'star' icon,
            # and then describes its parameters.
            #

            if d in self.database.get_class_methods( full_class_name ):

                signature = self.get_method_signature_from_database( full_class_name, d )
                estrela = self.get_type_image( 'estrela' )

            else:

                # only members with the 'star' icon are to be shown?
                # if so, do not add this member to the list.
                #
                if self.app.settings.ShowOnlyStar:
                    continue


                # is this a python internal member? (something like:
                # '__member')
                #
                if self.app.settings.HidePythonInternals and d[:2] == '__':
                    continue

                signature = d
                estrela = None


            self.app.storeMembros.append( [estrela, img, signature, dtype] )




    def ancestry_button_event_on_click(self, sender, ancestry_class):

        index = 0
        it = self.app.storeObjetos.get_iter_first()

        while it != None:
            classe = self.app.storeObjetos.get_value( it, 1 )
            if classe == ancestry_class:
                self.app.listaObjetos.set_cursor( (index,) )
                return

            it = self.app.storeObjetos.iter_next( it )
            index += 1

        print( "*** Error: did not find <%s>" % ancestry_class )



    def fill_ancestry(self, full_class_name, class_name, class_type):

        self.app.areaClasses.foreach( lambda btn: self.app.areaClasses.remove(btn) )

        ancs = []
        while True:
            try:
                anc = gobject.type_parent( class_type )
            except:
                anc = None

            if anc == None:
                break
            else:
                class_type = anc.pytype

                if class_type == None:
                    continue

                if anc.name == 'GInitiallyUnowned':
                    continue

                if class_type.__name__ == 'GObject':
                    class_str = "gobject.GObject"
                else:
                    class_str = \
                        class_type.__module__ + '.' + class_type.__name__

                ancs.append( class_str )

        ancs.reverse()
        ancs.append( full_class_name )

        for anc in ancs:
            hb = gtk.HBox()
            hb.add( gtk.image_new_from_pixbuf( self.get_object_image(anc) ) )
            hb.add( gtk.Label(anc) )
            hb.set_spacing( 2 )
            hb.show_all()

            b = gtk.Button()
            b.connect( "clicked", self.ancestry_button_event_on_click, anc )
            b.add( hb )
            b.show()

            self.app.areaClasses.add( b )




    def fill_interfaces(self, full_class_name, class_name, class_type):

        self.app.areaInterfaces.foreach( lambda btn: self.app.areaInterfaces.remove(btn) )

        try:
            interfaces = gobject.type_interfaces( class_type )
        except:
            interfaces = []

        for interface in interfaces:
            iname = interface.name

            if iname[:3] == "Gtk":
                iname = "gtk." + iname[3:]
            elif iname[:3] == "Atk":
                iname = "atk." + iname[3:]

                if iname == 'atk.ImplementorIface':
                    iname = 'atk.Implementor'
            else:
                continue

            hb = gtk.HBox()
            hb.add( gtk.image_new_from_pixbuf( self.get_object_image( iname ) ) )
            hb.add( gtk.Label(iname) )
            hb.set_spacing( 2 )
            hb.show_all()

            b = gtk.Button()
            b.connect( "clicked", self.ancestry_button_event_on_click, iname )
            b.add( hb )
            b.show()

            self.app.areaInterfaces.add( b )



    def fill_props(self, full_class_name, class_name, class_type):

        self.app.storeProps.clear()

        try:
            props = gobject.list_properties( class_type )
        except:
            props = []

        for prop in props:
            pname = prop.name
            ptipo = prop.value_type.name
            pdefault = str( prop.default_value )
            pdesc = prop.blurb

            if ptipo == 'gint' or ptipo == 'guint':
                img = self.get_type_image( 'prop_int' )

            elif ptipo == 'gboolean':
                img = self.get_type_image( 'prop_bool' )

            elif ptipo == 'gchararray':
                img = self.get_type_image( 'prop_string' )

            elif ptipo == 'gfloat':
                img = self.get_type_image( 'prop_float' )

            elif ptipo == 'GdkColor':
                img = self.get_type_image( 'prop_color' )

            else:
                img = self.get_type_image( 'prop_default' )

            py_ptipo = self.gtype_to_py( ptipo )

            self.app.storeProps.append( [img, pname, py_ptipo, pdefault, pdesc] )



    def gtype_to_py(self, gt):

        # pythonize types

        if gt == 'void': return 'None'
        if gt == 'gboolean': return 'bool'
        if gt == 'gint' or gt == 'guint': return 'int'
        if gt == 'gfloat' or gt == 'gdouble': return 'float'
        if gt == 'gchararray': return 'str'

        if gt[:3] == 'Gtk': return "gtk." + gt[3:]
        if gt[:3] == 'Gdk': return "gtk.gdk." + gt[3:]

        return gt



    def fill_signals(self, full_class_name, class_name, class_type):

        self.app.storeSignals.clear()

        try:
            sigs = gobject.signal_list_names( class_type )
        except:
            sigs = []

        for sig in sigs:
            details = gobject.signal_query( sig, class_type )

            sig_id = details[0]
            sig_ret = self.gtype_to_py( details[4].name )

            sig_params = details[5]
            if len(sig_params) > 0:

                sparams = []
                for sig_param in sig_params:
                    sparams.append( self.gtype_to_py( sig_param.name ) )

                s_sig_params = ", ".join( sparams )
            else:
                s_sig_params = "<None>"

            img = self.get_type_image( 'signal_default' )
            if "-event" in sig:
                img = self.get_type_image( 'signal_event' )

            self.app.storeSignals.append( [img, sig, sig_id, sig_ret, s_sig_params] )



    def is_interface(self, full_class_name):

        class_name, class_type, class_pak = \
            self.describe_full_class_name( full_class_name )

        try:
            type_name = gobject.type_name( class_type )
            type_info = gobject.type_from_name( type_name )
        except:
            return False

        return type_info.is_interface()



# If you run this file, then the program will run.
if __name__ == '__main__':
    import PyGtkObjectBrowser
