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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, sys, time, unicodedata, random, string, socket, requests
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
base_url = 'https://www.anitube.xyz/'

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
  add_dir('Lançamentos', base_url + '/categoria/lancamentos',       recent_episodes_mode, icons_folder + 'new.png')
  #add_dir('Legendados',  base_url + '/categoria/animes-legendados', sort_subbed_mode,     icons_folder + 'sort.png')
  #add_dir('Gêneros',     base_url + '/animes-por-generos',          genres_mode,          icons_folder + 'genres.png')
  #add_dir('Dublados',    base_url + '/categoria/animes-dublados',   list_animes_mode,     icons_folder + 'dubbed.png')
  #add_dir('Desenhos',    base_url + '/categoria/desenhos',          list_animes_mode,     icons_folder + 'cartoons.png')
  #add_dir('Tokusatsus',  base_url + '/categoria/tokusatsus',        list_animes_mode,     icons_folder + 'tokusatsu.png')
  #add_dir('Filmes',      base_url + '/categoria/filmes',            list_animes_mode,     icons_folder + 'movies.png')
  #add_dir('Pesquisar',   base_url,                                  search_mode,          icons_folder + 'search.png')
  #add_dir('Random',      base_url,                                  random_anime_mode,    icons_folder + 'random.png')
  
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
    anime_list_url = url + '/' + anime_list_url
    add_dir(letter, anime_list_url, list_animes_mode, mode_icon, True, len(a_tags), 'Lista de animes ' + mode_name + ' começados por ' + letter + '.')
    
  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_animes(url):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  #page_title = soup.title.string
  anitube_logo = soup.find('div', { 'id' : 'logo' }).img['src']
  
  animes_div_id = url[-1:]
  animes_div = soup.find('div', { 'id' : animes_div_id })
  
  animes = animes_div.find_all('li')
  
  for anime in animes:    
    title_verbose = anime.a['title']
    title = re.compile('(.*) . Todos.?.?.? Epis.dios').findall(title_verbose)[0]
    
    add_dir(title, anime.a['href'], list_episodes_mode, anitube_logo, total_items = len(animes))
  
  '''
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
  ''' 

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_episodes(url, view, mode):
  html_code = open_url(url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  if 'Todos os Epis' in soup.title.string:
    video_lists = soup.find_all('ul', { 'class' : 'lcp_catlist' })
    
    for list in video_lists:
      videos = list.find_all('a')
      
      for video in videos:        
        if 'Todos os Epis' in video['title']: continue
        
        #title = re.compile('.*? .{1} (.*)').findall(video['title'])[0]
        title = video['title']
        
        img_div = soup.find(id = 'capaAnime')
        img = img_div.img['src']
        
        if 'http' not in img: img = base_url + img
        
        plot = soup.find('p', { 'id' : 'sinopse2' })
        if not plot: plot = soup.find('div', { 'id' : 'sinopse2' }).p.get_text()
        #if not plot: plot = re.compile('</h2>\n<p>(.*)</p>').findall(html_code)[0]
        else: plot = plot.string
        
        #plot = plot.replace('<br />', '')
        
        year = re.compile('<strong>Ano:</strong> (\d{4})</div>').findall(html_code)[0]
        year = '[B]Ano:[/B] ' + year
        
        anime_name = '[B]' + soup.find(property = 'article:section')['content'] + '[/B]'
        
        status = re.compile('<strong>Status do Anime:</strong> (.+)</div>').findall(html_code)[0]
        status = '[B]Estado:[/B] ' + status
        
        genres = re.compile('<strong>Genero:</strong> (.+)</div>').findall(html_code)[0]
        genres = '[B]Categoria(s):[/B] ' + genres
        
        #plot = anime_name + ' ([COLOR blue]' + year + '[/COLOR])\r\n[I]' + status + '\r\n' + genres + '\r\n\r\n[/I]' + plot
        plot = '[I]' + year + '\r\n' + status + '\r\n' + genres + '\r\n\r\n[/I]' + plot
      
        add_dir(title, video['href'], resolve_episode_mode, img, True, 1, plot, is_episode = True)
  
  elif 'Lançamentos' in soup.title.string:
    main_box = soup.find_all('div', { 'class' : 'mainBox' })[0]
    episodes = main_box.find_all('div', { 'class' : 'videoThumb' })

    for episode in episodes:
      episode_url = episode.a['href']
      title = episode.a['title']
    
      img = episode.img['src']
      if 'http' not in img:
        img = base_url + img
      #xbmcgui.Dialog().textviewer('img', img)
      
      add_dir(title, episode_url, resolve_episode_mode, img, True, 1, title, is_episode = True)

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
  html_code = open_url(episode_page_url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  players = soup.find_all('div', { 'class' : 'GTTabs_divs' })
    
  for player in players:
    video_url = player.video['src']
    
    if requests.get(video_url, stream=True).status_code == 404: continue
    
    player_title = player.span.string
    
    list_item = create_episode_list_item(html_code, video_url)
    list_item.setLabel('[COLOR blue]' + player_title + '[/COLOR] ' + list_item.getLabel())
    add_link(video_url, list_item)
  
################################################
#              Aux Methods                     #
################################################

def open_url(url):
  html_code = requests.get(url).text
  return html_code
    
def add_paging(soup, url, mode):
  pages_div = soup.find('div', { 'class' : 'wp-pagenavi' })
  
  pages_span = pages_div.find('span', { 'class' : 'pages' })
  last_page_number = re.compile('P.gina .* de (.*)').findall(pages_span.text)[0]
  if last_page_number == '1': return
  
  last_page_element = pages_div.find('a', { 'class' : 'last' })
  if not last_page_element: last_page_url = get_url_from_page_number(url, last_page_number)
  else: last_page_url = last_page_element['href']
  
  first_page_element = pages_div.find('a', { 'class' : 'first' })
  if not first_page_element: first_page_url = get_url_from_page_number(url, '1')
  else: first_page_url = first_page_element['href']
  
  current_page_number = pages_div.find('span', { 'class' : 'current' }).text
  
  previous_page_element = pages_div.find('a', { 'class' : 'previouspostslink' })
  if not previous_page_element: previous_page_url = base_url
  else: previous_page_url = previous_page_element['href']
  
  next_page_element = pages_div.find('a', { 'class' : 'nextpostslink' })
  if not next_page_element: next_page_url = base_url
  else: next_page_url = next_page_element['href']


  if current_page_number == '1':
    is_folder = False
    title = '[COLOR grey]<< Primeira Página (' + str(current_page_number) + '/' + str(last_page_number) + ')[/COLOR]'
  else:
    is_folder = True
    title = '<< Primeira Página ([COLOR blue]' + str(current_page_number) + '/' + str(last_page_number) + '[/COLOR])'
    
  add_dir(title, first_page_url, mode, icons_folder + 'prev.png', is_folder, 1, 'Voltar para a primeira página.')
    
  if current_page_number == '1':
    is_folder = False
    title = '[COLOR grey]< Página Anterior (' + str(current_page_number) + '/' + str(last_page_number) + ')[/COLOR]'
  else:
    is_folder = True
    title = '< Página Anterior ([COLOR blue]' + str(current_page_number) + '/' + str(last_page_number) + '[/COLOR])'
  
  add_dir(title, previous_page_url, mode, icons_folder + 'prev.png', is_folder, 1, 'Voltar para a página anterior.')
    
  if current_page_number == last_page_number:
    is_folder = False
    title = '[COLOR grey]Página Seguinte > (' + str(current_page_number) + '/' + str(last_page_number) + ')[/COLOR]'
  else:
    is_folder = True
    title = 'Página Seguinte > ([COLOR blue]' + str(current_page_number) + '/' + str(last_page_number) + '[/COLOR])'
  
  add_dir(title, next_page_url, mode, icons_folder + 'next.png', is_folder, 1, 'Avançar para a página seguinte.')
    
  if current_page_number == last_page_number:
    is_folder = False
    title = '[COLOR grey]Última Página >> (' + str(current_page_number) + '/' + str(last_page_number) + ')[/COLOR]'
  else:
    is_folder = True
    title = 'Última Página >> ([COLOR blue]' + str(current_page_number) + '/' + str(last_page_number) + '[/COLOR])'
  
  add_dir(title, last_page_url, mode, icons_folder + 'next.png', is_folder, 1, 'Avançar para a última página.')

def get_page_number_from_url(url):
  url_splited = url.split('/')
  page_number = ''
  
  for i, string in enumerate(url_splited):
    if string == 'page':
      page_number = url_splited[i+1]
      break
  
  if not page_number: return '1'
  else: return page_number
  
def get_url_from_page_number(url, page_number):
  url_splited = url.split('/')
  
  for i, string in enumerate(url_splited):
    if string == 'page':
      url_splited[i + 1] = page_number
      break
        
  return '/'.join(url_splited)
  
def create_episode_list_item(html_code, url):
  soup = BeautifulSoup(html_code, 'html.parser')
  
  title_header = soup.find_all('h1', { 'class' : 'mainBoxHeader' })[0].text
  title = re.compile('ANITUBE -(.+?) - Assistir Online').findall(title_header)[0]
  
  tvshowtitle = soup.find(property = 'article:section')['content']
  
  dateadded = soup.find_all('span', { 'itemprop' : 'uploadDate' })[0]['content']
  
  image = soup.find(itemprop = 'thumbnailUrl')['content']
    
  #minutes = re.compile('<p>Dura.ao: <span>(.+?)m .+?s</span></p>').findall(html_code)[0]
  #seconds = re.compile('<p>Dura.ao: <span>.+?m (.+?)s</span></p>').findall(html_code)[0]
  #duration_seconds = int(minutes) * 60 + int(seconds)
  duration_seconds = None
  
  try: 
    episode_number = int(re.compile('Epis.dio (.+?):').findall(title)[0])
  except IndexError:
    try: 
      episode_number = int(re.compile('Epis.dio (.*)').findall(title)[0])
    except ValueError: 
      episode_number = None
  
  list_item = xbmcgui.ListItem(title, path = url, thumbnailImage = image)
  list_item.setProperty('fanart_image', fanart)
  list_item.setInfo('video', {'title': title,
                              'tvshowtitle': tvshowtitle,
                              'originaltitle': title,
                              'sorttitle': title,
                              'episode': episode_number,
                              'sortepisode': episode_number,
                              'duration': duration_seconds,
                              'dateadded': dateadded,
                              'mediatype': 'episode'
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
  
  if is_episode: contextMenuItems.append(('Ir para anime', 'xbmc.Container.Update(%s?mode=%s&url=%s)' % (sys.argv[0], from_episode_to_anime_mode, url)))
  
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
elif mode == 5: list_anime_initials(url, icons_folder + 'sort.png', 'legendados') 
elif mode == 6: list_episodes(url, wall_view, recent_episodes_mode)
#elif mode == 7: list_anime_initials(url, icons_folder + 'dubbed.png', 'dublados') 
elif mode == 8: list_animes(url) 
elif mode == 9: random_anime()
elif mode == 10: get_anime_from_episode_page(url)

xbmcplugin.endOfDirectory(__handle__)