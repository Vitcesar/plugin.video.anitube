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
from selenium import webdriver

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
  
  add_dir('Lançamentos', get_base_url(),                     recent_episodes_mode, icons_folder + 'new.png')
  add_dir('Lista A-Z',   get_base_url() + '/lista-completa', list_alphabet_mode,   icons_folder + 'sort.png', total_items = 27)
  add_dir('Categorias',  get_base_url() + '/lista-completa', genres_mode,          icons_folder + 'genres.png')
  add_dir('Aleatório',   get_base_url(), random_anime_mode, icons_folder + 'random.png')
  
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
    #xbmc.log('\n[VC_DEBUG] soup: ' + anime.renderContents())    
    number_of_eps = re.compile('<b>Epis.+dios</b>: (\d+)').findall(anime.renderContents())[0]
    if int(number_of_eps) == 0: continue
    
    title = anime.find('h1', {'class': 'bottom-div'}).text
    
    if 'Dublado' in title: 
      continue
    else:      
      #xbmc.log('\n[VC_DEBUG] soup: ' + anime.renderContents())
      translation_type = re.compile('<b>Tipo</b>:(.+)<br').findall(anime.renderContents())[0]
      
      if 'Legendado' not in translation_type: continue
      
    title = re.sub('Legendado$', '', title)
    
    year = anime.find(itemprop = 'copyrightYear').text
    title = title + ' ([COLOR crimson]' + year + '[/COLOR])'
    
    anime_url = get_base_url() + anime.div.a['href']
    img = anime.div.a.img['src']
        
    add_dir(title, anime_url, list_episodes_mode, img)
    
  add_paging(soup, url, list_animes_mode)

  xbmcplugin.setContent(__handle__, 'tvshows')
  xbmc.executebuiltin(wide_list_view)

