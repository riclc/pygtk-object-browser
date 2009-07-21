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
import cairo

from objectDetails import ObjectDetails


class App:
    first_time_status = 0

    captured_gui = None
    capturing_gui = False

    main_window = None
    main_w = 0
    main_h = 0

    objectDetails = None

    areas = []
    pass

class Form:
    pass

class ControlArea:
    x = 0
    y = 0
    w = 0
    h = 0
    size = 0 * 0
    ctrl = None

ctrl_over = None
ctrl_selected = None




def get_control_at(x, y, areas):
    menor_size = 0
    menor_size_ctrl = None

    for area in areas:
        if x >= area.x and x < area.x + area.w and y >= area.y and y < area.y + area.h:
            if menor_size_ctrl == None or area.size < menor_size:
                menor_size = area.size
                menor_size_ctrl = area.ctrl

    return menor_size_ctrl



def screenshot(app):

    # supoe que os allocations ja foram feitos.

    app.areas = []
    for obj in app.form.objs:
        if isinstance( obj, gtk.Widget ):
            a = obj.get_allocation()

            area = ControlArea()
            area.x = a.x
            area.y = a.y
            area.w = a.width
            area.h = a.height
            area.ctrl = obj
            area.size = area.w * area.h

            app.areas.append( area )

    app.main_w = app.main_window.get_allocation().width
    app.main_h = app.main_window.get_allocation().height

    # isso força um expose
    drawable = app.main_window.get_snapshot( None )

    app.captured_gui = gtk.gdk.Pixbuf( gtk.gdk.COLORSPACE_RGB,
        False, 8, app.main_w, app.main_h )
    app.captured_gui.get_from_drawable( drawable, \
        gtk.gdk.colormap_get_system(), 0, 0, 0, 0, app.main_w, app.main_h )
    #app.captured_gui.save( "teste.png", "png" )



def on_close(*args):
    gtk.main_quit()


def on_mouse_move(widget, event, app):
    x = int( event.x )
    y = int( event.y )

    global ctrl_over
    ctrl_over = get_control_at( x, y, app.areas )

    app.main_window.queue_draw()


def on_mouse_button_press(widget, event, app):
    x = int( event.x )
    y = int( event.y )

    global ctrl_selected
    ctrl_selected = get_control_at( x, y, app.areas )

    app.main_window.queue_draw()

    app.objectDetails.run_for( ctrl_selected, app.main_window )


def on_focus_in(widget, event, app):
    if app.first_time_status == 0:
        app.first_time_status = 1
    else:
        app.main_window.get_child().hide()

    return False

def on_focus_out(widget, event, app):
    app.main_window.get_child().show()
    return False

def on_configure(widget, event, app):

    if app.main_w != app.main_window.get_allocation().width or \
       app.main_h != app.main_window.get_allocation().height:

           app.captured_gui = None
           app.main_window.queue_draw()

    return False


def on_expose(widget, event, app):
    if app.captured_gui == None:

        if not app.capturing_gui:
            app.capturing_gui = True

            # isso força um expose aqui e agora
            screenshot( app )

            app.capturing_gui = False

            if app.first_time_status == 1:
                app.first_time_status = 2
                app.main_window.get_child().hide()

            # agenda um outro expose pra depois
            app.main_window.queue_draw()
            return False
        else:
            return False

    else:
        global controlArea_over, controlArea_selected

        cr = event.window.cairo_create()

        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        cr.set_source_pixbuf( app.captured_gui, 0, 0 )
        cr.paint()

        for a in app.areas:
            if a.ctrl == ctrl_selected:
                cr.set_dash( [] )
                cr.set_line_width( 3 )
                alpha = 1
            elif a.ctrl == ctrl_over:
                cr.set_dash( [3] )
                cr.set_line_width( 2 )
                alpha = 0.5
            else:
                continue

            grad = cairo.LinearGradient( a.x, a.y, a.x + a.w, a.y + a.h )
            grad.add_color_stop_rgba( 0.0,   0.4, 0.4, 0.9, alpha )
            grad.add_color_stop_rgba( 1.0,   0.2, 0.8, 0.9, alpha )

            cr.set_source( grad )
            cr.rectangle( a.x + 0.5, a.y + 0.5, a.w-1, a.h-1 )
            cr.stroke()

            coords = ( (a.x, a.y), (a.x + a.w-1, a.y), \
                (a.x + a.w-1, a.y + a.h-1), (a.x, a.y + a.h-1) )

            cr.set_dash( [] )
            cr.set_line_width( 1 )
            for coord in coords:
                x = coord[0]
                y = coord[1]

                cr.set_source_rgba( 1, 1, 1, alpha )
                cr.arc( x, y, 3, 0, 2 * 3.14159265 )
                cr.fill()

                cr.set_source_rgba( 0.2, 0.4, 1, alpha )
                cr.arc( x + 0.5, y + 0.5, 3, 0, 2 * 3.14159265 )
                cr.stroke()

        # pára aqui; nao pinta mais os controles do form.
        return True



def run(glade_filename, parentWindow = None, code_add_func = None):
    builder = gtk.Builder()
    builder.add_from_file( glade_filename )

    form = Form()
    form.objs = builder.get_objects()

    app = App()
    app.form = form

    for obj in form.objs:
        try:
            obj_name = obj.get_name()
        except:
            obj_name = obj.__class__.__name__ + "_" + str(hash(obj))

        setattr( form, obj_name, obj )

        if isinstance( obj, gtk.Window ):
            app.main_window = obj

    if app.main_window == None:
        print("*** No window found in the glade file!")
        return

    app.main_window.connect( "focus-in-event", on_focus_in, app )
    app.main_window.connect( "focus-out-event", on_focus_out, app )
    app.main_window.connect( "configure-event", on_configure, app )
    app.main_window.connect( "expose-event", on_expose, app )
    app.main_window.connect( "delete-event", on_close )

    app.main_window.add_events( gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK )
    app.main_window.connect("motion-notify-event", on_mouse_move, app )
    app.main_window.connect("button-press-event", on_mouse_button_press, app )

    app.main_window.set_position( gtk.WIN_POS_CENTER_ON_PARENT )
    app.main_window.set_transient_for( parentWindow )

    # temos que mostrar a janela mesmo, de um jeito ou de outro,
    # pois o gtk usa necessariamente o backend (x11 por ex.) pra
    # desenhar os widgets. uma nova versao (client-side-windows, csw)
    # permite desenhar tudo direto no gdk, sem backends. isso podera
    # ser usado para incorporar texturas, composite, clutter, etc.
    #
    app.main_window.show()

    app.objectDetails = ObjectDetails()
    app.objectDetails.code_add = code_add_func

    gtk.main()


if __name__ == "__main__":
    run( "objectDetails.glade" )
