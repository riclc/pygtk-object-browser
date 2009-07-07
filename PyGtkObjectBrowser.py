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
import pango
import inspect
import os
import os.path

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
    'estrela' \
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



def fill_membros(obj):
    global storeMembros, imgs2, textDoc, db
    storeMembros.clear()

    obj_nome = obj

    if "gtk.gdk." in obj_nome:
        obj_nome = obj_nome[ len("gtk.gdk.") : ]
        modulo = gtk.gdk
    elif "gtk." in obj_nome:
        obj_nome = obj_nome[ len("gtk.") : ]
        modulo = gtk
    else:
        return

    classe = getattr( modulo, obj_nome )

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
        b = gtk.Button( anc )
        b.connect( "clicked", find_obj, anc )
        b.show()
        areaClasses.add( b )

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



builder = gtk.Builder()
builder.add_from_file( "PyGtkObjectBrowser.glade" )

janela = builder.get_object( "window" )
listaObjetos = builder.get_object( "listaObjetos" )
storeObjetos = builder.get_object( "storeObjetos")
listaMembros = builder.get_object( "listaMembros" )
storeMembros = builder.get_object( "storeMembros")
textDoc = builder.get_object( "textDoc")
areaClasses = builder.get_object( "areaClasses" )

cl_hint = gtk.gdk.color_parse( "#fdffca" )
textDoc.modify_base( gtk.STATE_NORMAL, cl_hint )
textDoc.modify_font( pango.FontDescription("Tahoma 8") )

janela.connect( "delete-event", on_janela_destroy )
janela.show()

listaObjetos.append_column( new_coluna("9", text_src=1, img_src=0) )
listaObjetos.set_rules_hint( True )
listaObjetos.connect( "cursor-changed", on_select_obj )

storeMembros.set_sort_func( 0, sort_func_metodo_estrela )
storeMembros.set_sort_func( 1, sort_func_metodo_nome )

listaMembros.append_column( new_coluna( img_src=0, sort_id = 0 ) )
listaMembros.append_column( new_coluna( fonte = "Monospace 9", \
    text_src=2, img_src=1, resize=True, title="Name", sort_id = 1 ) )
listaMembros.append_column( new_coluna( fonte = "8", \
    text_src=3, cor_texto="#979797", resize=True, title="Type") )

listaMembros.set_rules_hint( True )

carregaObjetos()
carregaImagens()
adicionaObjetos()

carregaBancoMetodos()

gtk.main()
