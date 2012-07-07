####################################################################################################
#CBC.CA Video Plugin
#Written by mysciencefriend
#Overhauled and updated by Mikedm139
#Use at your own risk, etc. etc.

VIDEO_PREFIX = '/video/cbc'
NAME = 'CBC'

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

SHOWS = '2248506087'
MORE_SHOWS = '1329813962'

#NEWS_LIST = {'News'		:	'1221258968',
#				'Sports'	:	'1237510081',
#				'BC'		:	'1317899897',
#				'Calgary'	:	'1317901071',
#				'Edmonton'	:	'1317901477',
#				'Manitoba'	:	'1317902896',
#				'Montreal'	:	'1317903731',
#				'NB'		:	'1317906492',
#				'NL'		:	'1317907201',
#				'North'		:	'1317907460',
#				'NS'		:	'1317909223',
#				'Ottawa'	:	'1317910092',
#				'PEI'		:	'1317910853',
#				'Saskatchewan'	:	'1317911675',
#				'Toronto'	:	'1317912017',
#				'Windsor'	:	'1317913355'
#				}

#SHOWEXCEPTIONS = {'The Rick Mercer Report'				:	'Rick Mercer Report',
#				'The Ron James Show'			:	'Ron James Show',
#				'Hockey Night in Canada'		:	'HNIC',
#				'Q on bold'				:	'Q',
#				'George Stroumboulopoulos Tonight'	:	'George Tonight'
#				}

#SHOWEXCEPTIONS_REV = {'Rick Mercer Report'			:	'The Rick Mercer Report',
#					'Ron James Show'	:	'The Ron James Show',
#					'HNIC'			:	'Hockey Night in Canada',
#					'Q'			:	'Q on bold',
#					'George Tonight'	:	'George Stroumboulopoulos Tonight'
#					}

SHOWS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|%s'
VIDEOS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&query=CategoryIDs|%s&sortDescending=true&endIndex=500'
#LOCALLIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|1244502941'
#SHOWSURL = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=title&field=PID&field=ID&field=description&field=categoryIDs&field=thumbnailURL&field=URL&field=added&field=airdate&field=expirationDate&field=length&field=Keywords&query=%s&sortField=airdate&sortDescending=true&startIndex=1&endIndex=%s'
BASE_URL = 'http://www.cbc.ca'
PLAYER_URL = BASE_URL + '/player/%s/' 

CATEGORIES = ['News', 'Sports', 'Digital Archives']

#SMIL_URL = 'http://link.theplatform.com/s/h9dtGB/zRoOKQ_cN9OQOikWISihO5bmV8zWB3Xs?isPLS=false&airdate=1301356800000&site=cbcentca&zone=little_mosque_on_the_prairie&shortClip=false&show=little_mosque_on_the_prairie&liveondemand=ondemand&type=full_program&season=5&format=SMIL&Tracking=true&Embedded=true'

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

####################################################################################################
def VideoMainMenu():
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(ShowCategories), title=L('SHOWSMENU')))
    for category in CATEGORIES:
	oc.add(DirectoryObject(key=Callback(NewsCategories, category=category), title=category))
    
    return oc

####################################################################################################
def ShowCategories():
    oc = ObjectContainer(title2=L('SHOWSMENU'))
    data = HTML.ElementFromURL(PLAYER_URL % 'Shows')
    categories = data.xpath('//div[@id="catnav"]//a[@class="haschildren"]')
    for category in categories:
	title = category.text
	cat_id = category.xpath('parent::li')[0].get('data-id')
	oc.add(DirectoryObject(key=Callback(ShowsMenu, id=cat_id, title2=title), title=title))
    return oc

