from mock_kodi import MOCK
import os
import threading
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
from mock_kodi import makedirs
import runpy
from urllib.parse import urlparse
import sys
import doctest
import time


def execute_callback():
    runpy.run_module('foobar', run_name='__main__')

def start_service():
    from resources.lib import refresh
    _monitor = refresh.RefreshService()
    _monitor.waitForAbort()

def teardown():
    import shutil
    shutil.rmtree(MOCK.PROFILE_ROOT)

def setup():
    import tempfile
    MOCK.PROFILE_ROOT = tempfile.mkdtemp()

    _addon = xbmcaddon.Addon()

            # <item library="context_add.py">
            #     <label>$ADDON[plugin.program.autowidget 32003]</label>
            #     <visible>String.IsEqual(Window(10000).Property(context.autowidget),true)</visible>
            # </item>
    MOCK.DIRECTORY.register_contextmenu(
        _addon.getLocalizedString(32003),
        "plugin.program.autowidget",
        "context_add", 
        lambda : True
    )

            # <item library="context_refresh.py">
            #     <label>$ADDON[plugin.program.autowidget 32006]</label>
            #     <visible>String.Contains(ListItem.FolderPath, plugin://plugin.program.autowidget)</visible>
            # </item>
    MOCK.DIRECTORY.register_contextmenu(
        _addon.getLocalizedString(32006),
        "plugin.program.autowidget",
        "context_refresh", 
        lambda : True
    )

    MOCK.DIRECTORY.register_action("plugin://plugin.program.autowidget", "main")

    def home(path):
        xbmcplugin.addDirectoryItem(
            handle=1, 
            url="plugin://plugin.program.autowidget/", 
            listitem=xbmcgui.ListItem("AutoWidget"),  
            isFolder=True
        )
        # add our fake plugin    
        xbmcplugin.addDirectoryItem(
            handle=1, 
            url="plugin://dummy/", 
            listitem=xbmcgui.ListItem("Dummy"),
            isFolder=True
        )
        xbmcplugin.endOfDirectory(handle=1)
    MOCK.DIRECTORY.register_action("", home)

    def dummy_folder(path):
        for i in range(1,20):
            p = "plugin://dummy/item{}".format(i)
            xbmcplugin.addDirectoryItem(
                handle=1, 
                url=p, 
                listitem=xbmcgui.ListItem("Dummy Item {}".format(i), path=p),
                isFolder=False
            )
        xbmcplugin.endOfDirectory(handle=1)
    MOCK.DIRECTORY.register_action("plugin://dummy", dummy_folder)

def press(keys):
    MOCK.INPUT_QUEUE.put(keys)
    MOCK.INPUT_QUEUE.join() # wait until the action got processed (ie until we wait for more input)

def start_kodi(service=True):
    threading.Thread(target=MOCK.DIRECTORY.handle_directory, daemon = True).start()
    time.sleep(0.1) # give the home menu enough time to output
    if service:
        service = threading.Thread(target=start_service, daemon = True).start()
        time.sleep(1) # give the home menu enough time to output


def test_add_widget_group():
    """
    >>> start_kodi(service=False)
    -------------------------------
    -1) Back
     0) Home
    -------------------------------
     1) AutoWidget
     2) Dummy
    -------------------------------
    Enter Action Number

    >>> press("c2")
     1) Add to AutoWidget Group

    >>> press("Add to AutoWidget Group")
    Add as
    0) Shortcut
    1) Widget
    2) Clone as Shortcut Group
    3) Explode as Widget Group

    >>> press("Widget")
    Widget
    Choose a Group
    0) Create New Widget Group

    >>> press("Create New Widget Group")
    Create New Widget Group
    Name for Group

    >>> press("Widget1")
    Choose a Group
    0) Create New Widget Group
    1) Widget1

    >>> press("Widget1")
    Widget1
    Widget Label

    >>> press("My Label")
    -------------------------------
    -1) Back
     0) Home
    -------------------------------
     1) AutoWidget
     2) Dummy
    -------------------------------
    Enter Action Number

    >>> press("AutoWidget")
    -------------------------------
    -1) Back
     0) Home
    -------------------------------
     1) My Groups
     2) Active Widgets
     3) Tools
    -------------------------------

    >>> press("My Groups")
    -------------------------------
    -1) Back
     0) Home
    -------------------------------
     1) Widget1
    -------------------------------
    Enter Action Number

    >>> press("Widget1")
    -------------------------------
    -1) Back
     0) Home
    -------------------------------
     1) My Label
     2) Widget1 (Static)
     3) Widget1 (Cycling)
     4) Widget1 (Merged)
    -------------------------------
    Enter Action Number

    >>> press("Widget1 (Cycling)")
    Choose an Action
    0) Random Path
    1) Next Path   

    >>> press("Next Path") 
    """

if __name__ == '__main__':
    os.environ['SEREN_INTERACTIVE_MODE'] = 'True'
    setup()
    doctest.testmod()
    teardown()
