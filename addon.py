#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2018
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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, sys, time, unicodedata, random, string, base64, requests, io, datetime, cgi
from bs4 import BeautifulSoup
from zipfile import ZipFile
from xbmcgui import ListItem

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])

reload(sys)  
sys.setdefaultencoding('utf8')

addon_id = 'plugin.video.anitube-master'
self_addon = xbmcaddon.Addon(id = addon_id)
addon_folder = self_addon.getAddonInfo('path')
icons_folder = addon_folder + '/resources/media/icons/'
fanart = addon_folder + '/resources/fanart.jpg'
ad_here = addon_folder + '/resources/pub.jpg'
base_url = 'aHR0cHM6Ly93d3cuZHJlYW1hbmltZXMuY29tLmJy'

# Modes
genres_mode = 1
list_episodes_mode = 2
resolve_episode_mode = 3
list_alphabet_mode = 5
recent_episodes_mode = 6
list_animes_mode = 8
random_anime_mode = 9
from_episode_to_anime_mode = 10

# Estuary skin
list_view = 'Container.SetViewMode(0)'
poster_view = 'Container.SetViewMode(51)'
shift_view = 'Container.SetViewMode(53)'
info_wall_view = 'Container.SetViewMode(54)'
wide_list_view = 'Container.SetViewMode(55)'
wall_view = 'Container.SetViewMode(500)'
fanart_view = 'Container.SetViewMode(502)'

def main_menu():
  check_version()
  xbmcgui.Dialog().textviewer('AniTube', 'Publicite Aqui!')
  
  add_dir('Recentes',   get_base_url(),                     recent_episodes_mode, icons_folder + 'new.png')
  add_dir('Lista',      get_base_url() + '/lista-completa', list_alphabet_mode,   icons_folder + 'sort.png', total_items = 27)
  add_dir('Categorias', get_base_url() + '/lista-completa', genres_mode,          icons_folder + 'genres.png')
  #add_dir('Aleatório',   get_base_url(), random_anime_mode, icons_folder + 'random.png')
  
  xbmcplugin.setContent(__handle__,'tvshows')
  xbmc.executebuiltin(shift_view)

def list_genres(url):  
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  #xbmc.log('\n[VC_DEBUG] soup: ' + soup).renderContents()
    
  genres = soup.find(id = 'lista-filtros').find('ul').findAll('input')
  
  for genre in genres:
    genre_name = genre['value'].encode(encoding = 'UTF-8', errors = 'strict')
    anime_list_url = url + '/1?generos%5B%5D=' + urllib.quote(genre_name)
    
    add_dir(genre_name, anime_list_url, list_animes_mode, ad_here, True, 1, 'Lista de animes na categoria de ' + genre_name + '.')

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)
  