def list_episodes(url, view, mode):  
  if mode == recent_episodes_mode:
    html_code = open_url(url)
    soup = BeautifulSoup(html_code, 'html.parser')
  
    episodes = soup.find_all('article', { 'class' : 'col-3' })
    
    for x in range(16):
      episode = episodes[x]
      
      #xbmc.log('\n[VC_DEBUG] ' + str(episode))
      if 'Dublado' in str(episode): continue
      
      duration = episode.find(itemprop = 'duration').text.split(':')[0]
      if int(duration) == 0: continue
      
      title_full = episode.h4.text
      
      if 'Episodio' in title_full: tvshowtitle = re.compile('(.*) - Episodio \d+').findall(title_full)[0]
      else: continue
      
      if '...' in tvshowtitle: tvshowtitle = re.sub('\.\.\.', '', tvshowtitle).strip() + '…'
      else: tvshowtitle = tvshowtitle.strip()
      
      episode_number = re.compile('Episodio (\d+.?\d?)').findall(title_full)[0]
      
      title = '[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle
      
      episode_url = get_base_url() + episode.a['href']
      img = episode.a.img['src']
      
      add_dir(title, episode_url, resolve_episode_mode, img, True, 1, title, is_episode = True)
  elif mode == list_episodes_mode:
    if 'legendados' not in url: url = url + '/legendados/1'
    
    html_code = open_url(url)
    soup = BeautifulSoup(html_code, 'html.parser')
    
    episodes = soup.find_all('article', { 'class' : 'col-3' })
          
    anime_title = re.compile('<h3 class="truncate"><b>(.+)</b></h3>').findall(html_code)[0]
    year = re.compile('<b>Ano:</b> (\d+)<br>').findall(html_code)[0]
    
    list_item = create_anime_list_item(html_code, soup, anime_title, year)
    
    for ep in episodes:
      if 't-center' in str(ep['class']): continue      
      #xbmc.log('\n[VC_DEBUG] class: ' + str(ep))
      
      title = '[B]Episódio ' + re.compile('Epis.+dio (\d+)').findall(ep.renderContents())[0] + '[/B]'
      episode_url = get_base_url() + ep.div.a['href']
      
      add_dir(title, episode_url, resolve_episode_mode, list_item = list_item)
      
    add_paging(soup, url, mode)
      
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
  
  '''
  ff_profile_dir = addon_folder + '/selenium/webdriver/firefox'
  #ff_profile = webdriver.FirefoxProfile(profile_directory=ff_profile_dir)
  #driver = webdriver.Firefox(ff_profile)
  driver = webdriver.Chrome(addon_folder + r'/selenium/webdriver/chrome/chromedriver.exe')
  driver.get(episode_page_url) 
  html_code = driver.page_source
  xbmc.log('\n VC_DEBUG - ' + html_code)
  soup = BeautifulSoup(html_code, "html.parser")

  element = soup.find('video')
  
  xbmc.log('\n VC_DEBUG - ' + str(element))
  return



  '''
  #xbmc.log('\n VC_DEBUG - ' + url)
  html_code = open_url(episode_page_url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  #video_source = re.compile('(http[^"]+\.mp4)').findall(html_code)[0]
  #list_item = create_episode_list_item(html_code, soup, video_source)
  #xbmcplugin.addDirectoryItem(handle = __handle__, url = url, listitem = list_item)
  #return
  
  headers_fst = {  # headers dict to send in request
    'Host': 'www.anitube.xyz',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.79',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
  }
  requests.get('https://www.anitube.xyz/players/?contentId=UjlGNVhRKytKdmF5UHpoaHA1a2F5MndHVi92bExTMCs0UDlvOFBIMHB4WT0=', headers = headers_fst)
  
  video_source = 'https://www.anitube.xyz/players/p2.php?contentId=UjlGNVhRKytKdmF5UHpoaHA1a2F5MndHVi92bExTMCs0UDlvOFBIMHB4WT0='
  
  #r = requests.get(video_source,verify=False, stream=True)
  
  headers_snd = {  # headers dict to send in request
    #'Host': 'www.anitube.xyz',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.79',
    'chrome-proxy': 'frfr',
    'Accept': '*/*',
    'Referer': 'https://www.anitube.xyz/players/?contentId=UjlGNVhRKytKdmF5UHpoaHA1a2F5MndHVi92bExTMCs0UDlvOFBIMHB4WT0=',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Range': 'bytes=0-'
  }
 
  response = requests.get(video_source, headers = headers_snd)
  #xbmc.log('\n[VC_DEBUG] ' + str(response.headers['Location']))
  xbmc.log('\n[VC_DEBUG] Headers: ' + str(response.headers))
  xbmc.log('\n[VC_DEBUG] Status: ' + str(response.status_code))
  
  '''
  video_div = soup.find(id = 'player-container')
  video_source = get_base_url() + re.compile('file: "([^"]+)"').findall(str(video_div))[0] + '?text=true'
  xbmc.log('\n[VC_DEBUG] class: ' +video_source)
  '''
  
  list_item = create_episode_list_item(html_code, soup, video_source)
  
  #add_link(video_source, list_item)
  xbmcplugin.addDirectoryItem(handle = __handle__, url = url, listitem = list_item)
  #xbmcplugin.setResolvedUrl(__handle__, True, listitem=list_item)
  #xbmc.Player().play(video_source, list_item)

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
  curr_page_num = get_page_number_from_url(url)
  next_page_num = 1
  last_page_num = 1
  
  pagination_ul = soup.find('ul', {'class': 'pagination'})
  
  if len(pagination_ul) > 1:
    last_page_url = pagination_ul.findAll('li')[-1].a['data-url']
    last_page_num = get_page_number_from_url(last_page_url)    
    next_page_num = curr_page_num + 1
  
  #xbmc.log('\n[VC_DEBUG] last_page_num: ' + str(last_page_num))

  next_page_label = 'Página Seguinte'

  if curr_page_num >= last_page_num:
    is_folder = False
    
    page_url = url
    next_page_label = '[COLOR grey]' + next_page_label + ' (' + str(curr_page_num) + '/' + str(last_page_num) + ') ►[/COLOR]'
    next_page_description = 'Não há mais páginas.'
  else: 
    is_folder = True
    
    if 'lista-completa' in url: page_url = re.sub('/lista-completa/\d+', '/lista-completa/' + str(next_page_num), url)
    elif 'legendados' in url: page_url = re.sub('/legendados/\d+', '/legendados/' + str(next_page_num), url)
    
    next_page_label = next_page_label + ' ([COLOR crimson]' + str(curr_page_num) + '[/COLOR]/[COLOR crimson]' + str(last_page_num) + '[/COLOR]) ►'
    next_page_description = 'Avançar para a página ' + str(next_page_num) + ' de ' + str(last_page_num) + '.'
    
  add_dir(next_page_label, page_url, mode, icons_folder + 'next.png', is_folder, plot = next_page_description)

def get_page_number_from_url(url):
  try: page_number = re.compile('/lista-completa/(\d+)').findall(url)[0]
  except (IndexError): page_number = re.compile('/legendados/(\d+)').findall(url)[0]
  
  return int(page_number)
  
def create_episode_list_item(html_code, soup, url):
  soup = BeautifulSoup(html_code, 'html.parser')

  title = soup.head.title.text
  tvshowtitle = re.compile('(.*) - Epis.dio \d+').findall(title)[0]
  episode_number = re.compile('Epis.dio (\d+)').findall(title)[0]
  
  dateadded = re.compile('"uploadDate": "(.+)"').findall(html_code)[0]
  genre = re.compile('G.+neros:</b> (.*)\.').findall(html_code)[0].split(',')
  
  duration_full = soup.find(itemprop = 'duration').text
  duration_minutes = duration_full.split(':')[0]
  duration_seconds = duration_minutes * 60 + duration_full.split(':')[1]

  list_item = xbmcgui.ListItem('[COLOR crimson]Ep. ' + episode_number + '[/COLOR] ' + tvshowtitle, path = url)
  list_item.setArt({'poster': ad_here, 'fanart': fanart})
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

def create_anime_list_item(html_code, soup, title, year):
  studio = re.compile('<b>Est.+dio:</b> (.+)<br>').findall(html_code)[0]
  writer = re.compile('<b>Autor:</b> (.+)<br>').findall(html_code)[0]
  image = get_base_url() + soup.find_all('div', {'class': 'coverfly'})[0].img['src']
  status = re.compile('<b>Status Atual:</b> (.+)<br>').findall(html_code)[0]
  plot = soup.find(id = 'pcontent').div.text
  genres = re.compile('<b>G.+neros:</b> (.+)<br>').findall(html_code)[0]
    
  list_item = xbmcgui.ListItem()
  list_item.setArt({'thumb': image, 'fanart': fanart})
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
                              'tagline': '[B]Anime: [/B]' + title + ' (' + year + ')\n[B]Estado: [/B]' + status + '\n[B]Categoria(s): [/B]' + genres,
                              'path': url})
                            
  return list_item

