# -*- coding: utf-8 -*-
#
# Advanced Utilities for Kodi
#

# Copyright (c) 2017 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
# Division operator: https://www.python.org/dev/peps/pep-0238/
from __future__ import unicode_literals
from __future__ import division
import datetime
import pprint
import json
# import sys, os, shutil, fnmatch, string, time, traceback, pprint
# import re, urllib, urllib2, urlparse, socket, exceptions, hashlib

# --- Kodi stuff ---
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# --- Modules/packages in this plugin ---
from utils import *
from utils_kodi import *

# --- Addon object (used to access settings) ---
__addon_obj__     = xbmcaddon.Addon()
__addon_id__      = __addon_obj__.getAddonInfo('id').decode('utf-8')
__addon_name__    = __addon_obj__.getAddonInfo('name').decode('utf-8')
__addon_version__ = __addon_obj__.getAddonInfo('version').decode('utf-8')
__addon_author__  = __addon_obj__.getAddonInfo('author').decode('utf-8')
__addon_profile__ = __addon_obj__.getAddonInfo('profile').decode('utf-8')
__addon_type__    = __addon_obj__.getAddonInfo('type').decode('utf-8')

# --- Modules/packages in this plugin ---
# Addon module dependencies:
# main <-- utils, utils_kodi
from utils import *

# --- Addon paths and constant definition ---
# _FILE_PATH is a filename
# _DIR is a directory (with trailing /)
ADDONS_DATA_DIR         = FileName('special://profile/addon_data')
PLUGIN_DATA_DIR         = ADDONS_DATA_DIR.pjoin(__addon_id__)
BASE_DIR                = FileName('special://profile')
HOME_DIR                = FileName('special://home')
KODI_FAV_FILE_PATH      = FileName('special://profile/favourites.xml')
ADDONS_DIR              = HOME_DIR.pjoin('addons')
CURRENT_ADDON_DIR       = ADDONS_DIR.pjoin(__addon_id__)

# --- Plugin database indices ---
class Addon_Paths:
    def __init__(self):
        self.LAUNCH_LOG_FILE_PATH    = PLUGIN_DATA_DIR.pjoin('launcher.log')

# --- Global variables ---
PATHS = Addon_Paths()
g_settings = {}
g_base_url = ''
g_addon_handle = 0
g_content_type = ''
g_time_str = unicode(datetime.datetime.now())

# --- Main code -----------------------------------------------------------------------------------
#
# This is the plugin entry point.
#
def run_plugin(addon_argv):
    global g_base_url
    global g_addon_handle
    global g_content_type

    # --- Initialise log system ---
    # >> Force DEBUG log level for development.
    # >> Place it before setting loading so settings can be dumped during debugging.
    # set_log_level(LOG_DEBUG)

    # --- Fill in settings dictionary using __addon_obj__.getSetting() ---
    m_get_settings()
    set_log_level(g_settings['log_level'])

    # --- Some debug stuff for development ---
    log_debug('---------- Called AU run_plugin() constructor ----------')
    log_debug('sys.platform {0}'.format(sys.platform))
    log_debug('Python version ' + sys.version.replace('\n', ''))
    log_debug('__addon_id__      {0}'.format(__addon_id__))
    log_debug('__addon_version__ {0}'.format(__addon_version__))
    for i in range(len(addon_argv)): log_debug('sys.argv[{0}] = "{1}"'.format(i, addon_argv[i]))
    # >> Timestamp to see if this submodule is reinterpreted or not.
    log_debug('main submodule exec timestamp {0}'.format(g_time_str))

    # --- Addon data paths creation ---
    if not PLUGIN_DATA_DIR.exists(): PLUGIN_DATA_DIR.makedirs()

    # --- Process URL ---
    g_base_url = addon_argv[0]
    g_addon_handle = int(addon_argv[1])
    args = urlparse.parse_qs(addon_argv[2][1:])
    # log_debug('args = {0}'.format(args))
    # Interestingly, if plugin is called as type executable then args is empty.
    # However, if plugin is called as type video then Kodi adds the following
    # even for the first call: 'content_type': ['video']
    g_content_type = args['content_type'] if 'content_type' in args else None
    log_debug('content_type = {0}'.format(g_content_type))

    # --- If no com parameter display addon root directory ---
    args_size = len(args)
    if 'command' not in args:
        m_command_render_root_menu()
        log_debug('Advanced Utilities exit (addon root)')
        return

    # --- Process command ---------------------------------------------------------------------
    command = args['command'][0]
    if command == 'BROWSE_JSON':
        m_command_browse_json_root(args['dir'][0])
    else:
        kodi_dialog_OK('Unknown command {0}'.format(command))

    log_debug('Advanced DOOM Launcher exit')

