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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, sys
from bs4 import BeautifulSoup
from xbmcgui import ListItem

versao = '0.0.4'
addon_id = 'plugin.video.anitube'
selfAddon = xbmcaddon.Addon(id = addon_id)
addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.jpg'
baseUrl = 'http://anitubebr.biz'

genresMode = 1
listEpsMode = 2
resolveEpMode = 3
searchMode = 4
listSubLettersMode = 5
listRecentEpsMode = 6
listDubLettersMode = 7
animesMode = 8

listView = 'Container.SetViewMode(0)'
posterView = 'Container.SetViewMode(51)'
shiftView = 'Container.SetViewMode(53)'
infoWallView = 'Container.SetViewMode(54)'
wideListView = 'Container.SetViewMode(55)'
wallView = 'Container.SetViewMode(500)'
fanartView = 'Container.SetViewMode(502)'

def  mainMenu ():
  addDir('Recentes',   baseUrl + '/animes-lancamentos', listRecentEpsMode,  artfolder + 'new.png')
  addDir('Legendados', baseUrl + '/anime',              listSubLettersMode, artfolder + 'sort.png')
  addDir('Dublados',   baseUrl + '/animes-dublado',     listDubLettersMode, artfolder + 'dubbed.png')
  addDir('Géneros',    baseUrl + '/genero',             genresMode,         artfolder + 'genres.png')
  addDir('Pesquisar',  baseUrl,                         searchMode,         artfolder + 'search.png')
  
  xbmcplugin.setContent(int(sys.argv[1]),'movies')
  xbmc.executebuiltin(shiftView)

def listGenres(url):
  htmlCode = openUrl(url)
  
  genres = re.compile('<a href="(.+?)" class="list-group-item"> <!-- <span class="badge"></span> --> (.+?)</li></a>').findall(htmlCode)
  
  for genreUrl, genreTitle in genres:
    addDir(genreTitle, baseUrl + genreUrl, animesMode, artfolder + 'genres.png', True, len(genres), 'Lista de animes legendados na categoria de ' + genreTitle + '.')
    
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin(wideListView)
  
def listAnimesInitials(url, modeImage, modeName):
  htmlCode = openUrl(url)  
  soup = BeautifulSoup(htmlCode, "html.parser")

  leters = soup.find("div", { "id" : "abasSingle" })
  letersStr = str(leters)
  
  aTags = re.compile('<a href="(.+?)">(.+?)</a>').findall(letersStr)
    
  for animeListUrl, letter in aTags:
    animeListUrl = baseUrl + animeListUrl
    addDir(letter, animeListUrl, animesMode, modeImage, True, len(aTags), 'Lista de animes ' + modeName + ' começados por ' + letter + '.')
    
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin(wideListView)

animesData = []
  
def listAnimes(url):
  htmlCode = openUrl(url)
  soup = BeautifulSoup(htmlCode, "html.parser")
  
  pageTitle = soup.title.string
  
  if 'Genero' in pageTitle:
    animes = soup.find_all('div', { 'class' : 'imagePlace' })
        
    for anime in animes:
      animeUrl = baseUrl + anime.a['href']
      animePageHtml = openUrl(animeUrl)
      animeSoup = BeautifulSoup(animePageHtml, "html.parser")
      plot = getAnimePlot(animeSoup)
           
      addDir(anime.a['title'], animeUrl, listEpsMode, baseUrl + anime.img['src'], True, len(animes), plot)
    
  if ('Anime' in pageTitle) or ('Dublado' in pageTitle):
    #regex for subbed and dubbed
    animeElements = re.compile('<a href="(.+?)" class="list-group-item"><span class="badge">(.+?)</span> (.+?)</li></a>').findall(htmlCode)
        
    for animeUrl, numEpisodes, title in animeElements:
      if numEpisodes != '0':
        title = title + ' (' + numEpisodes + ' Episódios)'
        
        animeUrl = baseUrl + animeUrl
        animeData = getAnimeData(animeUrl)
        img = animeData[0]
        plot = animeData[1]
        
        addDir(title, animeUrl, listEpsMode, img, True, len(animeElements), plot)
    
  addPagingControls(htmlCode, animesMode)

  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin(listView)

def listEpisodes(url, view, modeId):
  htmlCode = openUrl(url)
  soup = BeautifulSoup(htmlCode, "html.parser")
  
  a = []
  genres = soup.find_all('div', { 'class' : 'well well-sm' })
  
  for genre in genres:
    try:
      temp = [baseUrl + genre.a['href'], '%s' % (genre.a.img['title'].encode('utf8', 'ignore')), genre.a.img['src']] 
      a.append(temp)
    except:
      pass
        
  for episodeUrl, title, img in a:
    # Se o vídeo ainda estiver a ser processado pelo site e não der para reproduzir de imediato.
    try: title = episode.find('div', { 'class' : 'label-private' }).string + title
    except: pass
  
    if 'http' not in img:
      img = baseUrl + img
    
    addDir(title, episodeUrl, resolveEpMode, img, False, len(a), title)
    
  addPagingControls(htmlCode, modeId)
  
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin(view) 

def search():
  keyb = xbmc.Keyboard('', 'Pesquisar...')
  keyb.doModal()
  
  if (keyb.isConfirmed()):
    search = keyb.getText()
    searchParameter = urllib.quote(search)
    url = baseUrl + '/busca/?search_query=' + str(searchParameter)
    listEpisodes(url, wideListView, listEpsMode)
    
