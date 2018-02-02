#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2014
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

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, HTMLParser, sys
from tools import *
from xbmcgui import ListItem
from BeautifulSoup import BeautifulSoup

versao = '0.0.4'
addon_id = 'plugin.video.anitube'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.jpg'
baseUrl = 'http://anitubebr.biz'

def  mainMenu ():
  addDir('Recentes',   baseUrl + '/animes-lancamentos', 6, artfolder + 'new.png')
  addDir('Legendados', baseUrl + '/anime',              5, artfolder + 'sort.png')
  addDir('Dublados',   baseUrl + '/animes-dublado',     5, artfolder + 'dubbed.png')
  addDir('Géneros',    baseUrl + '/genero',             1, artfolder + 'genres.png')
  addDir('Pesquisar',  baseUrl,                         4, artfolder + 'search.png')
  
  xbmcplugin.setContent(int(sys.argv[1]),'movies')
  xbmc.executebuiltin('Container.SetViewMode(53)')
   
# View  51 - Poster
# View  53 - Shift
# View  54 - InfoWall
# View  55 - WideList
# View 500 - Wall
# View 502 - Fanart
# All Others - List

def listGenres(url):
  html = abrir_url(url)
  #html = unicode(html, 'ascii', errors='ignore')
  soup = BeautifulSoup(html)

  aTags = []
  genres = soup.findAll("a", { "class" : "list-group-item" })
  
  for genre in genres:
    #temp = [baseUrl + genre["href"],"%s" % (genre.string.encode('utf8', 'ignore'))]
    temp = [baseUrl + genre["href"], genre["href"].split('/')[2].title()]
    aTags.append(temp)
    
  noGenres = len(aTags)
  
  for genreUrl, title in aTags:
    title = cleanHtml(title)
    addDir(title, genreUrl, 8, '', True, noGenres)
    
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin('Container.SetViewMode(55)')
  
def listAnimesInitials(url):
  html = abrir_url(url)  
  #html = unicode(html, 'ascii', errors='ignore')
  soup = BeautifulSoup(html)

  leters = soup.find("div", { "id" : "abasSingle" })
  letersStr = str(leters)
  #print type(leters)
  aTags = re.compile('<a href="(.+?)">(.+?)</a>').findall(letersStr)
  
  noItems = len(aTags)
  
  for animeListUrl, letter in aTags:
    animeListUrl = baseUrl + animeListUrl
    letter = cleanHtml(letter)
    addDir(letter, animeListUrl, 8, '', True, noItems, 'Lista de animes começados pela letra ' + letter + '.')
    
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin('Container.SetViewMode(55)')
 
def listAnimes(url):
  html = abrir_url(url)  
  #html = unicode(html, 'ascii', errors='ignore')
  
  pageTitle = re.compile('<title>(.+?)</title>').findall(html)
  
  if pageTitle[0] == 'Genero - AniTube! Animes Online':
    #regex for genres
    animesHtmlTags = re.compile('<a class="internalUrl" href="(.+?)" title="(.+?)" rel="bookmark" itemprop="name">\n\t\t\t\t\t<img class="img-responsive" alt=".+?" title=".+?" src="(.+?)" itemprop="image">').findall(html)
    
    noAnimes = len(animesHtmlTags)
    
    for animeUrl, title, img in animesHtmlTags:
      animeUrl = baseUrl + animeUrl
      title = cleanHtml(title)
      img = baseUrl + img
      plot = getAnimeInfo(animeUrl)[1]
      addDir(title, animeUrl, 2, img, True, noAnimes, plot)
    
  if (pageTitle[0] == 'Anime ') or (pageTitle[0] == 'Animes Dublado'):
    animesHtmlTags = re.compile('<a href="(.+?)" class="list-group-item"><span class="badge">(.+?)</span> (.+?)</li></a>').findall(html)
    
    noAnimes = len(animesHtmlTags)
    
    for animeUrl, noEpisodes, title in animesHtmlTags:
      animeUrl = baseUrl + animeUrl
      title = title + ' (' + noEpisodes + ' Episódios)'
      title = cleanHtml(title)
      animeInfo = getAnimeInfo(animeUrl)
      img = animeInfo[0]
      plot = animeInfo[1]
      addDir(title, animeUrl, 2, img, True, noAnimes, plot)
    
  addPagingControls(html, 8)

  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin('Container.SetViewMode(52)')
  
def getAnimeInfo(url):
  html = abrir_url(url)
  soup = BeautifulSoup(html)
    
  imageMeta = soup.find(itemprop = "thumbnailUrl")
  yearSpan = soup.find(itemprop = "copyrightYear")
  plotSpan = soup.find(itemprop = "description")

  image = ''
  plot = ''

  try: image = imageMeta['content']
  except: pass
  
  try: plot = 'Ano: ' + yearSpan.text + '\n'
  except: pass
  
  try: plot += 'Sinopse: ' + plotSpan.text
  except: pass

  return (image, plot)
    