####################################################################################################
def ShowsMenu(id, title1=None, title2=None):
    oc = ObjectContainer()
    if title1:
	oc.title1=title1
    if title2:
	oc.title2=title2
    
    data = JSON.ObjectFromURL(SHOWS_LIST % id)
    
    if data['listInfo']['itemCount'] == 0:
	return VideoMenu(id, title1, title2)
    else:
	pass
    
    for item in data['items']:
	title = item['title']
	Log(title)
	id = item['ID']
	Log(id)
	oc.add(DirectoryObject(key=Callback(ShowsMenu, id=id, title1=title2, title2=title), title=title))
	
    oc.objects.sort(key = lambda obj: obj.title)
    if title2 == 'Shows':
	oc.add(DirectoryObject(key=Callback(ShowsMenu, id=MORE_SHOWS, title2='More Shows'), title='More Shows'))
	
    return oc

####################################################################################################
def NewsCategories(category):
    oc = ObjectContainer(title2=category)
    data = HTML.ElementFromURL(PLAYER_URL % String.Quote(category, usePlus=True))
    for item in data.xpath('//div[@id="catnav"]//a'):
	url = item.get('href')
	name = item.text
	oc.add(DirectoryObject(key=Callback(NewsSortMenu, title1=category, title2=name, url=url), title=name))
    
    if len(oc) == 0:
	return ObjectContainer(header=L("Empty"), message=L('No content found.'))
    else:
	return oc

####################################################################################################
def NewsSortMenu(title1, title2, url):
    oc = ObjectContainer(title1=title1, title2=title2)
    for option in ['Featured', 'Most Popular', 'Most Recent']:
	oc.add(DirectoryObject(key=Callback(NewsMenu, title1=title1, title2=title2, url=url,
	    sort_type=option.replace(' ', '')), title=option))
    return oc

