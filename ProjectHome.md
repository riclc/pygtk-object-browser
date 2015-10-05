# PyGtk Object Browser #
Copyright (c) 2009, Ricardo Lenz

## Description ##

Browse and inspect gtk and gdk objects.

This is just a very small application to help PyGTK programmers out there. But it can be improved in a number of ways!


## Current stable version ##

The current stable version is 0.9.9.


## Installation ##

There is no need to install anything. Just run the "PyGtkObjectBrowser.py" file.
But please make sure that the "data" folder is in the same folder where the python files are! (But it should be there already.)


## Screenshots ##

These are screenshots for the 0.9.9 version (which is the current version):

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_001.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_001.png)

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_002.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_002.png)

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_003.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_003.png)

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_004.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_004.png)

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_005.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/0.9.9/screenshot_005.png)



## Component Images ##

All these images are either from Glade or done by myself. Just email me if you want to know which is which :)
For example, Glade does not have GDK icons, so I have made them by myself:

![http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/some_icons.png](http://pygtk-object-browser.googlecode.com/svn/trunk/screenshots/some_icons.png)

Anyway, I would like to know if you use some of the images I have made. Just send me an email and I will be happy :P



## Changelog for version 0.9.9 ##

```
Here is what has been changed since the last (0.9.8) version:

* Now it can show all objects that are interfaces in italic.

* Lists all interfaces that an object implements (this is done using GObject).

* Now, it also uses GObject for the ancestry-listing (instead of the internal database)

* Has a new "options tab", which uses GConf and watch for changes in real time :)

* Adds a nice logo bar, drawn in cairo, like the other bars.

* Refactoring of the code. Now, the application is split in several files.

* The following objects are now in the database too: gtk.CellLayout, gtk.Editable,
gtk.MenuShell, gtk.CellEditable, atk.Implementor, gtk.Buildable, gtk.Activatable,
gtk.Orientable, gtk.ImageMenuItem, gtk.TreeDragDest, gtk.TreeDragSource.

* The following existing object images have been modified for this version:
gobject.GObject, gtk.Action, gtk.CellRenderer, gtk.CellRendererProgress, gtk.Container,
gtk.Item, gtk.Menu, gtk.MenuBar, gtk.MenuItem, gtk.ProgressBar, gtk.Statusbar,
gtk.ToolButton, gtk.ToolItem, gtk.Toolbar, gtk.TreeModel.

* Added images for the following objects: gtk.TreeSortable, gtk.TreeDragSource,
gtk.TreeDragDest, gtk.ToolShell, gtk.Separator, gtk.Scrollbar, gtk.Scale, gtk.Range,
gtk.Progress, gtk.Paned, gtk.Orientable, gtk.MenuShell, gtk.ImageMenuItem, gtk.Editable,
gtk.CellLayout, gtk.CellEditable, gtk.Buildable, gtk.Box, gtk.Activatable,
gtk.ActionGroup, atk.Implementor.

* Fixed some minor bugs
```