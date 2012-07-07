####################################################################################################
#CBC.CA Video Plugin
#Written by mysciencefriend
#Overhauled and updated by Mikedm139
#Use at your own risk, etc. etc.

VIDEO_PREFIX = '/video/cbc'
NAME = 'CBC'

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

MORE_SHOWS = '1329813962'

SHOWS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|%s'
VIDEOS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&query=CategoryIDs|%s&sortDescending=true&endIndex=500'
BASE_URL = 'http://www.cbc.ca'
PLAYER_URL = BASE_URL + '/player/%s/' 

CATEGORIES = ['News', 'Sports', 'Digital Archives']

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

####################################################################################################
def VideoMainMenu():
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(ShowCategories), title='Shows'))
    for category in CATEGORIES:
	oc.add(DirectoryObject(key=Callback(NewsCategories, category=category), title=category))
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.cbcnewsnetwork", title="Search", summary="Search CBC videos", prompt="Search for...",
        thumb=R(ICON), art=R(ART)))
    return oc

####################################################################################################
def ShowCategories():
    oc = ObjectContainer(title2='Shows')
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
	id = item['ID']
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
	if name == 'Local News':
	    url = url.replace('Local+News', 'Canada')
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
    if title2 == 'Local News':
	return oc
    
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
	try:
	    summary = clip.xpath('.//span[@class="desc"]')[0].text
	except:
	    summary = ''
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
	date = Datetime.FromTimestamp(date).date()
	thumbs = sorted(item['assets'], key = lambda thumb: int(thumb["height"]), reverse=True)
	id = item['ID']
	oc.add(VideoClipObject(url=PLAYER_URL % id, title=title, summary=summary, originally_available_at=date,
	    thumb=Resource.ContentsOfURLWithFallback(url=[thumb['URL'] for thumb in thumbs], fallback=ICON)))
    
    if len(oc) == 0:
	return ObjectContainer(header=L("Empty"), message=L('No content found.'))
    else:
	return oc
