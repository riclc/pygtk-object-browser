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



import gtk
import gobject
import pango
import inspect
import os
import os.path
import cairo

imagens_classe = ( \
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
    'prop_default', \
    'prop_int', \
    'prop_bool', \
    'prop_string', \
    'prop_float', \
    'prop_color' \
)


imgs = {}
imgs2 = {}
objetos = []
db = {}
db_anc = {}



def carregaBancoMetodos():
    global db, db_anc

    cur_classe = None
    cur_metodo = None

    f = open( os.path.join( "data", "db.dat" ), "r" )
    for ln in f.readlines():

        ln = ln.strip()

        if len(ln) == 0:
            continue

        elif ln[0] == "#":
            continue

        elif ln[0] == "C":
            classe = ln[2:]
            db[classe] = {}
            db_anc[classe] = []
            cur_classe = db[classe]

        elif ln[0] == "m" or ln[0] == "c":
            metodo = ln[2:]
            cur_classe[metodo] = []
            cur_metodo = cur_classe[metodo]

        elif ln[0] == "p":
            param = ln[2:]
            cur_metodo.append( param )

        elif ln[0] == "a":
            anc = ln[2:]
            db_anc[classe].append( anc )

    f.close()


def carregaObjetos():
    global objetos

    obj_imgs = os.listdir( os.path.join( "data", "imgs", "objects" ) )

    for obj_img in obj_imgs:
        if obj_img[-3:].lower() != "png":
            continue

        objetos.append( obj_img[:-4] )

    objetos.sort()


def carregaImagens():
    global imgs, imgs2, imagens_classe

    for f in objetos:
        filename = os.path.join( "data", "imgs", "objects", f + ".png" )
        imgs[f] = gtk.gdk.pixbuf_new_from_file( filename )

    for f in imagens_classe:
        filename = os.path.join( "data", "imgs", "etc", f + ".png" )
        imgs2[f] = gtk.gdk.pixbuf_new_from_file( filename )


def adicionaObjetos():
    global objetos, storeObjetos, imgs

    for nome in objetos:
        img = imgs[nome]
        storeObjetos.append( [ img, nome ] )


def on_select_obj(*args):
    global listaObjetos, storeObjetos

    path, col = listaObjetos.get_cursor()
    if path == None:
        return

    it = storeObjetos.get_iter( path )
    obj = storeObjetos.get_value( it, 1 )

    fill_membros( obj )
    fill_hierarquia( obj )
    fill_props( obj )
    fill_signals( obj )



def get_class_from_obj(obj):
    if "gtk.gdk." in obj:
        obj_nome = obj[ len("gtk.gdk.") : ]
        modulo = gtk.gdk
    elif "gobject." in obj:
        obj_nome = obj[ len("gobject.") : ]
        modulo = gobject
    elif "gtk." in obj:
        obj_nome = obj[ len("gtk.") : ]
        modulo = gtk
    else:
        return None, ""

    classe = getattr( modulo, obj_nome )
    return classe, obj_nome


