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
#                        +------- Settings
#                        |
#                        |
#                        +------- ObjectImages  (YOU ARE HERE)
#                        |
#                        |
#                        +------- TypeImages    (YOU ARE HERE)
#
#
#
# This file defines both "ObjectImages" and "TypeImages" classes.
#


import gtk
import os
import os.path



class ObjectImages:

    def __init__(self):

        self.objects = []
        self.imgs = {}

        obj_imgs = os.listdir( os.path.join( "data", "imgs", "objects" ) )

        for obj_img in obj_imgs:
            if obj_img[-3:].lower() != "png":
                continue

            obj_name = obj_img[:-4]

            filename = os.path.join( "data", "imgs", "objects", obj_img )

            self.objects.append( obj_name )
            self.imgs[ obj_name ] = gtk.gdk.pixbuf_new_from_file( filename )

        self.objects.sort()


    def get_object_list(self):
        return self.objects

    def get_image_list(self):
        return self.imgs

    def get_image(self, object_name):
        return self.imgs[ object_name ]




class TypeImages:

    img_names = ( \
        'default', \
        'class', \
        'method', \
        'attribute', \
        'string', \
        'deprecated', \
        'method_special', \
        'method_get_set', \
        'method_constructor', \
        'estrela', \
        'signal_default', \
        'signal_event', \
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

            filename = os.path.join( "data", "imgs", "etc", f + ".png" )
            self.imgs[ f ] = gtk.gdk.pixbuf_new_from_file( filename )



    def get_image(self, image_name):
        return self.imgs[ image_name ]


# If you run this file, then the program will run.
if __name__ == '__main__':
    import PyGtkObjectBrowser
