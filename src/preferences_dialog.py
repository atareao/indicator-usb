#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of indicator-usb
#
# Copyright (C) 2016 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import comun
import os
import shutil
import comun
from comun import _
from configurator import Configuration


class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        #
        Gtk.Dialog.__init__(self,
                            'Indicator-USB | '+_('Preferences'),
                            parent,
                            Gtk.DialogFlags.MODAL |
                            Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_from_file(comun.ICON)
        #
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        # ***************************************************************
        notebook = Gtk.Notebook.new()
        vbox0.add(notebook)
        # ***************************************************************
        vbox11 = Gtk.VBox(spacing=5)
        vbox11.set_border_width(5)
        notebook.append_page(vbox11, Gtk.Label.new(_('General')))
        frame11 = Gtk.Frame()
        vbox11.pack_start(frame11, False, True, 1)
        table11 = Gtk.Table(2, 3, False)
        frame11.add(table11)
        # ***************************************************************
        label11 = Gtk.Label(_('Show disks')+':')
        label11.set_alignment(0, 0.5)
        table11.attach(label11, 0, 1, 0, 1, xpadding=5, ypadding=5)
        self.autostart = Gtk.Switch()
        table11.attach(self.autostart, 1, 2, 0, 1,
                       xpadding=5,
                       ypadding=5,
                       xoptions=Gtk.AttachOptions.SHRINK)
        label12 = Gtk.Label(_('Show disks')+':')
        label12.set_alignment(0, 0.5)
        table11.attach(label12, 0, 1, 1, 2, xpadding=5, ypadding=5)
        self.show_disks = Gtk.Switch()
        table11.attach(self.show_disks, 1, 2, 1, 2,
                       xpadding=5,
                       ypadding=5,
                       xoptions=Gtk.AttachOptions.SHRINK)
        label14 = Gtk.Label(_('Show network folders')+':')
        label14.set_alignment(0, 0.5)
        table11.attach(label14, 0, 1, 2, 3, xpadding=5, ypadding=5)
        self.show_net = Gtk.Switch()
        table11.attach(self.show_net, 1, 2, 2, 3,
                       xpadding=5,
                       ypadding=5,
                       xoptions=Gtk.AttachOptions.SHRINK)
        self.load_preferences()
        self.show_all()

    def load_preferences(self):
        configuration = Configuration()
        self.show_disks.set_active(configuration.get('show-hdd'))
        self.show_net.set_active(configuration.get('show-net'))
        filestart = os.path.join(
            os.getenv("HOME"),
            ".config/autostart/indicator-usb-autostart.desktop")
        self.autostart.set_active(os.path.exists(filestart))

    def save_preferences(self):
        configuration = Configuration()
        configuration.set('show-hdd', self.show_disks.get_active())
        configuration.set('show-net', self.show_net.get_active())
        configuration.save()
        filestart = os.path.join(
            os.getenv("HOME"),
            ".config/autostart/indicator-usb-autostart.desktop")
        if self.autostart.get_active():
            if not os.path.exists(os.path.dirname(filestart)):
                os.makedirs(os.path.dirname(filestart))
            shutil.copyfile(comun.AUTOSTART, filestart)
        else:
            if os.path.exists(filestart):
                os.remove(filestart)

if __name__ == "__main__":
    cm = PreferencesDialog(None)
    if cm.run() == Gtk.ResponseType.ACCEPT:
        print(1)
    cm.hide()
    cm.destroy()
    exit(0)