def fill_membros(obj):
    global storeMembros, imgs2, textDoc, db
    storeMembros.clear()

    classe, obj_nome = get_class_from_obj( obj )
    if obj_nome == "":
        return

    obj_doc = getattr(classe, "__doc__")
    if obj_doc != None:
        textDoc.get_buffer().set_text( obj_doc )
    else:
        textDoc.get_buffer().set_text( "No documentation.\n" + \
            "The __doc__ attribute for this class is null." )


    # adiciona os construtores
    #
    for d in db[obj]:
        if d == obj:
            dtype = "constructor"

            estrela = imgs2['estrela']
            img = imgs2['method_constructor']

            params = db[obj][d]
            if len(params) > 0:
                d = d + " (" + reduce( lambda x,y: x + ", " + y, params ) + ")"
            else:
                d = d + " ()"

            storeMembros.append( [estrela, img, d, dtype] )



    for d in dir(classe):

        dtype = str( getattr(classe, d) )
        if type( getattr(classe, d) ) == str:
            img = imgs2['string']
            dtype = "[string]"

        if "<class" in dtype:
            img = imgs2['class']
        elif "<deprecated" in dtype:
            img = imgs2['deprecated']
        elif "<attribute" in dtype:
            img = imgs2['attribute']
        elif "<method 'get_" in dtype or "<method 'set_" in dtype or \
             "<method 'is_" in dtype:
            img = imgs2['method_get_set']
        elif "<method" in dtype:
            img = imgs2['method']
        elif "<built-in function" in dtype or \
          "<built-in method" in dtype or \
          "<slot wrapper" in dtype:
            img = imgs2['method_special']
        else:
            img = imgs2['default']

        if d in db[obj]:
            estrela = imgs2['estrela']
            params = db[obj][d]
            if len(params) > 0:
                d = d + " (" + reduce( lambda x,y: x + ", " + y, params ) + ")"
            else:
                d = d + " ()"
        else:
            estrela = None

        storeMembros.append( [estrela, img, d, dtype] )


def fill_hierarquia(obj):
    global db_anc, areaClasses, storeObjetos, listaObjetos

    areaClasses.foreach( lambda btn: areaClasses.remove(btn) )

    def find_obj(sender, anc):

        index = 0
        it = storeObjetos.get_iter_first()
        while it != None:
            classe = storeObjetos.get_value( it, 1 )
            if classe == anc:
                listaObjetos.set_cursor( (index,) )
                return

            it = storeObjetos.iter_next( it )
            index += 1

        print( "Did not find: " + anc)

    for anc in db_anc[obj]:
        hb = gtk.HBox()
        hb.add( gtk.image_new_from_pixbuf( imgs[anc] ) )
        hb.add( gtk.Label(anc) )
        hb.set_spacing( 2 )
        hb.show_all()

        b = gtk.Button()
        b.connect( "clicked", find_obj, anc )
        b.add( hb )
        b.show()

        areaClasses.add( b )


def fill_props(obj):
    global storeProps

    storeProps.clear()
    classe, nome = get_class_from_obj( obj )

    props = gobject.list_properties( classe )
    for prop in props:
        pname = prop.name
        ptipo = prop.value_type.name
        pdefault = str( prop.default_value )
        pdesc = prop.blurb

        if ptipo == 'gint' or ptipo == 'guint':
            img = imgs2['prop_int']
        elif ptipo == 'gboolean':
            img = imgs2['prop_bool']
        elif ptipo == 'gchararray':
            img = imgs2['prop_string']
        elif ptipo == 'gfloat':
            img = imgs2['prop_float']
        elif ptipo == 'GdkColor':
            img = imgs2['prop_color']
        else:
            img = imgs2['prop_default']

        storeProps.append( [img, pname, ptipo, pdefault, pdesc] )


def fill_signals(obj):
    global storeSignals

    storeSignals.clear()
    classe, nome = get_class_from_obj( obj )

    sigs = gobject.signal_list_names( classe )
    for sig in sigs:
        details = gobject.signal_query( sig, classe )
        sig_id = details[0]
        sig_ret = details[4].name

        sig_params = details[5]
        if len(sig_params) > 0:

            sparams = []
            for sig_param in sig_params:
                sparams.append( sig_param.name )

            s_sig_params = ", ".join( sparams )
        else:
            s_sig_params = "<None>"

        img = imgs2['signal_default']
        storeSignals.append( [img, sig, sig_id, sig_ret, s_sig_params] )


def on_janela_destroy(sender, event):
    gtk.main_quit()


