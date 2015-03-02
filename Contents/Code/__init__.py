####################################################################################################
#CBC.CA Video Plugin
#Written by mysciencefriend
#Overhauled and updated by Mikedm139
#Use at your own risk, etc. etc.

ART  = 'art-default.jpg'
ICON = 'icon-default.jpg'

MORE_SHOWS = '1329813962'

SHOWS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&field=ID&field=title&field=parentID&field=description&customField=MaxClips&customField=ClipType&query=ParentIDs|%s'
VIDEOS_LIST = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij&query=CategoryIDs|%s&sortDescending=true&endIndex=500'
BASE_URL = 'http://www.cbc.ca'
PLAYER_URL = BASE_URL + '/player/%s/' 

CATEGORIES = ['News', 'Sports', 'Digital Archives']

####################################################################################################
def Start():

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'CBC'
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/cbc', 'CBC', art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(ShowCategories), title='Shows'))

    for category in CATEGORIES:

        oc.add(DirectoryObject(
            key = Callback(NewsCategories, category=category),
            title = category
        ))

    oc.add(SearchDirectoryObject(
        identifier = 'com.plexapp.plugins.cbcnewsnetwork',
        title = 'Search',
        summary = 'Search CBC videos',
        prompt = 'Search for...'
    ))

    return oc

####################################################################################################
@route('/video/cbc/category')
def ShowCategories():

    oc = ObjectContainer(title2='Shows')
    data = HTML.ElementFromURL(PLAYER_URL % 'Shows')
    categories = data.xpath('//div[@id="catnav"]//a[@class="haschildren"]')

    for category in categories:

        title = category.text
        cat_id = category.xpath('./parent::li/@data-id')[0]

        oc.add(DirectoryObject(
            key = Callback(ShowsMenu, id=cat_id, title2=title),
            title = title
        ))

    return oc

####################################################################################################
@route('/video/cbc/show')
def ShowsMenu(id, title1='', title2=''):

    oc = ObjectContainer()

    if title1 != '':
        oc.title1 = title1

    if title2 != '':
        oc.title2 = title2

    data = JSON.ObjectFromURL(SHOWS_LIST % id)

    if data['listInfo']['itemCount'] < 1:
        return VideoMenu(id, title1, title2)

    for item in data['items']:

        title = item['title']
        id = item['ID']

        oc.add(DirectoryObject(
            key = Callback(ShowsMenu, id=id, title1=title2, title2=title),
            title = title
        ))

    oc.objects.sort(key = lambda obj: obj.title)

    if title2 == 'Shows':

        oc.add(DirectoryObject(
            key = Callback(ShowsMenu, id=MORE_SHOWS, title2='More Shows'),
            title = 'More Shows'
        ))

    return oc

####################################################################################################
@route('/video/cbc/news/category')
def NewsCategories(category):

    oc = ObjectContainer(title2=category)
    data = HTML.ElementFromURL(PLAYER_URL % String.Quote(category, usePlus=True))

    for item in data.xpath('//div[@id="catnav"]//a'):

        url = item.get('href')
        name = item.text

        if name == 'Local News':
            url = url.replace('Local+News', 'Canada')

        oc.add(DirectoryObject(
            key = Callback(NewsSortMenu, title1=category, title2=name, url=url),
            title = name
         ))

    if len(oc) < 1:
        return ObjectContainer(header='Empty', message='No content found.')
    else:
        return oc

####################################################################################################
@route('/video/cbc/news/sort')
def NewsSortMenu(title1, title2, url):

    oc = ObjectContainer(title1=title1, title2=title2)

    for option in ['Featured', 'Most Popular', 'Most Recent']:

        oc.add(DirectoryObject(
            key = Callback(NewsMenu, title1=title1, title2=title2, url=url, sort_type=option.replace(' ', '')),
            title = option
        ))

    return oc

####################################################################################################
@route('/video/cbc/news', page=int, categories=list)
def NewsMenu(title1, title2, url, sort_type='', page=1, categories=[]):

    oc = ObjectContainer(title1=title1, title2=title2)
    data_url = BASE_URL + url + '?page=' + str(page)

    if sort_type != '':
        data_url = data_url + '&sort=' + sort_type

    data = HTML.ElementFromURL(data_url)

    if page == 1:

        subcategories = data.xpath('//div[@id="catnav"]//a')
        new_categories = [subcategory.text for subcategory in subcategories]

        for subcategory in subcategories:

            url = subcategory.get('href')
            name = subcategory.text

            if name not in categories:

                oc.add(DirectoryObject(
                    key = Callback(NewsMenu, title1=title2, title2=name, url=url, sort_type=sort_type, page=page, categories=new_categories),
                    title = name
                ))

    if title2 == 'Local News':
        return oc

    for clip in data.xpath('//div[@class="clips"]//div[contains(@class, "clip col")]'):

        clip_url = BASE_URL + clip.xpath('.//a/@href')[0]
        title = clip.xpath('.//img/@alt')[0]
        thumb = clip.xpath('.//img/@src')[0]

        try:
            date = Datetime.ParseDate(clip.xpath('.//span[@class="date"]/text()')[0]).date()
        except:
            date = None

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
            summary = clip.xpath('.//span[@class="desc"]/text()')[0]
        except:
            summary = None

        oc.add(VideoClipObject(
            url = clip_url,
            title = title,
            summary = summary,
            duration = duration,
            originally_available_at = date,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
        ))

    try:
        total_pages = int(data.xpath('//span[@class="totalpages"]/text()')[0])
    except:
        total_pages = 1

    if total_pages > page:

        page = page+1
        oc.add(DirectoryObject(
            key = Callback(NewsMenu, title1=title2, title2="Page %s" % page, url=url, sort_type=sort_type, page=page),
            title='More'
        ))

    if len(oc) < 1:
        return ObjectContainer(header='Empty', message='No content found.')
    else:
        return oc

####################################################################################################
@route('/video/cbc/video')
def VideoMenu(id, title1='', title2=''):

    oc = ObjectContainer()

    if title1 != '':
        oc.title1 = title1

    if title2 != '':
        oc.title2 = title2

    data = JSON.ObjectFromURL(VIDEOS_LIST % id)
    titles = {}

    for item in data['items']:

        title = item['title']
        summary = item['description']
        duration = int(item['length'])
        date = int(item['airdate'])/1000
        date = Datetime.FromTimestamp(date).date()
        thumbs = sorted(item['assets'], key = lambda thumb: int(thumb['height']), reverse=True)
        id = str(item['ID'])

        if title in titles:
            titles[title]['ids'].append(id)
            titles[title]['ids'].sort

        else:
            titles[title] = {
                'title': title,
                'summary': summary,
                'duration': duration,
                'date': date,
                'thumbs': thumbs,
                'ids': [id]
            }

    for title in titles:

        video = titles[title]

        oc.add(VideoClipObject(
            url = PLAYER_URL % ('Shows/ID/'+ video['ids'][-1]),
            title = video['title'],
            summary = video['summary'],
            originally_available_at = video['date'],
            thumb = Resource.ContentsOfURLWithFallback(url=[thumb['URL'] for thumb in video['thumbs']], fallback=ICON)
        ))

    if len(oc) < 1:
        return ObjectContainer(header='Empty', message='No content found.')
    else:
        oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)
        return oc
