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
#        +--------- Application  (YOU ARE HERE)
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
# This file defines the "Application" class.
#

import gtk
import pango
import cairo


from pgobInspector import Inspector
from pgobImages import ObjectImages, TypeImages
from pgobSettings import Settings




class Application:

    def __init__(self):

        builder = gtk.Builder()
        builder.add_from_file( "PyGtkObjectBrowser.glade" )

        self.janela = builder.get_object( "window" )
        self.textDoc = builder.get_object( "textDoc")
        self.boxLogo = builder.get_object( "boxLogo" )


        # check buttons

        self.checkHidePythonInternals = builder.get_object( "checkHidePythonInternals" )
        self.checkShowOnlyStar = builder.get_object( "checkShowOnlyStar" )
        self.checkIconForSetGet = builder.get_object( "checkIconForSetGet" )
        self.checkInterfaceFont = builder.get_object( "checkInterfaceFont" )


        # list objects

        self.listaObjetos = builder.get_object( "listaObjetos" )
        self.storeObjetos = builder.get_object( "storeObjetos")

        self.listaMembros = builder.get_object( "listaMembros" )
        self.storeMembros = builder.get_object( "storeMembros")

        self.listProps = builder.get_object( "listProps" )
        self.storeProps = builder.get_object( "storeProps" )

        self.listSignals = builder.get_object( "listSignals" )
        self.storeSignals = builder.get_object( "storeSignals" )

        # ancestry / interfaces objects

        self.areaClasses = builder.get_object( "areaClasses" )
        self.viewClasses = builder.get_object("viewClasses")

        self.areaInterfaces = builder.get_object( "areaInterfaces" )
        self.viewInterfaces = builder.get_object("viewInterfaces")


        # some widget configuration

        self.config_font_and_colors()
        self.prepare_lists()


        # our other main classes

        self.inspector = Inspector( self )
        self.object_images = ObjectImages()
        self.type_images = TypeImages()
        self.settings = Settings( self )


        # load settings

        self.settings.read_from_gconf()
        self.settings.write_to_gui_fields()
        self.settings.config_for_live_updates()


        # events

        self.janela.connect( "delete-event", self.on_janela_destroy )
        self.listaObjetos.connect( "cursor-changed", self.on_select_class )

        self.checkHidePythonInternals.connect( "toggled", self.on_option_toggled )
        self.checkShowOnlyStar.connect( "toggled", self.on_option_toggled )
        self.checkIconForSetGet.connect( "toggled", self.on_option_toggled )
        self.checkInterfaceFont.connect( "toggled", self.on_option_toggled )

        self.viewClasses.connect_after( "expose_event", \
            self.on_ancestry_expose, "classes" )

        self.viewInterfaces.connect_after( "expose_event", \
            self.on_ancestry_expose, "interfaces" )

        self.boxLogo.connect( "expose_event", self.on_box_logo_expose )
        self.boxLogo.set_app_paintable( True )



        # fills the object list with the objects that have images
        #

        self.fill_object_list()






    def fill_object_list(self):

        objs = self.object_images.get_object_list()
        self.storeObjetos.clear()

        for obj in objs:
            img = self.object_images.get_image( obj )
            self.storeObjetos.append( [ img, obj ] )



    def config_font_and_colors(self):

        cl_textDoc = gtk.gdk.color_parse( "#fdffca" )
        cl_classes = gtk.gdk.color_parse( "#c8dbe1" )
        cl_interfaces = gtk.gdk.color_parse( "#e4f29d" )

        self.textDoc.modify_font( pango.FontDescription("Tahoma 8") )

        self.textDoc.modify_base( gtk.STATE_NORMAL, cl_textDoc )
        self.viewClasses.modify_bg( gtk.STATE_NORMAL, cl_classes )
        self.viewInterfaces.modify_bg( gtk.STATE_NORMAL, cl_interfaces )


    def new_column(self, fonte = None, text_src = None, img_src = None, \
        cor_texto = '', resize = False, title = '', sort_id = -1):

        coluna = gtk.TreeViewColumn()
        coluna.set_spacing( 3 )
        coluna.set_resizable( resize )
        coluna.set_title( title )

        if img_src != None:
            imgRenderer = gtk.CellRendererPixbuf()
            coluna.pack_start( imgRenderer, expand=False )
            coluna.add_attribute( imgRenderer, "pixbuf", img_src )

        if text_src != None:
            textRenderer = gtk.CellRendererText()

            if fonte != None:
                textRenderer.set_property( "font", fonte )

            if cor_texto != '':
                textRenderer.set_property( "foreground", cor_texto )

            coluna.pack_start( textRenderer, expand=False )
            coluna.add_attribute( textRenderer, "text", text_src )

        coluna.set_sort_column_id( sort_id )
        return coluna




    def sort_func_metodo_estrela(self, model, iter1, iter2):

        img1 = model.get_value( iter1, 0 )
        img2 = model.get_value( iter2, 0 )

        if img1 == img2:
            return 0
        elif img1 != None:
            return -1
        else:
            return +1


    def sort_func_metodo_nome(self, model, iter1, iter2):

        nome1 = model.get_value( iter1, 0 )
        nome2 = model.get_value( iter2, 0 )

        if nome1 == nome2:
            return 0
        elif nome1 < nome2:
            return -1
        else:
            return +1



    def prepare_lists(self):

        # Object list
        self.listaObjetos.append_column( self.new_column("9", text_src=1, img_src=0) )

        # Member list
        self.storeMembros.set_sort_func( 0, self.sort_func_metodo_estrela )
        self.storeMembros.set_sort_func( 1, self.sort_func_metodo_nome )

        self.listaMembros.append_column( self.new_column( img_src=0, sort_id = 0 ) )

        self.listaMembros.append_column( \
            self.new_column( fonte = "Monospace 9", \
                text_src=2, img_src=1, resize=True, \
                title="Name", sort_id = 1 ) )

        self.listaMembros.append_column( \
            self.new_column( fonte = "8", \
                text_src=3, cor_texto="#979797", \
                resize=True, title="Type") )


        # Property list
        self.listProps.append_column( self.new_column("", img_src=0) )
        self.listProps.append_column( self.new_column(title="Name", text_src=1) )
        self.listProps.append_column( self.new_column(title="Type", text_src=2) )
        self.listProps.append_column( self.new_column(title="Default", text_src=3) )
        self.listProps.append_column( self.new_column(title="Desc.", text_src=4) )

        # Signal list
        self.listSignals.append_column( self.new_column("", img_src=0) )
        self.listSignals.append_column( self.new_column(title="Name", text_src=1) )
        self.listSignals.append_column( self.new_column(title="ID", text_src=2) )
        self.listSignals.append_column( self.new_column(title="Returns", text_src=3) )
        self.listSignals.append_column( self.new_column(title="Params", text_src=4) )





    def on_janela_destroy(self, sender, event):

        # in case there were no events which caused the storage of
        # the keys.
        #
        self.settings.write_to_gconf()

        gtk.main_quit()


    def on_option_toggled(self, sender):

        # this event ("toggled") only hapens when the check button's value
        # is changed to another value (it was False and now is True,
        # or it was True and now is False). this can occur either through
        # the user clicking on it or thru check button's set_active(..) method.
        # but, in case set_active(..) method is called, keep in mind that it
        # will run the 'toggled' event only if the new value being set is
        # different from the old value.
        #

        self.settings.read_from_gui_fields()
        self.settings.write_to_gconf()

        if sender == self.checkInterfaceFont:
            self.fill_object_list()
        else:
            self.on_select_class( self.listaMembros )


    def on_select_class(self, treeview):

        path, col = self.listaObjetos.get_cursor()
        if path == None:
            return

        it = self.storeObjetos.get_iter( path )
        full_class_name = self.storeObjetos.get_value( it, 1 )

        self.inspector.analyse( full_class_name )



    def on_ancestry_expose(self, widget, event, tip):

        widget = widget.get_child()
        w = widget.get_allocation().width
        h = widget.get_allocation().height

        cr = event.window.cairo_create()

        grad = cairo.LinearGradient( 0, h/1.5, 0, h-1 )
        if tip == 'classes':
            r, g, b = 0.3, 0.4, 0.5
        else:
            r, g, b = 0.5, 0.4, 0.3

        grad.add_color_stop_rgba( 0.0,   r, g, b, 0.0 )
        grad.add_color_stop_rgba( 1.0,   r-0.2, g+0.1, b+0.1, 0.5 )

        cr.set_source( grad )
        cr.rectangle( 0, 0, w-1, h-1 )
        cr.fill()

        cr.set_line_width( 1 )
        cr.set_source_rgba( r-0.1, g+0.1, b+0.2, 1 )
        cr.rectangle( 0 + 0.5, 0 + 0.5, w-1, h-1 )
        cr.stroke()

        return False



    def on_box_logo_expose(self, widget, event):

        widget = widget.get_child()
        w = widget.get_allocation().width
        h = widget.get_allocation().height

        cr = event.window.cairo_create()

        grad = cairo.LinearGradient( 0, 0, w-1, 0 )
        grad.add_color_stop_rgba( 1.0,   1, 1, 1, 0.0 )
        grad.add_color_stop_rgba( 0.0,   0.3, 0.6, 1, 0.5 )

        cr.set_source( grad )
        cr.rectangle( 0, 0, w-1, h-1 )
        cr.fill()

        cr.set_line_width( 1 )
        cr.set_source_rgba( 0.2, 0.4, 0.8, 0.5 )
        cr.rectangle( 0 + 0.5, 0 + 0.5, w-1, h-1 )
        cr.stroke()

        return False



    def run(self):

        self.janela.show()
        gtk.main()



# If you run this file, then the program will run.
if __name__ == '__main__':
    import PyGtkObjectBrowser