def new_coluna(fonte = None, text_src = None, img_src = None, \
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


def sort_func_metodo_estrela(model, iter1, iter2):
    img1 = model.get_value( iter1, 0 )
    img2 = model.get_value( iter2, 0 )

    if img1 == img2:
        return 0
    elif img1 != None:
        return -1
    else:
        return +1


def sort_func_metodo_nome(model, iter1, iter2):
    nome1 = model.get_value( iter1, 0 )
    nome2 = model.get_value( iter2, 0 )

    if nome1 == nome2:
        return 0
    elif nome1 < nome2:
        return -1
    else:
        return +1


def on_classes_expose(widget, event):
    widget = widget.get_child()
    w = widget.get_allocation().width
    h = widget.get_allocation().height

#    gc = event.window.new_gc()
#    gc.set_rgb_fg_color( gtk.gdk.color_parse("#69b8d3") )
#    event.window.draw_rectangle( gc, filled = False, \
#        x=0, y=0, width = w-7, height = h-7 )

    cr = event.window.cairo_create()

    grad = cairo.LinearGradient( 0, h/2, 0, h-1 )
    grad.add_color_stop_rgba( 0.0,   0.3, 0.4, 0.5, 0.0 )
    grad.add_color_stop_rgba( 1.0,   0.1, 0.5, 0.6, 0.5 )

    cr.set_source( grad )
    cr.rectangle( 0, 0, w-1, h-1 )
    cr.fill()

    return False





builder = gtk.Builder()
builder.add_from_file( "PyGtkObjectBrowser.glade" )

janela = builder.get_object( "window" )
listaObjetos = builder.get_object( "listaObjetos" )
storeObjetos = builder.get_object( "storeObjetos")

listaMembros = builder.get_object( "listaMembros" )
storeMembros = builder.get_object( "storeMembros")

listProps = builder.get_object( "listProps" )
storeProps = builder.get_object( "storeProps" )

listSignals = builder.get_object( "listSignals" )
storeSignals = builder.get_object( "storeSignals" )

textDoc = builder.get_object( "textDoc")
areaClasses = builder.get_object( "areaClasses" )

viewClasses = builder.get_object("viewClasses")
viewClasses.connect_after( "expose_event", on_classes_expose )
cl_classes = gtk.gdk.color_parse( "#c8dbe1" )
viewClasses.modify_bg( gtk.STATE_NORMAL, cl_classes )


cl_hint = gtk.gdk.color_parse( "#fdffca" )
textDoc.modify_base( gtk.STATE_NORMAL, cl_hint )
textDoc.modify_font( pango.FontDescription("Tahoma 8") )

janela.connect( "delete-event", on_janela_destroy )
janela.show()

listaObjetos.append_column( new_coluna("9", text_src=1, img_src=0) )
listaObjetos.connect( "cursor-changed", on_select_obj )

storeMembros.set_sort_func( 0, sort_func_metodo_estrela )
storeMembros.set_sort_func( 1, sort_func_metodo_nome )

listaMembros.append_column( new_coluna( img_src=0, sort_id = 0 ) )
listaMembros.append_column( new_coluna( fonte = "Monospace 9", \
    text_src=2, img_src=1, resize=True, title="Name", sort_id = 1 ) )
listaMembros.append_column( new_coluna( fonte = "8", \
    text_src=3, cor_texto="#979797", resize=True, title="Type") )

listProps.append_column( new_coluna("", img_src=0) )
listProps.append_column( new_coluna(title="Name", text_src=1) )
listProps.append_column( new_coluna(title="Type", text_src=2) )
listProps.append_column( new_coluna(title="Default", text_src=3) )
listProps.append_column( new_coluna(title="Desc.", text_src=4) )

listSignals.append_column( new_coluna("", img_src=0) )
listSignals.append_column( new_coluna(title="Name", text_src=1) )
listSignals.append_column( new_coluna(title="ID", text_src=2) )
listSignals.append_column( new_coluna(title="Returns", text_src=3) )
listSignals.append_column( new_coluna(title="Params", text_src=4) )

carregaObjetos()
carregaImagens()
adicionaObjetos()

carregaBancoMetodos()

gtk.main()
