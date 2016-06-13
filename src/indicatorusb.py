#!/usr/bin/env python3
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
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('Notify', '0.7')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Gio
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository import Notify
import os
import dbus
from configurator import Configuration
from preferences_dialog import PreferencesDialog
import comun
from comun import _

# YUCK: Gtk.image_new_from_gicon does not work, and pynotify does
# not support gicon, so just let the theme choose the icon


def _get_icon_name_from_gicon(gicon):
    assert type(gicon) == Gio.ThemedIcon
    name = "image-missing"
    theme = Gtk.IconTheme.get_default()
    for n in gicon.get_names():
        if theme.lookup_icon(n, Gtk.IconSize.MENU, 0):
            name = n
            break
    return n


class Main:
    def __init__(self):
        if dbus.SessionBus().request_name('es.atareao.indicator-usb') !=\
                dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
            print("application already running")
            exit(0)
        self.drives = []
        self.menu = None
        self.load_preferences()
        self.notifications = Notify.Notification.new('', '', None)
        self.indicator = AppIndicator.Indicator.new(
            _('Indicator-USB'),
            _('Indicator-USB'),
            AppIndicator.IndicatorCategory.HARDWARE)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_icon('media-removable-symbolic')
        self.monitor = Gio.VolumeMonitor.get()
        self.monitor.connect('mount-added', self._add_drive)
        self.monitor.connect('mount-removed', self._del_drive)
        self.refresh()

    def refresh(self):
        self.drives = []
        for m in self.monitor.get_mounts():
            self._add_drive(None, m)

    def _add_drive(self, s, m):
        if m.can_unmount():
            root = m.get_root()
            if (root.get_uri_scheme() == "file" and self.show_hdd) \
               or (not root.is_native() and self.show_net):
                self.drives.append(m)
        self.update()

    def _del_drive(self, s, d):
        self.drives.remove(d)
        self.update()

    def _eject_cb(self, m, result, t):
        # XXX: pynotify does not support gicon
        n = Notify.Notification.new(_('Device can be removed now'),
                                    m.get_name(),
                                    _get_icon_name_from_gicon(m.get_icon()))
        n.show()

    def eject(self, s, m):
        m.unmount(Gio.MountUnmountFlags.NONE, None, self._eject_cb, None)

    def load_preferences(self):
        configuration = Configuration()
        self.show_hdd = configuration.get('show-hdd')
        self.show_net = configuration.get('show-net')

    def save_config(self):
        configuration = Configuration()
        configuration.set('show-hdd', self.show_hdd)
        configuration.set('show-net', self.show_net)
        configuration.save()
        self.refresh()

    def update(self):
        if len(self.drives) > 0:
            self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
        if self.menu is not None:
            self.menu.destroy()
        self.menu = Gtk.Menu()
        # Header
        hdr = Gtk.MenuItem(label=_('Safely remove devices')+':')
        hdr.show()
        self.menu.append(hdr)
        # Separator
        smi = Gtk.SeparatorMenuItem()
        smi.show()
        self.menu.append(smi)
        for i in self.drives:
            mi = Gtk.ImageMenuItem(label=i.get_name())
            # XXX: gicon does not work...
            mi.set_image(Gtk.Image.new_from_stock(
                _get_icon_name_from_gicon(i.get_icon()), Gtk.IconSize.MENU))
            mi.set_always_show_image(True)
            self.menu.append(mi)
            mi.show()
            mi.connect('activate', self.eject, i)
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        preferences = Gtk.MenuItem(label=_('Preferences'))
        preferences.connect('activate', self.on_preferences_activated)
        preferences.show()
        self.menu.append(preferences)
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        about_item = Gtk.MenuItem(label=_('About...'))
        about_item.show()
        about_item.connect('activate', self.on_about_activate)
        self.menu.append(about_item)
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        quit_item = Gtk.MenuItem(label=_('Exit'))
        quit_item.show()
        quit_item.connect('activate', self.on_exit_activate)
        self.menu.append(quit_item)
        self.indicator.set_menu(self.menu)

    def on_exit_activate(self, widget):
        exit(0)

    def on_preferences_activated(self, widget):
        cm = PreferencesDialog(None)
        if cm.run() == Gtk.ResponseType.ACCEPT:
            cm.save_preferences()
            self.update()
        cm.hide()
        cm.destroy()

    def on_about_activate(self, widget):
        widget.set_sensitive(False)
        ad = Gtk.AboutDialog()
        ad.set_name(comun.APPNAME)
        ad.set_version(comun.VERSION)
        ad.set_copyright('''
Copyrignt (c) 2010-2016

Pedro Fragoso <ember@pfragoso.org>
Calum Lind <https://github.com/cas-->
Anton Eliasson <devel@antoneliasson.se>
Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
''')
        ad.set_comments(_('Cool flash drive unmounter for Ubuntu'))
        ad.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Pedro Fragoso <ember@pfragoso.org>',
            'Calum Lind <https://github.com/cas-->',
            'Anton Eliasson <devel@antoneliasson.se>',
            'Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_translator_credits('''
Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>\n\
''')
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_program_name(comun.APPNAME)
        ad.run()
        ad.destroy()
        widget.set_sensitive(True)

    def on_option(self, x, o):
        if o == 'hdd':
            self.monitor.show_hdd = x.get_active()
        if o == 'net':
            self.monitor.show_net = x.get_active()
        self.save_config()


def main():
    Notify.init('indicator-usb')
    m = Main()
    Gtk.main()

if __name__ == '__main__':
    main()