def list_alphabet(url):
  partial_url = url + '/1?letra='
  partial_description = 'Lista de animes iniciados por {0}.'

  add_dir('#', partial_url + 'Especial', list_animes_mode, ad_here, True, 1, partial_description.format('#'))
  
  for c in string.ascii_uppercase:
    add_dir(c, partial_url + c, list_animes_mode, ad_here, True, 1, partial_description.format(c))
  
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_animes(url):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  animes = soup.find(id = 'animeResult').findAll('article')
    
  for anime in animes:
    title = anime.find('h1', {'class': 'bottom-div'}).text
    
    number_of_eps = re.compile('<b>Epis.dios</b>: (\d+)').findall(anime.renderContents())[0]
    
    #if int(number_of_eps) = 0: continue
    
    if 'Dublado' in title: 
      continue
    else:      
      #xbmc.log('\n[VC_DEBUG] soup: ' + anime.renderContents())
      translation_type = re.compile('<b>Tipo</b>: (.+)<br/>').findall(anime.renderContents())[0]
      
      if 'Legendado' not in translation_type: 
        continue
      
    title = re.sub('Legendado$', '', title)
    
    anime_url = get_base_url() + anime.div.a['href']
    img = anime.div.a.img['src']
        
    add_dir(title, anime_url, list_episodes_mode, img)
    
  add_paging(soup, url, list_animes_mode)

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_episodes(url, view, mode):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  if mode == recent_episodes_mode:
    episodes = soup.find_all('article', { 'class' : 'col-3' })
    
    for x in range(16):
      duration = episodes[x].find(itemprop = 'duration').text.split(':')[0]
      if duration == '00': continue
      
      title_full = episodes[x].h4.text
      
      tvshowtitle = re.compile('(.*) - Epis.dio \d+').findall(title_full)[0]
      if '...' in tvshowtitle: tvshowtitle = re.sub('\.\.\.', '', tvshowtitle).strip() + '…'
      else: tvshowtitle = tvshowtitle.strip()
      
      episode_number = re.compile('Epis.dio (\d+)').findall(title_full)[0]
      
      title = '[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle
      
      episode_url = get_base_url() + episodes[x].a['href']
      img = episodes[x].a.img['src']
      
      add_dir(title, episode_url, resolve_episode_mode, img, True, 1, title, is_episode = True)
  elif mode == list_episodes_mode:
    #xbmc.log('\n[VC_DEBUG] ' + soup.head.title.text)
    eps_ul = soup.find_all('ul', { 'id' : 'lcp_instance_0' })[0]
    episodes = eps_ul.find_all('a')
    
    img = soup.find('div', { 'id' : 'capaAnime' }).img['src']
    
    for episode in episodes:
      title = episode.text
      episode_url = episode['href']
      
      add_dir(title, episode_url, resolve_episode_mode, img, True, 1, title, is_episode = True)
      
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(view) 
    
def random_anime():
  animes_url = base_url + '/anime/letra/' + random.choice(string.ascii_uppercase)
  
  html_code = open_url(animes_url)
  
  anime_elements = re.compile('<a href="(.+?)" class="list-group-item"><span class="badge">(.+?)</span>.+?</li></a>').findall(html_code)
  
  while True:
    anime = random.choice(anime_elements)
    
    if anime[1] != '0':
      url = base_url + anime[0]
      break 
      
  list_episodes(url, list_view, list_episodes_mode)
    
def resolve_episode(episode_page_url):
  #xbmc.log('\n VC_DEBUG - ' + url)
  html_code = open_url(episode_page_url)
  #soup = BeautifulSoup(html_code, 'html.parser')
  
  video_source = re.compile('(http.+\.mp4)').findall(html_code)[0]
  
  list_item = create_episode_list_item(html_code, video_source)
  add_link(video_source, list_item)

################################################
#              Aux Methods                     #
################################################