####################################################################################################
def NewsMenu(title1, title2, url, sort_type=None, page=1, categories=[]):
    oc = ObjectContainer(title1=title1, title2=title2)
    data_url = BASE_URL + url + '?page=' + str(page)
    if sort_type:
	data_url = data_url + '&sort=' + sort_type
    data = HTML.ElementFromURL(data_url)
    if page == 1:
	subcategories = data.xpath('//div[@id="catnav"]//a')
	new_categories = [subcategory.text for subcategory in subcategories]
	for subcategory in subcategories:
	    url = subcategory.get('href')
	    name = subcategory.text
	    if name not in categories:
		oc.add(DirectoryObject(key=Callback(NewsMenu, title1=title2, title2=name, url=url, sort_type=sort_type, page=page, categories=new_categories), title=name))
	    else:
		pass
    else:
	pass
    
    for clip in data.xpath('//div[@class="clips"]//div[contains(@class, "clip col")]'):
	clip_url = BASE_URL + clip.xpath('.//a')[0].get('href')
	title = clip.xpath('.//img')[0].get('alt')
	thumb = clip.xpath('.//img')[0].get('src')
	try:
	    date = Datetime.ParseDate(clip.xpath('.//span[@class="date"]')[0].text).date()
	except:
	    date=None
	try:
	    runtime = clip.xpath('.//span[@class="length"]')[0].text.split(':')
	    if len(runtime) == 3:
		duration = ((int(runtime[0])*60 + int(runtime[1]))*60 + int(runtime[2]))*1000
	    elif len(runtime) == 2:
	        duration = (int(runtime.split(':')[0])*60 + int(runtime.split(':')[1]))*1000
	    else:
	        duration = int(runtime[0])*1000
	except:
	    duration = None
	summary = clip.xpath('.//span[@class="desc"]')[0].text
	oc.add(VideoClipObject(url=clip_url, title=title, summary=summary, duration=duration, originally_available_at=date,
	    thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    
    try:
	total_pages = int(data.xpath('//span[@class="totalpages"]')[0].text)
    except:
	total_pages = 1
    if total_pages > page:
	page = page+1
	oc.add(DirectoryObject(key=Callback(NewsMenu, title1=title2, title2="Page %s" % page, url=url, sort_type=sort_type, page=page), title='More'))
    
    if len(oc) == 0:
	return ObjectContainer(header=L("Empty"), message=L('No content found.'))
    else:
	return oc
    
####################################################################################################
def VideoMenu(id, title1=None, title2=None):
    oc = ObjectContainer()
    if title1:
	oc.title1=title1
    if title2:
	oc.title2=title2
    data = JSON.ObjectFromURL(VIDEOS_LIST % id)
    for item in data['items']:
	title = item['title']
	summary = item['description']
	duration = int(item['length'])
	date = int(item['airdate'])/1000
	Log(date)
	date = Datetime.FromTimestamp(date).date()
	thumbs = sorted(item['assets'], key = lambda thumb: int(thumb["height"]), reverse=True)
	id = item['ID']
	oc.add(VideoClipObject(url=PLAYER_URL % id, title=title, summary=summary, originally_available_at=date,
	    thumb=Resource.ContentsOfURLWithFallback(url=[thumb['URL'] for thumb in thumbs], fallback=ICON)))
    
    if len(oc) == 0:
	return ObjectContainer(header=L("Empty"), message=L('No content found.'))
    else:
	return oc

####################################################################################################
'''
def NewsMenu(sender):
	url = 'http://www.cbc.ca/thenational/watch/'
	dir = MediaContainer(title2="News")
	dir.Append(WebVideoItem(url,L('TheNationalTitle'), subtitle=L('TheNationalSubtitle'), summary=L('TheNationalSummary'), duration="3600000", thumb=R('the_national_program.jpg')))
	dir.Append(Function(DirectoryItem(GetRSS,L('OnDemandTitle'),subtitle="",summary=L('OnDemandSummary'),thumb=R('bg-yourNational.jpg'),art=R(ART),),show="NoD", title2=L('OnDemandTitle')))
	dir.Append(Function(DirectoryItem(GetRSS,L('AtIssueTitle'),subtitle="",summary=L('AtIssueSummary'),thumb=R('atissue.png'),art=R(ART),),show="AtIssue", title2=L('AtIssueTitle')))
	dir.Append(Function(DirectoryItem(GetRSS,L('RexMurphyTitle'),subtitle="",summary=L('RexMurphySummary'),thumb=R('rexmurphy.jpg'),art=R(ART),),show="RexMurphy", title2=L('RexMurphyTitle')))
	dir.Append(Function(DirectoryItem(GetClips,L('NewsRecent'),subtitle="",summary=L('NewsRecentSummary'),thumb=R(ICON),art=R(ART),),category="News", arrange="airdate", title2=L('Latest')))
	dir.Append(Function(DirectoryItem(GetClips,title=L('NewsPopular'),summary=L('NewsPopularSummary'),thumb=R(ICON),art=R(ART),),category="News", arrange="requestCount", title2=L('MostWatched')))
	dir.Append(Function(DirectoryItem(LocalMenu,L('LocalMenu'),subtitle="",summary=L('NewsLocalSummary'),thumb=R(ICON),art=R(ART),),title2=L('ShowsMenu')))
	return dir
####################################################################################################

def SportsMenu(sender):
	dir = MediaContainer(title2="Sports")
	dir.Append(Function(DirectoryItem(ShowsMenu,L('LiveMenu'),subtitle="",summary=L('ShowsSummary'),thumb=R(ICON),art=R(ART),),level=2, title2=L('LiveMenu'),clipType="",category='Sports',showName='Live_Streaming'))
	dir.Append(Function(DirectoryItem(GetClips,L('SportsRecent'),subtitle="",summary=L('SportsRecentSummary'),thumb=R(ICON),art=R(ART),),category="Sports", arrange="airdate", title2=L('Latest')))
	dir.Append(Function(DirectoryItem(GetClips,title=L('SportsPopular'),summary=L('SportsPopularSummary'),thumb=R(ICON),art=R(ART),),category="Sports", arrange="requestCount", title2=L('MostWatched')))
	dir.Append(Function(DirectoryItem(ShowsMenu,L('HNICMenu'),subtitle="",summary=L('HNICSummary'),thumb=R(ICON),art=R(ART),),level=2, title2=L('HNICMenu'),clipType="",category='Shows',showName='HNIC', maxClips='500'))
	return dir

####################################################################################################

def ShowsMenu(sender, level, title2, showName="",category='Shows', currentPage=0, clipType="",maxClips="",subtitle=""):
	dir = MediaContainer(title2=title2)
	if level == 1:
		cbcJson = JSON.ObjectFromURL(SHOWSLIST, cacheTime=600)['items']
		#Log(cbcJson)
		level=int(level)
		for show in cbcJson:
			title = show['title']
			clipType = show['customData'][1]['value']
			if show['customData'][0]['value'] != "":
				maxClips = show['customData'][0]['value']
			else:
				maxClips = 500	
			if show['title'] in SHOWEXCEPTIONS:
				showName = String.Quote(SHOWEXCEPTIONS[show['title']], usePlus=False)
			elif show['title'] == 'Holiday Guide' or show['title'] == 'More Shows':
				continue
			else:
				showName = String.Quote(show['title'], usePlus=False)
			dir.Append(Function(DirectoryItem(ShowsMenu,title=title,thumb=R(ICON),art=R(ART),), level=level+1, title2=title, showName=showName,clipType=clipType, maxClips=maxClips))
	elif level == 2:
		epUrl = GetEpisodesUrl(showName, clipType, maxClips)
		cbcData = JSON.ObjectFromURL(epUrl, cacheTime=600)
		cbcJson = cbcData['items']
		level=int(level)
		total = cbcData['listInfo']['itemCount'] - 1
		pages = total // 20
		remainder = (total % 20)
		if (remainder) == 0:
			pages = pages-1
		pageStart = (currentPage * 20)
		if (pageStart + 19) > total:
			pageEnd = pageStart + remainder + 1
		else:
			pageEnd = int(pageStart + 20)
		cbcJsonCurrPage = cbcJson[pageStart:pageEnd]
		for show in cbcJsonCurrPage:
			if String.Unquote(showName, usePlus=False) in SHOWEXCEPTIONS_REV:
				showName = String.Quote(SHOWEXCEPTIONS_REV[String.Unquote(showName, usePlus=False)], usePlus=False)
			title = show['title']
			url = WATCHURL % (category + '/' + showName.replace('%20','_')) + str(show['ID'])
			length = show['length']
			summary = show['description']
			if showName == 'Live_Streaming':
				airdate = int(show['airdate']) / 1000
				if airdate < time.time():
					subtitle = 'Streaming Live Now!'
					summary = summary + '\n\nStreaming Live Now!'
				else:
					airdate = time.localtime(airdate)
					airdate = time.strftime('%A, %B %d, %Y at %I:%M %p',airdate)
					subtitle = 'Streams live on ' + airdate
					summary = summary + '\n\nStreams live on ' + airdate
			thumb = show['thumbnailURL']
			dir.Append(VideoItem(Route(PlayVideo, url=url), title=title, summary=summary, duration=length, subtitle=subtitle, thumb=thumb))
		if currentPage < pages:
			if String.Unquote(showName, usePlus=False) in SHOWEXCEPTIONS:
				showName = String.Quote(SHOWEXCEPTIONS[String.Unquote(showName, usePlus=False)], usePlus=False)
			dir.Append(Function(DirectoryItem(ShowsMenu,title=L('NextPage'),summary=L('NextPageSummary'),thumb=R(ICON),art=R(ART),),level=2, title2=title2, showName=showName, currentPage=currentPage+1,clipType=clipType, maxClips=maxClips))
	return dir

####################################################################################################

def GetClips(sender, category, arrange, title2, currentPage=0):
	cbcData = JSON.ObjectFromURL(CLIPSURL % (CATEGORY_LIST[category], arrange), cacheTime=600)
	cbcJson = cbcData['items']
	total = cbcData['listInfo']['itemCount'] - 1
	pages = total // 20
	if (total % 20) == 0:
		pages = pages-1
	else:
		remainder = (total % 20)
	pageStart = (currentPage * 20)
	if (pageStart + 19) > total:
		pageEnd = int(pageStart + remainder)
	else:
		pageEnd = int(pageStart + 20)
	cbcJsonCurrPage = cbcJson[pageStart:pageEnd]
	dir = MediaContainer(title1=category,title2=title2)
	for clip in cbcJsonCurrPage:
		title = clip['title']
		url = WATCHURL % category + str(clip['ID'])
		length = clip['length']
		summary = clip['description']
		thumb = clip['thumbnailURL']
		dir.Append(WebVideoItem(url, title, summary=summary, thumb=thumb, duration=length))
	if currentPage < pages:
		dir.Append(Function(DirectoryItem(GetClips,title=L('NextPage'),summary="More %s Clips" % category,thumb=R(ICON),art=R(ART),),category=category,arrange=arrange, title2=title2, currentPage=currentPage+1))
	return dir

####################################################################################################

def GetRSS(sender, title2, show=""):
        if show == "NoD":
                dataURL = "http://www.cbc.ca/podcasting/includes/thenational-video-podcast.xml"
                thumb = R('bg-yourNational.jpg')
        elif show == "AtIssue":
                dataURL = "http://www.cbc.ca/mediafeeds/rss/cbc/atissue-video-podcast.xml"
                thumb = R('atissue.png')
        elif show == "RexMurphy":
                dataURL = "http://www.cbc.ca/mediafeeds/rss/cbc/rexmurphy-video-podcast.xml"
                thumb = R('rexmurphy.jpg')
        cbcRSS = XML.ElementFromURL(dataURL, cacheTime=600).xpath('/rss/channel/item')
        dir = MediaContainer(title2=title2)
        for clip in cbcRSS:
                title = clip.xpath('./title')[0].text
                summary = clip.xpath('./itunes:summary', namespaces={'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'})[0].text
                url = clip.xpath('./link')[0].text
                length = clip.xpath('./itunes:duration', namespaces={'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'})[0].text
                length = int(length) * 1000
                dir.Append(VideoItem(url, title, thumb=thumb, summary=summary, duration=length))
        return dir

####################################################################################################

def GetEpisodesUrl(showName, clipType, maxClips='500'):
	query = 'ContentCustomText|Show|' + showName
	if showName == 'HNIC':
		query = 'CategoryIDs|1245861901'
		url = SHOWSURL % (query, maxClips)
	elif showName == 'Live_Streaming':
		url = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=title&field=PID&field=ID&field=description&field=categoryIDs&field=thumbnailURL&field=URL&field=added&field=airdate&field=expirationDate&field=length&field=Keywords&contentCustomField=backgroundImage&contentCustomField=show&contentCustomField=relatedURL1&contentCustomField=relatedURL2&contentCustomField=relatedURL3&contentCustomField=sport&contentCustomField=seasonNumber&contentCustomField=clipType&contentCustomField=segment&contentCustomField=event&contentCustomField=adCategory&contentCustomField=LiveOnDemand&contentCustomField=AudioVideo&contentCustomField=EpisodeNumber&contentCustomField=RelatedClips&contentCustomField=Genre&contentCustomField=CommentsEnabled&contentCustomField=CommentsExpirationDate&query=CategoryIDs|1248955900&sortField=airdate&endIndex=500'
	else:
		if clipType == "Full Program":
			query = query + '&query=ContentCustomText|ClipType|' + String.Quote(clipType, usePlus=False)
		url = SHOWSURL % (query, maxClips)
	return url

####################################################################################################

@route('/video/cbc/v/p')
def PlayVideo(url):
    return Redirect(WebVideoItem(url))

####################################################################################################

def LocalMenu(sender, title2, showName="",category="", currentPage=0, clipType="",maxClips="",subtitle=""):
	dir = MediaContainer(title2=title2)
	cbcJson = JSON.ObjectFromURL(LOCALLIST, cacheTime=600)['items']
	for show in cbcJson:
		title = show['title']
		summary = show['description']
		clipType = show['customData'][1]['value']
		if show['customData'][0]['value'] != "":
			maxClips = show['customData'][0]['value']
		else:
			maxClips = 500	
		showName = String.Quote(show['title'], usePlus=False)
		dir.Append(Function(DirectoryItem(GetClips,title=title,subtitle="",summary=L('NewsLocalSummary'),thumb=R(ICON),art=R(ART),),category=title, arrange="airdate", title2=L('Latest')))
	return dir
'''