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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, sys, time, unicodedata, random, string
from bs4 import BeautifulSoup
from xbmcgui import ListItem

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])

reload(sys)  
sys.setdefaultencoding('utf8')

addon_id = 'plugin.video.anitube'
self_addon = xbmcaddon.Addon(id = addon_id)
addon_folder = self_addon.getAddonInfo('path')
icons_folder = addon_folder + '/resources/media/icons/'
fanart = addon_folder + '/resources/fanart.jpg'
base_url = 'http://anitubebr.com'

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

# Estuary skin
list_view = 'Container.SetViewMode(0)'
poster_view = 'Container.SetViewMode(51)'
shift_view = 'Container.SetViewMode(53)'
info_wall_view = 'Container.SetViewMode(54)'
wide_list_view = 'Container.SetViewMode(55)'
wall_view = 'Container.SetViewMode(500)'
fanart_view = 'Container.SetViewMode(502)'

def main_menu():
  add_dir('Recentes',   base_url + '/animes-lancamentos', recent_episodes_mode, icons_folder + 'new.png')
  add_dir('Legendados', base_url + '/anime',              sort_subbed_mode,     icons_folder + 'sort.png')
  add_dir('Géneros',    base_url + '/genero',             genres_mode,          icons_folder + 'genres.png')
  add_dir('Dublados',   base_url + '/animes-dublado',     list_animes_mode,     icons_folder + 'dubbed.png')
  add_dir('Tokusatsu',  base_url + '/tokusatsu',          list_animes_mode,     icons_folder + 'tokusatsu.png')
  add_dir('Pesquisar',  base_url,                         search_mode,          icons_folder + 'search.png')
  add_dir('Random',     base_url,                         random_anime_mode,    icons_folder + 'random.png')
  
  xbmcplugin.setContent(__handle__,'tvshows')
  xbmc.executebuiltin(shift_view)

def list_genres(url):
  html_code = open_url(url)
  
  genres = re.compile('<a href="(.+?)" class="list-group-item"> (.+?)</li></a>').findall(html_code)
  
  for genre_url, genre_title in genres:
    add_dir(genre_title, base_url + genre_url, list_animes_mode, icons_folder + 'genres.png', True, len(genres), 'Lista de animes legendados na categoria de ' + genre_title + '.')
    
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)
  
def list_anime_initials(url, mode_icon, mode_name):
  html_code = open_url(url)  
  soup = BeautifulSoup(html_code, 'html.parser')

  leters = soup.find('div', { 'id' : 'abasSingle' })
  leters_string = str(leters)
  
  a_tags = re.compile('<a href="(.+?)">(.+?)</a>').findall(leters_string)
    
  for anime_list_url, letter in a_tags:
    anime_list_url = base_url + anime_list_url
    add_dir(letter, anime_list_url, list_animes_mode, mode_icon, True, len(a_tags), 'Lista de animes ' + mode_name + ' começados por ' + letter + '.')
    
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_animes(url):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  page_title = soup.title.string
  
  if 'Genero' in page_title:
    animes = soup.find_all('div', { 'class' : 'imagePlace' })
        
    for anime in animes:
      anime_url = base_url + anime.a['href']
      title = anime.a['title']
      
      add_dir(title, anime_url, list_episodes_mode, base_url + anime.img['src'], total_items = len(animes))
    
  if ('Anime' in page_title) or ('Dublado' in page_title) or ('Tokusatsu' in page_title):
    anime_elements = re.compile('<a href="(.+?)" class="list-group-item"><span class="badge">(.+?)</span> (.+?)</li></a>').findall(html_code)
        
    for anime_url, num_episodes, title in anime_elements:
      if num_episodes != '0':
        title = title + ' ([COLOR blue]' + num_episodes + ' Episódios[/COLOR])'
        anime_url = base_url + anime_url
        add_dir(title, anime_url, list_episodes_mode, total_items = len(anime_elements))
    
  add_paging(soup, url, list_animes_mode)

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_episodes(url, view, mode):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  try:
    list_item = create_anime_list_item(html_code)
    add_link(None, list_item)
  except IndexError: pass
  
  episodes = soup.find_all('div', { 'class' : 'col-sm-6 col-md-4 col-lg-4' })
  
  for episode in episodes:
    episode_url = base_url + episode.a['href']
    title = episode.a.img['title']
    img = episode.a.img['src']
    
    try: title = '[COLOR red]' + episode.find_all('div', { 'class' : 'label-private' })[0].string + '[/COLOR] ' + title
    except IndexError: pass
  
    if 'http' not in img:
      img = base_url + img
    
    add_dir(title, episode_url, resolve_episode_mode, img, False, 1, title)
    
  add_paging(soup, url, mode)
  
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(view) 