def addPagingControls(html, modeId):
  soup = BeautifulSoup(html)
  pages = soup.find('div', { 'class' : 'hidden-xs center m-b--15' }).findAll('a')

  for page in pages:
    if page.string == 'Primeiro':
      addDir('<< Primeira Página', baseUrl + page['href'], modeId, artfolder + 'prev.png', True, 1, 'Voltar para a primeira página.')
    
    if page.string == 'Voltar':
      addDir('< Página Anterior',  baseUrl + page['href'], modeId, artfolder + 'prev.png', True, 1, 'Voltar para a página anterior.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Avançar'):
      addDir('Página Seguinte >',  baseUrl + page['href'], modeId, artfolder + 'next.png', True, 1, 'Avançar para a página seguinte.')
    
    if re.sub('[^A-Za-z0-9]+', '', page.string) == re.sub('[^A-Za-z0-9]+', '', 'Último'):
      addDir('Última Página >>',   baseUrl + page['href'], modeId, artfolder + 'next.png', True, 1, 'Avançar para a última página.')

def listEpisodes(url, viewMode, modeId):
  html = abrir_url(url)
  #html = unicode(html, 'ascii', errors='ignore')
  soup = BeautifulSoup(html)
  
  a = []
  genres = soup.findAll('div', { 'class' : 'well well-sm' })
  
  for genre in genres:
    try:
      temp = [baseUrl + genre.a['href'], '%s' % (genre.a.img['title'].encode('utf8', 'ignore')), genre.a.img['src']] 
      a.append(temp)
    except:
      pass
      
  noEpisodes = len(a)
  
  for episodeUrl, title, img in a:
    if 'http' not in img:
      img = baseUrl + img
    title = cleanHtml(title)
    
    addDir(title, episodeUrl, 3, img, False, noEpisodes, title)
    
  addPagingControls(html, modeId)
  
  xbmcplugin.setContent(int(sys.argv[1]), 'movies')
  xbmc.executebuiltin('Container.SetViewMode(' + viewMode + ')')
    
def resolveEpisode(url):
  html = abrir_url(url)  
  match = re.compile('<br>\n<script type="text/javascript" src="(.+?)"></script>').findall(html)
  
  for url2 in match:
    html2 = abrir_url(url2)
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
  
  if quality == 0 :
    xbmc.Player().play(hdFileUrl)
  if quality == 1:
    xbmc.Player().play(sdFileUrl)    

def search():
  keyb = xbmc.Keyboard('', 'Pesquisar...')
  keyb.doModal()
  
  if (keyb.isConfirmed()):
    search = keyb.getText()
    searchParameter = urllib.quote(search)
    url = baseUrl + '/busca/?search_query=' + str(searchParameter) + '&tipo=desc'
    listEpisodes(url, '55', 2)

################################################
#    Funções relacionadas a media.             #
################################################

def addLink(name, url, iconimage, plot):
  ok = True
  liz = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = iconimage)
  liz.setProperty('fanart_image', fanart)
  liz.setInfo(type = "Video", infoLabels = { "Title" : name, "Plot" : plot } )
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = liz)
  return ok

def addDir(name, url, mode, iconimage, pasta = True, total = 1, plot = ''):
  u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage = iconimage)
  liz.setProperty('fanart_image', fanart)
  liz.setInfo(type="video", infoLabels={ "title" : name, "plot" : plot })
  ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = pasta, totalItems = total)
  return ok
  
################################################
#    Pega os parametros                        #
################################################

def getParams():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=sys.argv[2]
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  return param
      
params=getParams()
url=None
name=None
mode=None
iconimage=None

try: url=urllib.unquote_plus(params["url"])
except: pass

try: name=urllib.unquote_plus(params["name"])
except: pass
        
try: mode=int(params["mode"])
except: pass

try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

################################################
#    Destina para cada modo.                   #
################################################

if mode==None or url==None or len(url)<1:
        print "Sem mode"
        print "Inicio: Menu Principal"
        mainMenu()

elif mode==1:
  print "Mode: 1 - Listar Generos"
  listGenres(url)
  
elif mode==2:
  print "Mode: 2 - Listar Episodios"
  listEpisodes(url, '55', 2)

elif mode==3:
  print "Mode: 3 - Resolve Episodio"
  resolveEpisode(url)

elif mode==4:
  print 'Mode: 4 - Pesquisa'
  search()

elif mode==5:
  print 'Mode: 5 - Listar Letras'
  listAnimesInitials(url)
  
elif mode==6:
  print 'Mode: 6 - Listar Episodios Recentes'
  listEpisodes(url, '500', 6)
  
elif mode==8:
  print 'Mode: 8 - Listar Animes'
  listAnimes(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))