def open_url(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0')
	response = urllib2.urlopen(request)
	content = response.read()
	response.close()
  
	return content
    
def get_base_url():
  return base64.b64decode(base_url)
    
def add_paging(soup, url, mode):
  page_number = get_page_number_from_url(url)
  last_page_num = 1

  next_page_label = 'Página Seguinte ►'
  next_page_description = 'Avançar para a página seguinte.'
  
  pagination_ul = soup.find('ul', {'class': 'pagination'})
  
  if len(pagination_ul) > 1:
    last_page_url = pagination_ul.findAll('li')[-1].a['data-url']
    last_page_num = get_page_number_from_url(last_page_url)
    #xbmc.log('\n[VC_DEBUG] soup: ' + pagination_ul.renderContents())

  if page_number >= last_page_num:
    is_folder = False
    page_url = url
    next_page_label = '[COLOR grey]' + next_page_label + '[/COLOR]'
  else: 
    is_folder = True
    page_url = re.sub('/lista-completa/\d+', '/lista-completa/' + str(int(page_number) + 1), url)
    
  add_dir(next_page_label, page_url, mode, icons_folder + 'next.png', is_folder, plot = next_page_description)

def get_page_number_from_url(url):
  page_number = re.compile('/lista-completa/(\d+)').findall(url)[0]
  return int(page_number)
  
def create_episode_list_item(html_code, url):
  soup = BeautifulSoup(html_code, 'html.parser')

  title = soup.head.title.text
  tvshowtitle = re.compile('(.*) - Epis.dio \d+').findall(title)[0]
  episode_number = re.compile('Epis.dio (\d+)').findall(title)[0]
  
  dateadded = re.compile('"uploadDate": "(.+)"').findall(html_code)[0]
  genre = re.compile('G.+neros:</b> (.*)\.').findall(html_code)[0].split(',')
  
  duration_full = soup.find(itemprop = 'duration').text
  duration_minutes = duration_full.split(':')[0]
  duration_seconds = duration_minutes * 60 + duration_full.split(':')[1]

  list_item = xbmcgui.ListItem('[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle, path = url, thumbnailImage = ad_here)
  #list_item.setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
  #[thumb, poster, banner, fanart, clearart, clearlogo, landscape, icon]
  
  list_item.setProperty('fanart_image', fanart)
  list_item.setInfo('video', {'title': tvshowtitle,
                              'tvshowtitle': tvshowtitle,
                              'originaltitle': tvshowtitle,
                              'sorttitle': tvshowtitle,
                              'genre': genre,
                              'tag': genre,
                              'episode': episode_number,
                              'sortepisode': episode_number,
                              'dateadded': dateadded,
                              'duration': duration_seconds,
                              'mediatype': 'episode',
                              'lastplayed': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              'path': url})
                            
  return list_item

def create_anime_list_item(html_code):
  soup = BeautifulSoup(html_code, 'html.parser')

  title = soup.find_all('span', { 'itemprop' : 'name' })[0].string
  year = soup.find_all('span', { 'itemprop' : 'copyrightYear' })[0].string
  studio = soup.find_all('span', { 'itemprop' : 'productionCompany' })[0].string
  writer = soup.find_all('span', { 'itemprop' : 'author' })[0].string
  image = soup.find_all('img', { 'class' : ' img-hover' })[0]['src']
  status = re.compile('<p><b>Status:</b>(.+?)</p>').findall(html_code)[0]
  plot = soup.find_all('span', { 'itemprop' : 'description' })[0].text
  
  genre_list = soup.find_all('span', { 'itemprop' : 'genre' })[0].contents
  genres = []
  
  for genre in genre_list:
    genre_string = genre.string
    if not genre_string.isspace(): genres.append(genre_string.strip(','))
    
  list_item = xbmcgui.ListItem('[COLOR crimson][B]INFO[/B][/COLOR] ' + title + ' ([COLOR crimson]' + year + '[/COLOR])', thumbnailImage = image)
  list_item.setProperty('fanart_image', fanart)
  list_item.setInfo('video', {'title': title,
                              'tvshowtitle': title,
                              'originaltitle': title,
                              'sorttitle': title,
                              'genre': genres,
                              'tag': genres,
                              'year': year,
                              'premiered': year,
                              'status': status,
                              'studio': studio,
                              'writer': writer,
                              'plot': plot,
                              'plotoutline': plot,
                              'mediatype': 'tvshow',
                              'tagline': '[B]Estado:[/B]' + status + '\n[B]Género: [/B]' + ', '.join(genres),
                              'path': url})
                            
  return list_item

def get_anime_from_episode_page(episode_page_url):
  html_code = open_url(episode_page_url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  anime_url = base_url + re.compile('<b>Categoria do Anime:</b> <a href="(.+?)" class="tag">.+?</a>').findall(html_code)[0]
  
  list_episodes(anime_url, list_view, list_episodes_mode)

def check_version():
  server_version = get_server_version()
  local_version = get_local_version()
  xbmc.log('\n[VC_DEBUG] Local Version: ' + local_version)
  xbmc.log('\n[VC_DEBUG] Server Version: ' + server_version)
  
  if server_version > local_version:
    local_splited = local_version.split('.')
    local_major = local_splited[0]
    local_minor = local_splited[1]
    local_patch = local_splited[-1]
    
    server_splited = server_version.split('.')
    server_major = server_splited[0]
    server_minor = server_splited[1]
    server_patch = server_splited[-1]
    
    if server_major > local_major or server_minor > local_minor:
      update_major()
    elif server_patch > local_patch:
      update_patch()

    xbmcgui.Dialog().notification('AniTube', 'Add-on atualizado', addon_folder + '/resources/icon.png')

def get_server_version():
  xml_code = open_url('https://raw.githubusercontent.com/Vitcesar/plugin.video.anitube/master/addon.xml')
  soup = BeautifulSoup(xml_code, 'html.parser')
  
  return soup.addon['version']
  
def get_local_version():
  xml_file = open(addon_folder + '/addon.xml')
  soup = BeautifulSoup(xml_file, 'html.parser')
  
  return soup.addon['version']
  
def update_patch():
  #TODO
  return

def update_major():
  master_zip = requests.get('https://github.com/Vitcesar/plugin.video.anitube/archive/master.zip')
  
  with ZipFile(io.BytesIO(master_zip.content), 'r') as zip:
    zip.extractall(addon_folder + '/..')
  
  return

################################################
#            Media Methods                     #
################################################

def add_link(url, list_item):
  return xbmcplugin.addDirectoryItem(handle = __handle__, url = url, listitem = list_item)
  
def add_dir(name, url, mode, image = '', is_folder = True, total_items = 1, plot = '', is_episode = False):
  name = name.encode(encoding = 'UTF-8', errors = 'strict')
  
  link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
  
  item = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png', thumbnailImage = image)
  item.setProperty('fanart_image', fanart)
  
  contextMenuItems = []
  
  if is_episode: contextMenuItems.append(('Abrir Anime', 'xbmc.Container.Update(%s?mode=%s&url=%s)' % (sys.argv[0], from_episode_to_anime_mode, url)))  
  contextMenuItems.append(('Refrescar', 'xbmc.Container.Refresh'))
  
  item.addContextMenuItems(contextMenuItems)
  
  if not plot: plot = name
  
  item.setInfo(type = 'video', infoLabels = {'title': name, 'plot': plot})
  
  return xbmcplugin.addDirectoryItem(handle = __handle__, url = link, listitem = item, isFolder = is_folder, totalItems = total_items)
    
################################################
#               Get Parameters                 #
################################################

def get_params():
  param = []
  param_string = sys.argv[2]
  
  if len(param_string) >= 2:
    params = sys.argv[2]
    cleaned_params = params.replace('?', '')
    
    if (params[len(params) - 1] == '/'):
      params = params[0 : len(params) - 2]
    
    pairs_of_params = cleaned_params.split('&')
    param = { }
    
    for i in range(len(pairs_of_params)):
      splited_params = { }
      splited_params = pairs_of_params[i].split('=')
      
      if (len(splited_params)) == 2:
        param[splited_params[0]] = splited_params[1]
  
  return param
      
params = get_params()
url = None
name = None
mode = None
icon_image = None

try: url = urllib.unquote_plus(params['url'])
except (KeyError, TypeError): pass

try: name = urllib.unquote_plus(params['name'])
except (KeyError, TypeError): pass
        
try: mode = int(params['mode'])
except (KeyError, TypeError): pass

try: icon_image = urllib.unquote_plus(params['iconImage'])
except (KeyError, TypeError): pass

################################################
#                  Modes                       #
################################################

if mode == None or url == None or len(url) < 1: main_menu() 
elif mode == 1: list_genres(url) 
elif mode == 2: list_episodes(url, list_view, list_episodes_mode) 
elif mode == 3: resolve_episode(url)
elif mode == 5: list_alphabet(url) 
elif mode == 6: list_episodes(url, wall_view, recent_episodes_mode)
elif mode == 8: list_animes(url) 
elif mode == 9: random_anime()
elif mode == 10: get_anime_from_episode_page(url)

xbmcplugin.endOfDirectory(__handle__)