def search():
  keyb = xbmc.Keyboard('', 'Pesquisar...')
  keyb.doModal()
  
  if (keyb.isConfirmed()):
    search = keyb.getText()
    search_parameter = urllib.quote(search)
    url = base_url + '/busca/?search_query=' + str(search_parameter)
    list_episodes(url, wide_list_view, list_episodes_mode)
    
def random_anime():
  url = get_random_anime_url();
  list_episodes(url, list_view, list_episodes_mode)
    
def resolve_episode(episode_page_url):
  html_code = open_url(episode_page_url)
  
  script_src = re.compile('<br>\n<script type="text/javascript" src="(.+?)"></script>').findall(html_code)
  
  for script_url in script_src:
    script_code = open_url(script_url)
    file_links = re.compile("source: '(.+?)'").findall(script_code)
    
  qualities = []
  
  try: 
    hd_file_url = file_links[1]
    qualities.append('HD')
  except: pass
  
  try:
    sd_file_url = file_links[0]
    qualities.append('SD')
  except: pass
    
  quality = xbmcgui.Dialog().select('Escolha a qualidade:', qualities)
  
  if quality == 0: 
    list_item = create_episode_list_item(html_code, hd_file_url)
    hd_file_url = hd_file_url + '|Referer=' + base_url
    xbmc.Player().play(hd_file_url, list_item)
  if quality == 1: 
    list_item = create_episode_list_item(html_code, sd_file_url)
    sd_file_url = sd_file_url + '|Referer=' + base_url
    xbmc.Player().play(sd_file_url, list_item)
  
################################################
#              Aux Methods                     #
################################################