def list_anime_eps_from_recent_ep(episode_page_url):
  html_code = open_url(episode_page_url)
  soup = BeautifulSoup(html_code, 'html.parser')
  
  anime_url = get_base_url() + soup.find(id = 'anime_name')['href']
  #anime_url = base_url + re.compile('<b>Categoria do Anime:</b> <a href="(.+?)" class="tag">.+?</a>').findall(html_code)[0]
  
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
  
def add_dir(name, url, mode, image = '', is_folder = True, total_items = 1, plot = '', is_episode = False, list_item = None):
  name = name.encode(encoding = 'UTF-8', errors = 'strict')  
  link = __url__ + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
  
  contextMenuItems = []  
  if is_episode: contextMenuItems.append(('Abrir Anime', 'xbmc.Container.Update(%s?mode=%s&url=%s)' % (sys.argv[0], from_episode_to_anime_mode, url)))  
  contextMenuItems.append(('Refrescar', 'xbmc.Container.Refresh'))
    
  if list_item is None:
    if not plot: plot = name
    
    list_item = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png')
    list_item.setArt({'thumb': image, 'fanart': fanart})
    list_item.addContextMenuItems(contextMenuItems)  
    list_item.setInfo(type = 'video', infoLabels = {'title': name, 'plot': plot})
  
  list_item.setLabel(name)
  
  return xbmcplugin.addDirectoryItem(handle = __handle__, url = link, listitem = list_item, isFolder = is_folder, totalItems = total_items)

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
elif mode == 10: list_anime_eps_from_recent_ep(url)

xbmcplugin.endOfDirectory(__handle__)