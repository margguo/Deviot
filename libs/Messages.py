#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import threading
import sublime
import time
import queue

from .I18n import I18n


_ = I18n().translate


class MessageQueue(object):
    """
    Print messages in the user console,
    placed in the message queue
    """

    def __init__(self, console=None):
        self.queue = queue.Queue(0)
        self.is_alive = False
        self.console = console

    def put(self, text, *args):
        text = _(text, *args)
        if '\\n' in text:
            text = text.replace('\\n', '\n')
        self.queue.put(text)

    def startPrint(self, one_time=False):
        if not self.is_alive:
            self.is_alive = True
            thread = threading.Thread(
                target=lambda: self.printScreen(one_time))
            thread.start()

    def printScreen(self, one_time=False):
        if one_time:
            self.printOnce()
        else:
            while self.is_alive:
                self.printOnce()
                time.sleep(0.01)

    def printOnce(self):
        while not self.queue.empty():
            text = self.queue.get()
            if self.console:
                self.console.printScreen(text)
            else:
                print(text)
            time.sleep(0.01)

    def stopPrint(self):
        while(not self.queue.empty()):
            time.sleep(2)
        self.is_alive = False


class Console:
    """
    Creates the user console to show different messages.
    """

    def __init__(self, window=False):
        self.window = window
        if(not window):
            self.window = sublime.active_window()
        self.panel = self.window.create_output_panel('exec')
        self.panel.set_syntax_file("Packages/Deviot/Arduino.tmLanguage")
        self.panel.set_name('exec')

    def printScreen(self, text):
        sublime.set_timeout(lambda: self.println(text), 0)

    def println(self, text):
        if(len(text)):
            self.window.run_command("show_panel", {"panel": "output.exec"})
            self.panel.set_read_only(False)
            self.panel.run_command("append", {"characters": text})
            self.panel.run_command("move_to", {"extend": False, "to": "eof"})
            self.panel.set_read_only(True)


class MonitorView:
    """
    Show the serial monitor messages from and to a device
    """

    def __init__(self, window, serial_port):
        self.name = 'Serial Monitor - ' + serial_port
        self.window, self.view = findInOpendView(self.name)
        if self.view is None:
            self.window = window
            self.view = self.window.new_file()
            self.view.set_name(self.name)
        self.view.run_command('toggle_setting', {'setting': 'word_wrap'})
        self.view.set_scratch(True)
        self.window.focus_view(self.view)

    def printScreen(self, text):
        sublime.set_timeout(lambda: self.println(text), 0)

    def println(self, text):
        try:
            from .Preferences import Preferences
        except:
            from libs.Preferences import Preferences

        # Preferences to auto-scroll
        auto_scroll = Preferences().get('auto_scroll', True)

        self.view.set_read_only(False)
        self.view.run_command("append", {"characters": text})
        if(auto_scroll):
            self.view.run_command("move_to", {"extend": False, "to": "eof"})
        self.view.set_read_only(True)


def findInOpendView(view_name):
    """
    Search a specific view in the list of available views

    Arguments:
        view_name {string}
            Name of the view to search
    """
    opened_view = None
    found = False
    windows = sublime.windows()
    for window in windows:
        views = window.views()
        for view in views:
            name = view.name()
            if name == view_name:
                opened_view = view
                found = True
                break
        if found:
            break
    return (window, opened_view)


def isMonitorView(view):
    """
    Check if the view passed is Serial monitor 'type'

    Arguments:
        view {object}
            current view

    Returns:
        [Bool] -- True or false if the view is Serial monitor 'type'
    """
    state = False
    name = view.name()
    if name and 'Serial Monitor - ' in name:
        state = True
    return state
