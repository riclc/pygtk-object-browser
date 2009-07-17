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
#                        |            +-------- Database
#                        |
#                        |
#                        +------- Settings (YOU ARE HERE)
#                        |
#                        |
#                        +------- ObjectImages
#                        |
#                        |
#                        +------- TypeImages
#
#
#
# This file defines the "Settings" class.
#


import gconf



GCONF_KEY = "/apps/py-gtk-object-browser/"


class Settings:

    def __init__(self, app):

        self.app = app

        self.HidePythonInternals = False
        self.ShowOnlyStar = False
        self.IconForSetGet = True
        self.InterfaceFont = False



    def read_from_gconf(self):

        gclient = gconf.client_get_default()

        try:
            self.HidePythonInternals = gclient.get( \
                GCONF_KEY + "HidePythonInternals" ).get_bool()

            self.ShowOnlyStar = gclient.get( \
                GCONF_KEY + "ShowOnlyStar" ).get_bool()

            self.IconForSetGet = gclient.get( \
                GCONF_KEY + "IconForSetGet" ).get_bool()

            self.InterfaceFont = gclient.get( \
                GCONF_KEY + "InterfaceFont" ).get_bool()
        except:
            pass




    def write_to_gconf(self):

        gclient = gconf.client_get_default()

        try:
            gclient.set_bool( GCONF_KEY + "HidePythonInternals", \
                self.HidePythonInternals )

            gclient.set_bool( GCONF_KEY + "ShowOnlyStar", \
                self.ShowOnlyStar )

            gclient.set_bool( GCONF_KEY + "IconForSetGet", \
                self.IconForSetGet )

            gclient.set_bool( GCONF_KEY + "InterfaceFont", \
                self.InterfaceFont )
        except:
            pass




    def read_from_gui_fields(self):

        self.HidePythonInternals = self.app.checkHidePythonInternals.get_active()
        self.ShowOnlyStar = self.app.checkShowOnlyStar.get_active()
        self.IconForSetGet = self.app.checkIconForSetGet.get_active()
        self.InterfaceFont = self.app.checkInterfaceFont.get_active()


    def write_to_gui_fields(self):

        self.app.checkHidePythonInternals.set_active( self.HidePythonInternals )
        self.app.checkShowOnlyStar.set_active( self.ShowOnlyStar )
        self.app.checkIconForSetGet.set_active( self.IconForSetGet )
        self.app.checkInterfaceFont.set_active( self.InterfaceFont )



    def config_for_live_updates(self):

        # if the path includes the last '/', gconf will not accept it
        # for gclient.add_dir( ).
        #
        path = GCONF_KEY[:-1]

        gclient = gconf.client_get_default()
        gclient.add_dir( path, gconf.CLIENT_PRELOAD_NONE )

        self.handle_HidePythonInternals = gclient.notify_add( GCONF_KEY + \
            "HidePythonInternals", self.on_live_update )

        self.handle_ShowOnlyStar = gclient.notify_add( GCONF_KEY + \
            "ShowOnlyStar", self.on_live_update )

        self.handle_IconForSetGet = gclient.notify_add( GCONF_KEY + \
            "IconForSetGet", self.on_live_update )

        self.handle_InterfaceFont = gclient.notify_add( GCONF_KEY + \
            "InterfaceFont", self.on_live_update )


    def on_live_update(self, gclient, connection_id, gconf_entry, params):

        # there should not be an extra "params" in this callback.
        # but python-gconf will fail if this is not made.
        # if on gclient.notify_add we pass some 'user data' into,
        # then 'params' will contain this 'user data' in the form
        # of a tuple. but we do not pass anything, that is the problem.
        # imho, probably a bug in python-gconf itself.
        #
        if gconf_entry.value == None:
            return

        if gconf_entry.value.type != gconf.VALUE_BOOL:
            return

        val = gconf_entry.get_value().get_bool()

        #debug...
        #print "live update: %s = %s" % ( gconf_entry.get_key(), str(val))

        if connection_id == self.handle_HidePythonInternals:
            self.HidePythonInternals = val

        elif connection_id == self.handle_ShowOnlyStar:
            self.ShowOnlyStar = val

        elif connection_id == self.handle_IconForSetGet:
            self.IconForSetGet = val

        elif connection_id == self.handle_InterfaceFont:
            self.InterfaceFont = val

        self.write_to_gui_fields()




# If you run this file, then the program will run.
if __name__ == '__main__':
    import PyGtkObjectBrowser