def open_url(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0')
	response = urllib2.urlopen(request)
	link = response.read()
	response.close()
  
	return link
    
def add_paging(soup, url, mode):
  pages = soup.find('div', { 'class' : 'hidden-xs center m-b--15' }).find_all('a')
  
  for page in pages:
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Último'):
      last_page = get_page_number_from_url(page['href'])
      
  if last_page == '1': return

  current_page = get_page_number_from_url(url)
  
  for page in pages:
    if page.string == 'Primeiro':
      title = '<< Primeira Página ([COLOR blue]' + str(current_page) + '/' + str(last_page) + '[/COLOR])'
      add_dir(title, base_url + page['href'], mode, icons_folder + 'prev.png', True, 1, 'Voltar para a primeira página.')
    
    if page.string == 'Voltar':
      title = '< Página Anterior ([COLOR blue]' + str(current_page) + '/' + str(last_page) + '[/COLOR])'
      add_dir(title, base_url + page['href'], mode, icons_folder + 'prev.png', True, 1, 'Voltar para a página anterior.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Avançar'):
      title = 'Página Seguinte > ([COLOR blue]' + str(current_page) + '/' + str(last_page) + '[/COLOR])'
      add_dir(title, base_url + page['href'], mode, icons_folder + 'next.png', True, 1, 'Avançar para a página seguinte.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Último'):
      title = 'Última Página >> ([COLOR blue]' + str(current_page) + '/' + str(last_page) + '[/COLOR])'
      add_dir(title, base_url + page['href'], mode, icons_folder + 'next.png', True, 1, 'Avançar para a última página.')

def get_page_number_from_url(url):
  url_splited = url.split('/')
  
  for i, string in enumerate(url_splited):
    if string == 'page':
      return url_splited[i+1]
      
  return 1
  
def get_random_anime_url():
  animes_url = base_url + '/anime/letra/' + random.choice(string.ascii_uppercase)
  
  html_code = open_url(animes_url)
  
  anime_elements = re.compile('<a href="(.+?)" class="list-group-item"><span class="badge">(.+?)</span>.+?</li></a>').findall(html_code)
  
  while True:
    anime = random.choice(anime_elements)
    
    if anime[1] != '0':
      return base_url + anime[0]
  
def create_episode_list_item(html_code, url):
  soup = BeautifulSoup(html_code, 'html.parser')

  title = soup.find_all('meta', { 'itemprop' : 'description' })[0]['content']
  tvshowtitle = anime_elements = re.compile('<b>Categoria do Anime:</b> <a href=".+?" class="tag">(.+?)</a>').findall(html_code)[0]
  dateadded = soup.find_all('meta', { 'itemprop' : 'uploadDate' })[0]['content']
  genre = soup.find_all('meta', { 'itemprop' : 'genre' })[0]['content'].strip(',')
  image = soup.find_all('meta', { 'itemprop' : 'thumbnailUrl' })[0]['content']
  
  try: episode_id = int(soup.find_all('meta', { 'property' : 'og:url' })[0]['content'].strip('/').split('/')[-1])
  except ValueError: episode_id = None
  
  duration_seconds = soup.find_all('meta', { 'property' : 'video:duration' })[0]['content']
  duration_minutes = time.strftime('%M:%S', time.gmtime(float(duration_seconds)))
  
  try: 
    episode_number = int(title.split(' ')[-1])
  except ValueError:
    try:
      episode_number = int(title.split(' ')[-2])
    except (ValueError, IndexError): 
      episode_number = None
      
  try: season_number = re.compile('.+?\sS(\d)[\s$]').findall(title)[0]
  except IndexError: season_number = 1
    
  list_item = xbmcgui.ListItem(title, path = url, thumbnailImage = image)
  list_item.setInfo('video', {'title': title,
                              'tvshowtitle': tvshowtitle,
                              'originaltitle': title,
                              'sorttitle': title,
                              'genre': genre,
                              'tag': genre,
                              'episode': episode_number,
                              'sortepisode': episode_number,
                              'season': season_number,
                              'sortseason': season_number,
                              'duration': duration_minutes,
                              'dateadded': dateadded,
                              'overlay': 5,
                              'playcount': 1,
                              'mediatype': 'episode',
                              'setid': episode_id,
                              'tracknumber': episode_id
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
                              'premiered': year + '-00-00',
                              'status': status,
                              'studio': studio,
                              'writer': writer,
                              'plot': plot,
                              'plotoutline': plot,
                              'mediatype': 'tvshow',
                              'tagline': '[B]Estado:[/B]' + status + '\n[B]Género: [/B]' + ', '.join(genres)
                             })
                            
  return list_item

################################################
#            Media Methods                     #
################################################

#def add_link(name, url, image, plot):
#  ok = True
#  item = xbmcgui.ListItem(name, iconImage = 'DefaultVideo.png', thumbnailImage = image)
#  item.setProperty('fanart_image', fanart)
#  item.setInfo(type = 'Video', infoLabels = { 'Title' : name, 'Plot' : plot } )
#  ok = xbmcplugin.addDirectoryItem(handle = __handle__, url = url, listitem = item)
#  
#  return ok
  
def add_link(url, list_item):
  ok = True
  ok = xbmcplugin.addDirectoryItem(handle = __handle__, url = url, listitem = list_item)
  
  return ok

def add_dir(name, url, mode, image = '', is_folder = True, total_items = 1, plot = ''):
  try: link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
  except KeyError: link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name.encode('utf8'))
  
  ok = True
  item = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png', thumbnailImage = image)
  item.setProperty('fanart_image', fanart)
  
  if not plot: plot = name
  
  item.setInfo(type='video', infoLabels={ 'title' : name, 'plot' : plot })
  ok = xbmcplugin.addDirectoryItem(handle = __handle__, url = link, listitem = item, isFolder = is_folder, totalItems = total_items)
  
  return ok
  
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
except: pass

try: name = urllib.unquote_plus(params['name'])
except: pass
        
try: mode = int(params['mode'])
except: pass

try: icon_image = urllib.unquote_plus(params['iconImage'])
except: pass

################################################
#                  Modes                       #
################################################

if mode == None or url == None or len(url) < 1: main_menu() 
elif mode == 1: list_genres(url) 
elif mode == 2: list_episodes(url, list_view, list_episodes_mode) 
elif mode == 3: resolve_episode(url) 
elif mode == 4: search()
elif mode == 5: list_anime_initials(url, icons_folder + 'sort.png', 'legendados') 
elif mode == 6: list_episodes(url, wall_view, recent_episodes_mode)
#elif mode == 7: list_anime_initials(url, icons_folder + 'dubbed.png', 'dublados') 
elif mode == 8: list_animes(url) 
elif mode == 9: random_anime() 

xbmcplugin.endOfDirectory(__handle__)