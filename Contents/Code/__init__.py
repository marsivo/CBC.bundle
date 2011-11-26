import time

####################################################################################################
#Version 0.08
#CBC.CA Video Plugin
#Written by mysciencefriend - look me up on the plexapp.com forums for help
#Use at your own risk, etc. etc.

VIDEO_PREFIX = '/video/cbc'
NAME = 'CBC'

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

CATEGORY_LIST = {'News'		:	'1221258968',
				'Sports'	:	'1237510081',
				'BC'		:	'1317899897',
				'Calgary'	:	'1317901071',
				'Edmonton'	:	'1317901477',
				'Manitoba'	:	'1317902896',
				'Montreal'	:	'1317903731',
				'NB'		:	'1317906492',
				'NL'		:	'1317907201',
				'North'		:	'1317907460',
				'NS'		:	'1317909223',
				'Ottawa'	:	'1317910092',
				'PEI'		:	'1317910853',
				'Saskatchewan'	:	'1317911675',
				'Toronto'	:	'1317912017',
				'Windsor'	:	'1317913355'
				}

SHOWEXCEPTIONS = {'The Rick Mercer Report'				:	'Rick Mercer Report',
				'The Ron James Show'			:	'Ron James Show',
				'Hockey Night in Canada'		:	'HNIC',
				'Q on bold'				:	'Q',
				'George Stroumboulopoulos Tonight'	:	'George Tonight'
				}

SHOWEXCEPTIONS_REV = {'Rick Mercer Report'			:	'The Rick Mercer Report',
					'Ron James Show'	:	'The Ron James Show',
					'HNIC'			:	'Hockey Night in Canada',
					'Q'			:	'Q on bold',
					'George Tonight'	:	'George Stroumboulopoulos Tonight'
					}

SHOWSLIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|1221254309'
LOCALLIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|1244502941'
CLIPSURL = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&query=CategoryIDs|%s&sortField=%s&sortDescending=true&endIndex=500'
SHOWSURL = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=title&field=PID&field=ID&field=description&field=categoryIDs&field=thumbnailURL&field=URL&field=added&field=airdate&field=expirationDate&field=length&field=Keywords&query=%s&sortField=airdate&sortDescending=true&startIndex=1&endIndex=%s'
WATCHURL = 'http://www.cbc.ca/video/#/%s/ID='

SMIL_URL = 'http://link.theplatform.com/s/h9dtGB/zRoOKQ_cN9OQOikWISihO5bmV8zWB3Xs?isPLS=false&airdate=1301356800000&site=cbcentca&zone=little_mosque_on_the_prairie&shortClip=false&show=little_mosque_on_the_prairie&liveondemand=ondemand&type=full_program&season=5&format=SMIL&Tracking=true&Embedded=true'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = 'InfoList'
    DirectoryItem.thumb = R(ICON)

    HTTP.CacheTime = 1800

####################################################################################################

def VideoMainMenu():
	dir = MediaContainer()

	dir.Append(Function(DirectoryItem(NewsMenu,L('NewsMenu'),subtitle="",summary=L('NewsSummary'),thumb=R(ICON),art=R(ART))))
	dir.Append(Function(DirectoryItem(ShowsMenu,L('ShowsMenu'),subtitle="",summary=L('ShowsSummary'),thumb=R(ICON),art=R(ART),),level=1, title2=L('ShowsMenu')))
	dir.Append(Function(DirectoryItem(SportsMenu,L('SportsMenu'),subtitle="",summary=L('SportsSummary'),thumb=R(ICON),art=R(ART))))

	return dir

####################################################################################################

def NewsMenu(sender):
	url = 'http://www.cbc.ca/thenational/watch/'
	dir = MediaContainer(title2="News")
	dir.Append(WebVideoItem(url,L('TheNationalTitle'), subtitle=L('TheNationalSubtitle'), summary=L('TheNationalSummary'), duration="3600000", thumb=R('the_national_program.jpg')))
#	dir.Append(Function(DirectoryItem(GetRSS,L('OnDemandTitle'),subtitle="",summary=L('OnDemandSummary'),thumb=R('bg-yourNational.jpg'),art=R(ART),),show="NoD", title2=L('OnDemandTitle')))
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