#
# Get Addon Settings
#
def m_get_settings():
    # >> Modify global PATHS object instance
    global PATHS
    global g_settings
    o = __addon_obj__

    # --- Advanced tab ---
    g_settings['log_level'] = int(o.getSetting('log_level'))

    # --- Dump settings for DEBUG ---
    # log_debug('Settings dump BEGIN')
    # for key in sorted(self.settings):
    #     log_debug('{0} --> {1:10s} {2}'.format(key.rjust(21), str(self.settings[key]), type(self.settings[key])))
    # log_debug('Settings dump END')

# ---------------------------------------------------------------------------------------------
# Root menu rendering
# ---------------------------------------------------------------------------------------------
def m_command_render_root_menu():
    m_set_Kodi_all_sorting_methods()

    # --- Filesystem browser ---
    m_command_render_root_menu_row('[Browse JSON-RPC API]', m_misc_url_2_arg('command', 'BROWSE_JSON', 'dir', '/'))
    xbmcplugin.endOfDirectory(handle = g_addon_handle, succeeded = True, cacheToDisc = False)

def m_command_render_root_menu_row(root_name, root_URL):
    # --- Create listitem row ---
    icon = 'DefaultFolder.png'
    ICON_OVERLAY = 6
    listitem = xbmcgui.ListItem(root_name, iconImage = icon)

    # listitem.setProperty('fanart_image', category_dic['fanart'])
    listitem.setInfo('video', {'title' : root_name, 'overlay' : ICON_OVERLAY } )

    # --- Create context menu ---
    commands = []
    commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
    commands.append(('AU addon Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
    listitem.addContextMenuItems(commands)

    # --- Add row ---
    xbmcplugin.addDirectoryItem(handle = g_addon_handle, url = root_URL, listitem = listitem, isFolder = True)

def m_command_browse_json_root(dir):
    m_set_Kodi_all_sorting_methods()

    # --- Test JSON-RPC API ---
    c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
             ' "method" : "Application.GetProperties",'
             ' "params" : {"properties" : ["name", "version"]}'
             '}')
    response_props = xbmc.executeJSONRPC(c_str)
    log_debug('JSON      ''{0}'''.format(c_str))
    log_debug('Response  ''{0}'''.format(response_props))

    # --- Call JSONRPC.Introspect() ---
    c_str = ('{"id" : 1, "jsonrpc" : "2.0",'
             ' "method" : "JSONRPC.Introspect",'
             ' "params" : {}'
             '}')
    response_props = xbmc.executeJSONRPC(c_str)
    # log_debug('JSON      ''{0}'''.format(c_str))
    # log_debug('Response  ''{0}'''.format(response_props))

    ret_dic = json.loads(response_props)
    ret_id = ret_dic['id']
    ret_jsonrpc = ret_dic['jsonrpc']
    ret_result = ret_dic['result']
    methods_dic = ret_result['methods']

    # log_debug(pprint.pformat(ret_dic))
    # log_debug(pprint.pformat(methods_dic))

    # --- Extract all addon methods ---
    for method_name in methods_dic.keys():
        m_command_render_root_menu_row(method_name, m_misc_url_2_arg('command', 'BROWSE_JSON', 'dir', method_name))

    # --- Render JSON-RPC API root menu ---
    xbmcplugin.endOfDirectory(handle = g_addon_handle, succeeded = True, cacheToDisc = False)

# ---------------------------------------------------------------------------------------------
# Misc functions
# ---------------------------------------------------------------------------------------------
# List of sorting methods here http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcplugin.html#-setSetting
def m_set_Kodi_all_sorting_methods():
    if g_addon_handle < 0: return
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

def m_set_Kodi_all_sorting_methods_and_size():
    if g_addon_handle < 0: return
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_SIZE)
    xbmcplugin.addSortMethod(handle=g_addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

# ---------------------------------------------------------------------------------------------
# Misc URL building functions
# ---------------------------------------------------------------------------------------------
#
# Used in xbmcplugin.addDirectoryItem()
#
def m_misc_url_1_arg(arg_name, arg_value):
    arg_value_escaped = arg_value.replace('&', '%26')

    return '{0}?{1}={2}'.format(g_base_url, arg_name, arg_value_escaped)

def m_misc_url_2_arg(arg_name_1, arg_value_1, arg_name_2, arg_value_2):
    # >> Escape '&' in URLs
    arg_value_1_escaped = arg_value_1.replace('&', '%26')
    arg_value_2_escaped = arg_value_2.replace('&', '%26')

    return '{0}?{1}={2}&{3}={4}'.format(g_base_url, 
                                        arg_name_1, arg_value_1_escaped,
                                        arg_name_2, arg_value_2_escaped)

def m_misc_url_3_arg(arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                     arg_name_3, arg_value_3):
    arg_value_1_escaped = arg_value_1.replace('&', '%26')
    arg_value_2_escaped = arg_value_2.replace('&', '%26')
    arg_value_3_escaped = arg_value_3.replace('&', '%26')

    return '{0}?{1}={2}&{3}={4}&{5}={6}'.format(g_base_url,
                                                arg_name_1, arg_value_1_escaped,
                                                arg_name_2, arg_value_2_escaped,
                                                arg_name_3, arg_value_3_escaped)

def m_misc_url_4_arg(arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                     arg_name_3, arg_value_3, arg_name_4, arg_value_4):
    arg_value_1_escaped = arg_value_1.replace('&', '%26')
    arg_value_2_escaped = arg_value_2.replace('&', '%26')
    arg_value_3_escaped = arg_value_3.replace('&', '%26')
    arg_value_4_escaped = arg_value_4.replace('&', '%26')

    return '{0}?{1}={2}&{3}={4}&{5}={6}&{7}={8}'.format(g_base_url,
                                                        arg_name_1, arg_value_1_escaped,
                                                        arg_name_2, arg_value_2_escaped,
                                                        arg_name_3, arg_value_3_escaped,
                                                        arg_name_4, arg_value_4_escaped)

#
# Used in context menus
#
def m_misc_url_1_arg_RunPlugin(arg_name_1, arg_value_1):
    return 'XBMC.RunPlugin({0}?{1}={2})'.format(g_base_url, 
                                                arg_name_1, arg_value_1)

def m_misc_url_2_arg_RunPlugin(arg_name_1, arg_value_1, arg_name_2, arg_value_2):
    return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4})'.format(g_base_url,
                                                        arg_name_1, arg_value_1,
                                                        arg_name_2, arg_value_2)

def m_misc_url_3_arg_RunPlugin(arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                               arg_name_3, arg_value_3):
    return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4}&{5}={6})'.format(g_base_url,
                                                                arg_name_1, arg_value_1,
                                                                arg_name_2, arg_value_2,
                                                                arg_name_3, arg_value_3)

def m_misc_url_4_arg_RunPlugin(arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                               arg_name_3, arg_value_3, arg_name_4, arg_value_4):
    return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4}&{5}={6}&{7}={8})'.format(g_base_url,
                                                                        arg_name_1, arg_value_1,
                                                                        arg_name_2, arg_value_2,
                                                                        arg_name_3, arg_value_3, 
                                                                        arg_name_4, arg_value_4)
