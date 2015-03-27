import sys
import urllib
import urllib2
import urlparse
import xbmcgui
import xbmc
import xbmcplugin
import xbmcaddon
import string

import json

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')
name = None
mode = args.get('mode', None)

api_root = 'https://api.blitzr.com'

api_key = xbmcplugin.getSetting(addon_handle, 'api_key')

def blitzr_get(path, params={}):
    params['key'] = api_key
    url = api_root + path + '?' + urllib.urlencode(params)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    content = response.read()
    response.close()
    return json.loads(content)

def search(search_type, query):
    for entity in blitzr_get('/search/' + search_type + '/', {'query' : query}):
        buildMenu(
            mode=search_type.title(),
            foldername=entity['uuid'],
            description=entity['name'],
            icon=entity['thumb'],
            thumbnail=entity['image']
        );

def search_track(query):
    for entity in blitzr_get('/search/track/', {'query' : query}):
        buildMenu(
            mode='Release',
            foldername=entity['release']['uuid'],
            description=entity['title'] + ' on ' + entity['release']['name'],
            icon=entity['release']['thumb'], 
            thumbnail=entity['release']['image']
        );

def topArtists():
    for artist in blitzr_get('/top/50/'):
        buildMenu(
            mode="Artist", 
            foldername=artist['uuid'], 
            description=artist['name'], 
            icon=artist['thumb'], 
            thumbnail=artist['image']
        );

def listReleases(artist_uuid):
    for release in blitzr_get('/artist/releases/', {'uuid': artist_uuid, 'type' : 'official'}):
        buildMenu(
            mode="Release", 
            foldername=release['uuid'], 
            description=release['name'], 
            icon=release['thumb'], 
            thumbnail=release['image']
        );

def listTracks(release_uuid):
    release = blitzr_get('/release/', {'uuid': release_uuid})
    for track in release['tracklist']:
        if 'uuid' in track:
            buildMenu(
                mode        = "Track", 
                foldername  = track['uuid'],
                description = track['title'], 
                icon        = release['thumb'], 
                thumbnail   = release['image']
            );

def playTrack(track_uuid):
    for source in blitzr_get('/track/sources/', {'uuid': track_uuid}):
        if source['source'] == 'youtube':
            xbmc.Player().play('plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=' + source['id'])
            return

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def buildMenu(mode, foldername, description, icon, thumbnail):
    url = build_url({'mode': mode, 'foldername': foldername})
    li = xbmcgui.ListItem(description, iconImage=icon, thumbnailImage=thumbnail)
    li.setProperty('fanart_image', thumbnail)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

if mode is None:
    buildMenu(mode="search_menu", foldername="Search", description="Search", icon="icon.png", thumbnail="thumbnail.png");
    buildMenu(mode="top_artist", foldername="Top Artists", description="Top Artists", icon="icon.png", thumbnail="thumbnail.png");
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'Artist':
    foldername = args['foldername'][0]
    listReleases(urllib.quote_plus(foldername))
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'Release':
    foldername = args['foldername'][0]
    listTracks(urllib.quote_plus(foldername))
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'Track':
    foldername = args['foldername'][0]
    playTrack(urllib.quote_plus(foldername))

elif mode[0] == 'search':
    # Search videos
    search_type = args['foldername'][0]
    keyboard = xbmc.Keyboard('', "name", False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if len(query) > 0:
            if search_type == 'track':
                search_track(urllib.quote_plus(query))
            else:    
                search(search_type, urllib.quote_plus(query))
            xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'search_menu':
    # Display Search menu
    foldername = args['foldername'][0]
    buildMenu(mode="search", foldername="artist", description="Search Artist", icon="icon.png", thumbnail="thumbnail.png");
    buildMenu(mode="search", foldername="release", description="Search Album", icon="icon.png", thumbnail="thumbnail.png");
    buildMenu(mode="search", foldername="track", description="Search Song", icon="icon.png", thumbnail="thumbnail.png");
    buildMenu(mode="search", foldername="label", description="Search Label", icon="icon.png", thumbnail="thumbnail.png");
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'top_artist':
    # Display top artist
    foldername = args['foldername'][0]
    topArtists()
    xbmcplugin.endOfDirectory(addon_handle)