def resolveEpisode(url):
  htmlCode = openUrl(url)  
  match = re.compile('<br>\n<script type="text/javascript" src="(.+?)"></script>').findall(htmlCode)
  
  for url2 in match:
    html2 = openUrl(url2)
    newMatch = re.compile("source: '(.+?)',").findall(html2)
    
  qualities = []
  
  try: 
    hdFileUrl = newMatch[1]
    qualities.append("HD")
  except: 
    pass
  
  try: 
    sdFileUrl = newMatch[0]
    qualities.append("SD")
  except: 
    pass
  
  quality = xbmcgui.Dialog().select('Escolha a qualidade', qualities)
  
  if quality == 0: xbmc.Player().play(hdFileUrl)
  if quality == 1: xbmc.Player().play(sdFileUrl)   
  
################################################
#    Métodos auxiliares                        #
################################################

def openUrl(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(request)
	link = response.read()
	response.close()
  
	return link
    
def addPagingControls(htmlCode, modeId):
  soup = BeautifulSoup(htmlCode, "html.parser")
  pages = soup.find('div', { 'class' : 'hidden-xs center m-b--15' }).find_all('a')

  for page in pages:
    if page.string == 'Primeiro':
      addDir('<< Primeira Página', baseUrl + page['href'], modeId, artfolder + 'prev.png', True, 1, 'Voltar para a primeira página.')
    
    if page.string == 'Voltar':
      addDir('< Página Anterior',  baseUrl + page['href'], modeId, artfolder + 'prev.png', True, 1, 'Voltar para a página anterior.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Avançar'):
      addDir('Página Seguinte >',  baseUrl + page['href'], modeId, artfolder + 'next.png', True, 1, 'Avançar para a página seguinte.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Último'):
      addDir('Última Página >>',   baseUrl + page['href'], modeId, artfolder + 'next.png', True, 1, 'Avançar para a última página.')
  
def getAnimeData(url):
  htmlCode = openUrl(url)
  soup = BeautifulSoup(htmlCode, "html.parser")

  image = getAnimeImage(soup)
  plot = getAnimePlot(soup)

  return (image, plot)
  
def getAnimeImage(soup):
  imageElement = soup.find(itemprop = "thumbnailUrl")  
  image = ''
  
  try: image = imageElement['content']
  except: pass
  
  return image
  
def getAnimePlot(soup):
  yearElement = soup.find(itemprop = "copyrightYear")
  plotElement = soup.find(itemprop = "description")
  plot = ''
    
  try: plot = 'Ano: ' + yearElement.string + '\n'
  except: pass
  
  try: plot += 'Sinopse: ' + plotElement.string.strip()
  except: pass
  
  return plot

################################################
#    Funções relacionadas a media.             #
################################################

def addLink(name, url, iconImage, plot):
  ok = True
  liz = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = iconImage)
  liz.setProperty('fanart_image', fanart)
  liz.setInfo(type = "Video", infoLabels = { "Title" : name, "Plot" : plot } )
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = liz)
  
  return ok

def addDir(name, url, mode, iconImage, pasta = True, total = 1, plot = ''):
  u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage = iconImage)
  liz.setProperty('fanart_image', fanart)
  liz.setInfo(type="video", infoLabels={ "title" : name, "plot" : plot })
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = pasta, totalItems = total)
  
  return ok
  
################################################
#    Pega os parametros                        #
################################################

def getParams():
  param = []
  paramString = sys.argv[2]
  
  if len(paramString) >= 2:
    params = sys.argv[2]
    cleanedParams = params.replace('?', '')
    
    if (params[len(params) - 1] == '/'):
      params = params[0 : len(params) - 2]
    
    pairsOfParams = cleanedParams.split('&')
    param = { }
    
    for i in range(len(pairsOfParams)):
      splitParams = { }
      splitParams = pairsOfParams[i].split('=')
      
      if (len(splitParams)) == 2:
        param[splitParams[0]] = splitParams[1]
  
  return param
      
params = getParams()
url = None
name = None
mode = None
iconImage = None

try: url = urllib.unquote_plus(params["url"])
except: pass

try: name = urllib.unquote_plus(params["name"])
except: pass
        
try: mode = int(params["mode"])
except: pass

try: iconImage = urllib.unquote_plus(params["iconImage"])
except: pass

################################################
#    Destina para cada modo.                   #
################################################

# Menu Inicial
if mode == None or url == None or len(url) < 1: mainMenu() 

# Géneros
elif mode == 1: listGenres(url) 

# Listar Episódios
elif mode == 2: listEpisodes(url, wideListView, listEpsMode) 

# Listar Qualidades & Play
elif mode == 3: resolveEpisode(url) 

# Pesquisar
elif mode == 4: search()

# Listar Letras (Legendados)
elif mode == 5: listAnimesInitials(url, artfolder + 'sort.png', 'legendados') 

# Episódios Recentes
elif mode == 6: listEpisodes(url, wallView, listRecentEpsMode)

# Listar Letras (Dublados)
elif mode == 7: listAnimesInitials(url, artfolder + 'dubbed.png', 'dublados') 

# Listar Animes
elif mode == 8: listAnimes(url) 

xbmcplugin.endOfDirectory(int(sys.argv[1]))