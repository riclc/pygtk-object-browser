#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gtk
import cairo
import pango
import os
import os.path

from msgbox import alert
from images import Images
from ideForm import Form
from ideFormTitleBar import draw_titlebar
from ideObjectInspector import ObjectInspector


class IDE:

    def __init__(self):

        builder = gtk.Builder()
        builder.add_from_file( \
            os.path.join( os.path.dirname(__file__), "ide.glade" ) )

        self.window = builder.get_object( "window" )
        self.textInfo = builder.get_object( "textInfo" )
        self.imgObject = builder.get_object( "imgObject" )
        self.labObject = builder.get_object( "labObject" )
        self.formView = builder.get_object( "formView" )
        self.formContainer = builder.get_object( "formContainer" )
        self.formFrame = builder.get_object( "formFrame" )
        self.formBox = builder.get_object( "formBox" )
        self.formTitle = builder.get_object( "formTitle" )
        self.formTitleBar = builder.get_object( "formTitleBar" )
        self.listProps = builder.get_object( "listProps" )
        self.storeProps = builder.get_object( "storeProps" )
        self.listSignals = builder.get_object( "listSignals" )
        self.storeSignals = builder.get_object( "storeSignals" )
        self.labAccess = builder.get_object( "labAccess" )
        self.btnOpenGlade = builder.get_object( "btnOpenGlade" )

        self.textInfo.modify_base( gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffbd") )
        self.textInfo.modify_font( pango.FontDescription("8") )
        self.formView.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("white") )

        self.images = Images()
        self.objectInspector = ObjectInspector( self )
        self.form = Form( self )
        self.analyser = None
        self.glade_file = None

        self.formTitleBar.set_app_paintable( True )
        self.titleBarClose = self.images.by_name( "close" )

        self.formTitleBar.connect( "expose-event", self.on_draw_titlebar )
        self.formBox.connect_after( "expose-event", self.on_draw_border )
        self.window.connect( "delete-event", self.on_close )
        self.btnOpenGlade.connect( "clicked", self.on_open_glade )

        self.listProps.connect( "cursor-changed", self.objectInspector.on_select_prop )
        self.listSignals.connect( "cursor-changed", self.objectInspector.on_select_signal )
        self.listProps.connect( "row-activated", self.objectInspector.on_exec_prop )
        self.listSignals.connect( "row-activated", self.objectInspector.on_exec_signal )




    def run(self, glade_file = None, parentWindow = None, \
            analyser = None):

        self.analyser = analyser
        self.glade_file = glade_file

        self.window.show()

        if self.glade_file:
            self.form.load_from_file( glade_file )

        self.parentWindow = parentWindow
        if self.parentWindow:
            self.window.set_transient_for( parentWindow )
        else:
            gtk.main()


    def on_close(self, *args):

        if self.parentWindow:
            self.window.hide()
            return True
        else:
            gtk.main_quit()
            return False


    def on_draw_titlebar(self, sender, event):

        cr = event.window.cairo_create()
        w = self.formTitle.get_allocation().width
        h = self.formTitle.get_allocation().height

        draw_titlebar( cr, w, h, self.titleBarClose )
        return False


    def on_draw_border(self, sender, event):

        cr = event.window.cairo_create()
        w = self.formBox.get_allocation().width
        h = self.formBox.get_allocation().height

        cr.set_line_width( 1 )
        cr.set_source_rgba( 0, 0, 0, 1 )
        cr.rectangle( 0 + 0.5, -1 + 0.5, w-1, h )
        cr.stroke()

        return True


    def on_open_glade(self, sender):

        if self.glade_file:
            os.system( "glade-3 %s &" % self.glade_file )
        else:
            alert( "No glade file!", "Open Glade file" )


if __name__ == '__main__':
    IDE().run( glade_file = "newCode.glade" )
