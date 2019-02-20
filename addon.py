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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, sys, time, unicodedata, random, string, base64, requests, io, datetime
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
base_url = 'aHR0cHM6Ly93d3cuYW5pbWVzb3Jpb24uaW8='

# Modes
genres_mode = 1
list_episodes_mode = 2
resolve_episode_mode = 3
search_mode = 4
sort_subbed_mode = 5
recent_episodes_mode = 6
#sort_dubbed_mode = 7
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
  
  add_dir('Últimos Lançamentos', get_base_url(),                      recent_episodes_mode, icons_folder + 'new.png')
  add_dir('Animes',              get_base_url() + '/lista-de-animes', sort_subbed_mode,     icons_folder + 'sort.png')
  #add_dir('Categorias',  base_url + '/genero',             genres_mode,          icons_folder + 'genres.png')
  #add_dir('Aleatório',   base_url,                         random_anime_mode,    icons_folder + 'random.png')
  
  xbmcplugin.setContent(__handle__,'tvshows')
  xbmc.executebuiltin(shift_view)

def list_genres(url):
  html_code = open_url(url)
  
  genres = re.compile('<a href="(.+?)" class="list-group-item"> (.+?)</li></a>').findall(html_code)
  
  for genre_url, genre_title in genres:
    add_dir(genre_title, base_url + genre_url, list_animes_mode, icons_folder + 'genres.png', True, len(genres), 'Lista de animes legendados na categoria de ' + genre_title + '.')
    
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)
  
def list_anime_initials(url):
  html_code = open_url(url)  
  soup = BeautifulSoup(html_code, 'html.parser')
  
  add_dir('#', get_base_url() + '/animes-com-numeros-ou-simbolos', list_animes_mode, ad_here, True, 1, 'Lista de animes começados por #.')
    
  letters_div = soup.find('div', { 'class' : 'Letras' })
  a_tags = letters_div.find_all('a')
  
  for letter in a_tags:
    if letter.text == 'All': continue
    anime_list_url = get_base_url() + '/lista-de-animes' + letter['href']
    
    add_dir(letter.text, anime_list_url, list_animes_mode, ad_here, True, 1, 'Lista de animes começados por ' + letter.text + '.')
    
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_animes(url):
  #xbmc.log('\n[VC_DEBUG] ' + url)
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  animes = soup.find_all('div', { 'class' : 'PostsItemImg' })
    
  for anime in animes:
    title = anime.a['title']
    title = re.sub('Todos os Epis.dios Online', '', title)
    title = re.sub('Todos os Epis.dios de ', '', title)
    
    anime_url = anime.a['href']
    
    img = anime.a.img['src']
    if 'fundososvideos.jpg' in img: img = addon_folder + '/resources/ani.png' # play safe
        
    add_dir(title, anime_url, list_episodes_mode, img)
    
  add_paging(soup, url, list_animes_mode)

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_episodes(url, view, mode):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  if mode == recent_episodes_mode:
    episodes = soup.find_all('div', { 'class' : 'PostsItemImg' })
    
    for episode in episodes:
      title = episode.a['title']      
      if 'Episódio ' not in title: continue
          
      tvshowtitle = re.compile('(.*) Epis.dio \d+').findall(title)[0]
      episode_number = re.compile('Epis.dio (\d+)').findall(title)[0]
      title = '[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle
      
      episode_url = episode.a['href']
      
      img = episode.a.img['src']
      if 'fundososvideos.jpg' in img: img = addon_folder + '/resources/ani.png'
      
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

def search():
  keyb = xbmc.Keyboard('', 'Pesquisar...')
  keyb.doModal()
  
  if (keyb.isConfirmed()):
    search = keyb.getText()
    search_parameter = urllib.quote(search)
    url = base_url + '/busca/?search_query=' + str(search_parameter)
    list_episodes(url, list_view, list_episodes_mode)
    
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
  xbmc.log('\n VC_DEBUG - ' + url)
  html_code = open_url(episode_page_url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  video_source = soup.find_all('source', { 'type' : 'video/mp4' })[0]['src']
  
  episode_id = url.split('/')[-1]
  
  list_item = create_episode_list_item(html_code, video_source, episode_id)
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
  url = base64.b64decode(base_url)
  return url
    
def add_paging(soup, url, mode):
  prev_page = soup.find('a', { 'class' : 'prev page-numbers' })
  next_page = soup.find('a', { 'class' : 'next page-numbers' })
  
  if prev_page is None:
    is_folder = False
    title = '[COLOR grey]<< Página Anterior[/COLOR]'
    page_url = get_base_url()
  else:
    is_folder = True
    title = '<< Página Anterior'    
    page_url = prev_page['href']
    
  add_dir(title, page_url, mode, icons_folder + 'prev.png', is_folder, 1, 'Voltar para a página anterior.')
  
  if next_page is None:
    is_folder = False
    title = '[COLOR grey]Página Seguinte >>[/COLOR]'
    page_url = get_base_url()
  else:
    is_folder = True
    title = 'Página Seguinte >>'    
    page_url = next_page['href']
    
  add_dir(title, page_url, mode, icons_folder + 'next.png', is_folder, 1, 'Avançar para a página seguinte.')

def get_page_number_from_url(url):
  url_splited = url.split('/')
  page_number = ''
  
  for i, string in enumerate(url_splited):
    if string == 'page':
      page_number = url_splited[i+1]
      break
  
  if not page_number: return '1'
  else: return page_number
  
def create_episode_list_item(html_code, url, episode_id):
  soup = BeautifulSoup(html_code, 'html.parser')

  title = soup.head.title.text
  tvshowtitle = re.compile('(.*) Epis.dio \d+').findall(title)[0]
  dateadded = soup.find(property = 'article:published_time')['content']
  image = soup.find(property = 'og:image')['content']
  genre = 'Anime'
  duration_seconds = 20 * 60
  episode_number = re.compile('Episódio (\d+)').findall(html_code)[0]
  season_number = 1

  list_item = xbmcgui.ListItem('[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle, path = url, thumbnailImage = ad_here)
  #list_item.setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
  #[thumb, poster, banner, fanart, clearart, clearlogo, landscape, icon]
  
  list_item.setProperty('fanart_image', fanart)
  list_item.setInfo('video', {'count' : episode_id,
                              'setid': episode_id,
                              'tracknumber': episode_id,
                              'title': title,
                              'tvshowtitle': tvshowtitle,
                              'originaltitle': title,
                              'sorttitle': title,
                              #'genre': genre,
                              #'tag': genre,
                              'episode': episode_number,
                              'sortepisode': episode_number,
                              #'season': season_number,
                              #'sortseason': season_number,
                              #'duration': duration_seconds,
                              'dateadded': dateadded,
                              'mediatype': 'episode',
                              'lastplayed': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              'path': url
                             })
                            
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
    
  list_item = xbmcgui.ListItem('[COLOR red][B]INFO[/B][/COLOR] ' + title + ' ([COLOR blue]' + year + '[/COLOR])', thumbnailImage = image)
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
                              'tagline': '[B]Estado:[/B]' + status + '\n[B]Género: [/B]' + ', '.join(genres)
                             })
                            
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
  try: link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
  except KeyError: link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name.encode('utf8'))
  
  item = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png', thumbnailImage = image)
  item.setProperty('fanart_image', fanart)
  
  contextMenuItems = []
  
  if is_episode:
    contextMenuItems.append(('Ir para anime', 'xbmc.Container.Update(%s?mode=%s&url=%s)' % (sys.argv[0], from_episode_to_anime_mode, url)))
  
  contextMenuItems.append(('Recarregar a página', 'xbmc.Container.Refresh'))
  item.addContextMenuItems(contextMenuItems)
  
  if not plot: plot = name
  
  item.setInfo(type='video', infoLabels={ 'title' : name, 'plot' : plot })
  
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
elif mode == 4: search()
elif mode == 5: list_anime_initials(url) 
elif mode == 6: list_episodes(url, wall_view, recent_episodes_mode)
#elif mode == 7: list_anime_initials(url, icons_folder + 'dubbed.png', 'dublados') 
elif mode == 8: list_animes(url) 
elif mode == 9: random_anime()
elif mode == 10: get_anime_from_episode_page(url)

xbmcplugin.endOfDirectory(__handle__)