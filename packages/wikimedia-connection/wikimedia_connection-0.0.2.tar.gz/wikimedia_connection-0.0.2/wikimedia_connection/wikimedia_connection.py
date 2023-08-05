# coding=utf-8
# download prefix in functions means that the function will inevitably attempt to download
# get prefix means that it will try to use cache before downloading

import os.path
import re
import json
import urllib.request, urllib.error, urllib.parse
import http
import socket
import hashlib
import time
import errno
import osm_handling_config

def wikidata_url(wikidata_id):
    return "https://www.wikidata.org/wiki/" + wikidata_id

def wikipedia_url(language_code, article_name):
    return "https://" + language_code + ".wikipedia.org/wiki/" + urllib.parse.quote(article_name)

class UrlResponse:
    def __init__(self, content, code):
        self.content = content
        self.code = code

class UnableToCacheData(Exception):
   pass

class FatalInternalIssueDoNotRetry(Exception):
   pass

class TitleViolatesKnownLimits(ValueError):
   pass

def download(url, timeout=360):
    retry_count = 0
    while True:
        try:
            print("downloading " + url)
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': osm_handling_config.get_user_agent()
                }
            )
            f = urllib.request.urlopen(url, timeout=timeout)
            return UrlResponse(f.read(), f.getcode())
        except socket.timeout as e:
            print(("socket.timeout " + url))
            print(e)
            print("retry_count: ", str(retry_count))
            retry_count += 1
            time.sleep(retry_count)
            if retry_count > 20:
                return UrlResponse(b'', 404)
            continue        
        except urllib.error.HTTPError as e:
            return UrlResponse(b'', e.getcode())
        except urllib.error.URLError as e:
            print(("no response from server for url " + url))
            print(e)
            print("retry_count: ", str(retry_count))
            retry_count += 1
            time.sleep(retry_count)
            if retry_count > 20:
                return UrlResponse(b'', 404)
            continue
        except http.client.RemoteDisconnected as e:
            print(("http.client.RemoteDisconnected for url " + url))
            print(e)
            print("retry_count: ", str(retry_count))
            retry_count += 1
            time.sleep(retry_count)
            if retry_count > 20:
                return UrlResponse(b'', 404)
            continue

def interwiki_language_codes():
    # TODO
    # should use https://stackoverflow.com/questions/33608751/retrieve-a-list-of-all-wikipedia-languages-programmatically
    # - maybe in tests only and hardcode otherwise?
    # see /home/mateusz/Documents/install_moje/OSM software/wikibrain_py_package_published/wikibrain/wikipedia_knowledge.py for more
    # that maybe also should use that new code, at least in tests
    return ['en', 'de', 'fr', 'nl', 'ru', 'it', 'es', 'pl',
                'vi', 'ja', 'pt', 'zh', 'uk', 'fa', 'ca', 'ar', 'no', 'sh', 'fi',
                'hu', 'id', 'ko', 'cs', 'ro', 'sr', 'ms', 'tr', 'eu', 'eo', 'bg',
                'hy', 'da', 'zh-min-nan', 'sk', 'min', 'kk', 'he', 'lt', 'hr',
                'ce', 'et', 'sl', 'be', 'gl', 'el', 'nn', 'uz', 'simple', 'la',
                'az', 'ur', 'hi', 'vo', 'th', 'ka', 'ta', 'cy', 'mk', 'mg', 'oc',
                'tl', 'ky', 'lv', 'bs', 'tt', 'new', 'sq', 'tg', 'te', 'pms',
                'br', 'be-tarask', 'zh-yue', 'bn', 'ml', 'ht', 'ast', 'lb', 'jv',
                'mr', 'azb', 'af', 'sco', 'pnb', 'ga', 'is', 'cv', 'ba', 'fy',
                'su', 'sw', 'my', 'lmo', 'an', 'yo', 'ne', 'gu', 'io', 'pa',
                'nds', 'scn', 'bpy', 'als', 'bar', 'ku', 'kn', 'ia', 'qu', 'ckb',
                'mn', 'arz', 'bat-smg', 'wa', 'gd', 'nap', 'bug', 'yi', 'am',
                'si', 'cdo', 'map-bms', 'or', 'fo', 'mzn', 'hsb', 'xmf', 'li',
                'mai', 'sah', 'sa', 'vec', 'ilo', 'os', 'mrj', 'hif', 'mhr', 'bh',
                'roa-tara', 'eml', 'diq', 'pam', 'ps', 'sd', 'hak', 'nso', 'se',
                'ace', 'bcl', 'mi', 'nah', 'zh-classical', 'nds-nl', 'szl', 'gan',
                'vls', 'rue', 'wuu', 'bo', 'glk', 'vep', 'sc', 'fiu-vro', 'frr',
                'co', 'crh', 'km', 'lrc', 'tk', 'kv', 'csb', 'so', 'gv', 'as',
                'lad', 'zea', 'ay', 'udm', 'myv', 'lez', 'kw', 'stq', 'ie',
                'nrm', 'nv', 'pcd', 'mwl', 'rm', 'koi', 'gom', 'ug', 'lij', 'ab',
                'gn', 'mt', 'fur', 'dsb', 'cbk-zam', 'dv', 'ang', 'ln', 'ext',
                'kab', 'sn', 'ksh', 'lo', 'gag', 'frp', 'pag', 'pi', 'olo', 'av',
                'dty', 'xal', 'pfl', 'krc', 'haw', 'bxr', 'kaa', 'pap', 'rw',
                'pdc', 'bjn', 'to', 'nov', 'kl', 'arc', 'jam', 'kbd', 'ha', 'tpi',
                'tyv', 'tet', 'ig', 'ki', 'na', 'lbe', 'roa-rup', 'jbo', 'ty',
                'mdf', 'kg', 'za', 'wo', 'lg', 'bi', 'srn', 'zu', 'chr', 'tcy',
                'ltg', 'sm', 'om', 'xh', 'tn', 'pih', 'chy', 'rmy', 'tw', 'cu',
                'kbp', 'tum', 'ts', 'st', 'got', 'rn', 'pnt', 'ss', 'fj', 'bm',
                'ch', 'ady', 'iu', 'mo', 'ny', 'ee', 'ks', 'ak', 'ik', 've', 'sg',
                'dz', 'ff', 'ti', 'cr', 'atj', 'din', 'ng', 'cho', 'kj', 'mh',
                'ho', 'ii', 'aa', 'mus', 'hz', 'kr',
                'ceb', 'sv', 'war'
                ]

def get_from_wikipedia_api(language_code, what, article_name, forced_refresh=False):
    # note that invalid article_name may cause issues
    # uk:title at ruwiki will be intereted specially, returning interwiki rather "page is not existing here"
    # it will happen for example with
    # wikipedia:ru=uk:title
    # triggering https://ru.wikipedia.org/w/api.php?action=query&format=json&redirects=&titles=uk%3A%D0%92%D0%BE%D0%BB%D0%BE%D0%B4%D1%8C%D0%BA%D0%BE%D0%B2%D0%B0%20%D0%94%D1%96%D0%B2%D0%B8%D1%86%D1%8F
    # what results in a crash here
    # for now it is not handled as it happens with rare invalid data
    # see https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions)#Colons

    if ":" in article_name:
        for code in interwiki_language_codes():
            match = code + ":"
            if article_name.lower().find(match) == 0:
                error = "article_name <" + str(article_name) + "> has <" + match + ">  at beggining"
                error += "\nand : with interwiki code in front on it violates restrictions and triggers weird api responses"
                error += "\nsee https://en.wikipedia.org/wiki/Wikipedia:Naming_conventions_(technical_restrictions)#Colons"
                raise TitleViolatesKnownLimits(error)

    try:
        language_code = urllib.parse.quote(language_code)
        article_name = urllib.parse.quote(article_name)
        url = "https://" + language_code + ".wikipedia.org/w/api.php?action=query&format=json"+what+"&redirects=&titles=" + article_name
        wikidata_id = get_wikidata_object_id_from_article(language_code, article_name)
        if wikidata_id == None:
            wikidata_id = ""
        response_string = get_from_generic_url(url, forced_refresh, wikidata_id)
        if response_string == None:
            get_from_wikipedia_api_show_debug_on_failure(language_code, what, article_name)
            raise FatalInternalIssueDoNotRetry
        parsed_json = json.loads(response_string)
        try:
            query = parsed_json['query']
            if 'pages' not in query:
                raise TitleViolatesKnownLimits("title was <" + str(article_name) + "> at <" + language_code + "> language wiki. exact limits unknown, sorry - making this TODO. see get_from_wikipedia_api( comments")
            query = query['pages']
        except KeyError as e:
            print('unexpected content of the response!')
            print('query:')
            print(url)
            print('returned:')
            print(parsed_json)
            raise FatalInternalIssueDoNotRetry
        id = list(query)[0]
        data = query[id]
    except TypeError:
        get_from_wikipedia_api_show_debug_on_failure(language_code, what, article_name)
        raise FatalInternalIssueDoNotRetry
    except UnableToCacheData as my:
        print(my)
        raise FatalInternalIssueDoNotRetry
    return data

def get_from_wikipedia_api_show_debug_on_failure(language_code, what, article_name):
    print("language_code=<" + str(language_code) + "> what=<" + str(what) + "> article_name=<" + str(article_name) + ">")

def get_intro_from_wikipedia(language_code, article_name, requested_length=None):
    request = "&prop=extracts&exintro=&explaintext"
    if requested_length != None:
        request += "&exchars=" + str(requested_length)
    data = None
    try:
        data = get_from_wikipedia_api(language_code, request, article_name)
    except TitleViolatesKnownLimits:
        return None
    try:
        return data['extract']
    except KeyError:
        print(("Failed extract extraction for " + article_name + " on " + language_code))
        return None
    raise("unexpected")

def get_pageprops(language_code, article_name):
    request = "&prop=pageprops"
    data = None
    try:
        data = get_from_wikipedia_api(language_code, request, article_name)
    except TitleViolatesKnownLimits:
        return None
    try:
        return data['pageprops']
    except KeyError:
        print(("Failed pageprops extraction for " + article_name + " on " + language_code))
        return None
    raise("unexpected")

def get_image_from_wikipedia_article(language_code, article_name):
    page = get_pageprops(language_code, article_name)
    if page == None:
        return None
    filename_via_page_image =  None
    try:
        filename_via_page_image = "File:" + page['page_image']
    except KeyError:
        return None
    return filename_via_page_image

def get_wikidata_object_id_from_article(language_code, article_name, forced_refresh = False):
    if article_name == None:
        return None
    if isinstance(article_name, str) == False:
        print("get_wikidata_object_id_from_article got invalid data, article_name=<" + str(article_name) +"> (not a string)")
        assert False
    if isinstance(language_code, str) == False:
        print("get_wikidata_object_id_from_article got invalid data, language_code=<" + str(language_code) +"> (not a string)")
        assert False
    try:
        wikidata_entry = get_data_from_wikidata(language_code, article_name, forced_refresh)['entities']
        id = list(wikidata_entry)[0]
        if id == "-1":
            return None
        return id
    except KeyError:
        return None

def get_wikidata_object_id_from_link(link, forced_refresh = False):
    if link == None:
        raise ValueError("expected text, got<" + str(link)+ ">")
    language_code = get_language_code_from_link(link)
    article_name = get_article_name_from_link(link)
    return get_wikidata_object_id_from_article(language_code, article_name, forced_refresh)

def get_property_from_wikidata(wikidata_id, property, forced_refresh = False):
    wikidata = get_data_from_wikidata_by_id(wikidata_id, forced_refresh)
    try:
        return wikidata['entities'][wikidata_id]['claims'][property]
    except KeyError:
        return None

def get_interwiki_link(language_code, article_name, target_language_code, forced_refresh = False):
    wikidata_id = get_wikidata_object_id_from_article(language_code, article_name)
    if wikidata_id == None:
        return None
    wikidata = get_data_from_wikidata_by_id(wikidata_id, forced_refresh)
    try:
        return wikidata['entities'][wikidata_id]['sitelinks'][target_language_code+"wiki"]['title']
    except KeyError:
        return None

def get_image_from_wikidata(wikidata_id):
    data = get_property_from_wikidata(wikidata_id, 'P18')
    if data == None:
        return None
    data = data[0]['mainsnak']
    if data['datatype'] != 'commonsMedia':
        print(("unexpected datatype for " + wikidata_id + " - " + datatype))
        return None
    return "File:"+data['datavalue']['value'].replace(" ", "_")

def get_location_from_wikidata(wikidata_id):
    data = get_property_from_wikidata(wikidata_id, 'P625')
    if data == None:
        return (None, None)
    data = data[0]['mainsnak']
    if data == None:
        return (None, None)
    data = data['datavalue']['value']
    return data['latitude'], data['longitude']

def get_text_before_first_colon(text):
    if text == None:
        raise ValueError("got None, expected text")
    try:
        parsed_link = re.match('([^:]*):(.*)', text)
        if parsed_link is None:
            return None
        return parsed_link.group(1)
    except TypeError:
        raise ValueError("expected text, got<" + str(text)+ ">")
        

def get_text_after_first_colon(text):
    if text == None:
        raise ValueError("got None, expected text")
    try:
        parsed_link = re.match('([^:]*):(.*)', text)
        if parsed_link is None:
            return None
        return parsed_link.group(2)
    except TypeError:
        raise ValueError("expected text, got<" + str(text)+ ">")

def get_language_code_from_link(link):
    if link == None:
        raise ValueError("expected text, got<" + str(link)+ ">")
    try:
        return get_text_before_first_colon(link)
    except ValueError as e:
        print(link, "triggered value error")
        raise e


def get_article_name_from_link(link):
    return get_text_after_first_colon(link)


def get_form_of_link_usable_as_filename(link):
    # (it depends on where cache folder is located probably, but it is a hack anyway)
    if len(link) > 220: #200 was enough, also with overhead, 300 extended with overhead to 330 and crashed 
        return text_to_hash(link) # superugly HACK
    link = link.replace("\"", "")
    link = link.replace("*", "")
    link = link.replace("\\", "")
    link = link.replace("/", "")
    link = link.replace("?", "")
    link = link.replace("<", "")
    link = link.replace(">", "")
    link = link.replace("|", "")
    return link

def get_form_of_link_usable_as_filename_without_data_loss(link):
    #TODO - on cache purge replace get_form_of_link_usable_as_filename by this
    #to ensure that extension (especially .code.txt) are going to work - othewise url ending on .code would cause problems
    link = link.replace(".", ".d.")

    link = link.replace("\"", ".q.")
    link = link.replace("*", ".st.")
    link = link.replace("\\", ".b.")
    link = link.replace("/", ".s.")
    link = link.replace("?", ".qe.")
    link = link.replace("<", ".l.")
    link = link.replace(">", ".g.")
    link = link.replace("|", ".p.")
    return link

def url_to_hash(url):
    print("url_to_hash is deprecated") # TODO eliminate
    return text_to_hash(url)

def text_to_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def set_cache_location(path):
    if path[-1] != "/":
        path += "/"
    global cache_location_store
    cache_location_store = path

def cache_location():
    assert cache_location_store != None, "wikimedia_connection.set_cache_location must be called before that point"
    return cache_location_store

def wikidata_language_placeholder():
    return 'wikidata_by_id'

def cache_folder_name():
    return 'wikimedia-connection-cache'

def get_filename_with_wikidata_entity_by_id(id):
    return os.path.join(cache_location(), cache_folder_name(), wikidata_language_placeholder(), get_form_of_link_usable_as_filename(id) + ".wikidata_entity.txt")

def get_filename_with_wikidata_by_id_response_code(id):
    return os.path.join(cache_location(), cache_folder_name(), wikidata_language_placeholder(), get_form_of_link_usable_as_filename(id) + ".wikidata_entity.code.txt")

def get_filename_with_wikidata_entity(language_code, article_name):
    return os.path.join(cache_location(), cache_folder_name(), language_code, get_form_of_link_usable_as_filename(article_name) + ".wikidata_entity.txt")

def get_filename_with_wikidata_response_code(language_code, article_name):
    return os.path.join(cache_location(), cache_folder_name(), language_code, get_form_of_link_usable_as_filename(article_name) + ".wikidata_entity.code.txt")

def get_filename_with_article(language_code, article_name):
    return os.path.join(cache_location(), cache_folder_name(), language_code, get_form_of_link_usable_as_filename(article_name) + ".txt")

def get_filename_with_wikipedia_response_code(language_code, article_name):
    return os.path.join(cache_location(), cache_folder_name(), language_code, get_form_of_link_usable_as_filename(article_name) + ".code.txt")

def write_to_text_file(filename, content):
    write_to_file(filename, content, 'w')

def write_to_binary_file(filename, content):
    write_to_file(filename, content, 'wb')

def write_to_file(filename, content, access_mode):
    try:
        specified_file = open(filename, access_mode)
        specified_file.write(content)
        specified_file.close()
    except OSError as exc:
        if exc.errno == errno.ENAMETOOLONG:
            error = "filename too long! Length was " + str(len(filename)) + " for <" + filename + ">"
            print(error)
            raise UnableToCacheData(error)
        raise

def ensure_that_cache_folder_exists(language_code):
    path = os.path.join(cache_location(), cache_folder_name(), language_code)
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def is_it_necessary_to_reload_files(content_filename, response_code_filename):
    if not os.path.isfile(content_filename) or not os.path.isfile(response_code_filename):
        return True
    else:
        files_need_reloading = False
        if get_entire_file_content(response_code_filename) == "":
            files_need_reloading = True
        return files_need_reloading
    return False

def get_data_from_cache_files(response_filename, response_code_filename):
    code_as_string = get_entire_file_content(response_code_filename)
    code = int(code_as_string)
    if code != 200:
        return None
    return get_entire_file_content(response_filename)

def get_entire_file_content(filename):
    try:
        file = open(filename, 'r')
        content = file.read()
        file.close()
    except UnicodeDecodeError as e:
        print("failed opening", filename, "due to UnicodeDecodeError")
        raise e
    return content

def download_data_from_wikipedia(language_code, article_name):
    ensure_that_cache_folder_exists(language_code)
    response_filename = get_filename_with_article(language_code, article_name)
    code_filename = get_filename_with_wikipedia_response_code(language_code, article_name)
    url = "https://" + urllib.parse.quote(language_code) + ".wikipedia.org/wiki/" + urllib.parse.quote(article_name)
    result = download(url)
    write_to_text_file(response_filename, str(result.content))
    write_to_text_file(code_filename, str(result.code))

def download_data_from_wikidata_by_id(wikidata_id):
    ensure_that_cache_folder_exists(wikidata_language_placeholder())
    response_filename = get_filename_with_wikidata_entity_by_id(wikidata_id)
    code_filename = get_filename_with_wikidata_by_id_response_code(wikidata_id)

    url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=" + urllib.parse.quote(wikidata_id) + "&format=json"
    result = download(url)
    content = str(result.content.decode())
    write_to_text_file(response_filename, content)
    write_to_text_file(code_filename, str(result.code))

def get_data_from_wikidata_by_id(wikidata_id, forced_refresh=False):
    if it_is_necessary_to_reload_wikidata_by_id_files(wikidata_id) or forced_refresh:
        download_data_from_wikidata_by_id(wikidata_id)
    response_filename = get_filename_with_wikidata_entity_by_id(wikidata_id)
    response_code_filename = get_filename_with_wikidata_by_id_response_code(wikidata_id)
    if not os.path.isfile(response_filename):
        print(it_is_necessary_to_reload_wikidata_by_id_files(wikidata_id))
        print(response_filename)
        assert False
    response = get_data_from_cache_files(response_filename, response_code_filename)
    if response == None:
        print("get_data_from_wikidata_by_id got None response, reload will be forced")
        download_data_from_wikidata_by_id(wikidata_id)
        return get_data_from_wikidata_by_id(wikidata_id)
    response = json.loads(response)
    if 'error' not in response:
        return response
    if response['error']['code'] == 'no-such-entity':
        return None
    raise NotImplementedError("unhandled error" + str(response))

def it_is_necessary_to_reload_wikidata_by_id_files(wikidata_id):
    content_filename = get_filename_with_wikidata_entity_by_id(wikidata_id)
    response_code_filename = get_filename_with_wikidata_by_id_response_code(wikidata_id)
    return is_it_necessary_to_reload_files(content_filename, response_code_filename)

def download_data_from_wikidata(language_code, article_name):
    ensure_that_cache_folder_exists(language_code)
    response_filename = get_filename_with_wikidata_entity(language_code, article_name)
    code_filename = get_filename_with_wikidata_response_code(language_code, article_name)

    url = "https://www.wikidata.org/w/api.php?action=wbgetentities&sites=" + urllib.parse.quote(language_code) + "wiki&titles=" + urllib.parse.quote(article_name) + "&format=json"
    result = download(url)
    content = str(result.content.decode())
    write_to_text_file(response_filename, content)
    write_to_text_file(code_filename, str(result.code))

def get_data_from_wikidata(language_code, article_name, forced_refresh):
    if it_is_necessary_to_reload_wikidata_files(language_code, article_name) or forced_refresh:
        download_data_from_wikidata(language_code, article_name)
    response_filename = get_filename_with_wikidata_entity(language_code, article_name)
    response_code_filename = get_filename_with_wikidata_response_code(language_code, article_name)
    if not os.path.isfile(response_filename):
        print(it_is_necessary_to_reload_wikidata_files(language_code, article_name))
        print(response_filename)
        assert False
    response = get_data_from_cache_files(response_filename, response_code_filename)
    if response == None:
        print("get_data_from_wikidata got None response, reload will be forced")
        download_data_from_wikidata(language_code, article_name)
        return get_data_from_wikidata(language_code, article_name, forced_refresh)
    return json.loads(response)


def it_is_necessary_to_reload_wikidata_files(language_code, article_name):
    content_filename = get_filename_with_wikidata_entity(language_code, article_name)
    response_code_filename = get_filename_with_wikidata_response_code(language_code, article_name)
    return is_it_necessary_to_reload_files(content_filename, response_code_filename)

def it_is_necessary_to_reload_wikipedia_files(language_code, article_name):
    content_filename = get_filename_with_article(language_code, article_name)
    response_code_filename = get_filename_with_wikipedia_response_code(language_code, article_name)
    return is_it_necessary_to_reload_files(content_filename, response_code_filename)

def get_wikipedia_page(language_code, article_name, forced_refresh):
    if it_is_necessary_to_reload_wikipedia_files(language_code, article_name) or forced_refresh:
        download_data_from_wikipedia(language_code, article_name)
    response_filename = get_filename_with_article(language_code, article_name)
    response_code_filename = get_filename_with_wikipedia_response_code(language_code, article_name)
    if not os.path.isfile(response_filename):
        print(it_is_necessary_to_reload_wikipedia_files(language_code, article_name))
        print(response_filename)
        assert False
    response = get_data_from_cache_files(response_filename, response_code_filename)
    return response

def get_filename_cache_for_url(url, identifier_hack):
    #HACK! but simply using get_form_of_link_usable_as_filename is not going to work as filename due to limit of filename length
    return os.path.join(cache_location(), cache_folder_name(), 'url', text_to_hash(url) + ":" + identifier_hack + ".txt")

def get_filename_cache_for_url_response_code(url, identifier_hack):
    return os.path.join(cache_location(), cache_folder_name(), 'url', text_to_hash(url) + ":" + identifier_hack + ".code.txt")

def it_is_necessary_to_reload_generic_url(url, identifier_hack):
    content_filename = get_filename_cache_for_url(url, identifier_hack)
    code_filename = get_filename_cache_for_url_response_code(url, identifier_hack)
    return is_it_necessary_to_reload_files(content_filename, code_filename)

def download_data_from_generic_url(url, identifier_hack):
    ensure_that_cache_folder_exists('url')
    response_filename = get_filename_cache_for_url(url, identifier_hack)
    code_filename = get_filename_cache_for_url_response_code(url, identifier_hack)
    result = download(url)
    write_to_text_file(response_filename, str(result.content.decode()))
    write_to_text_file(code_filename, str(result.code))

def get_from_generic_url(url, forced_refresh=False, identifier_hack=""):
    if it_is_necessary_to_reload_generic_url(url, identifier_hack) or forced_refresh:
        download_data_from_generic_url(url, identifier_hack)
    response_filename = get_filename_cache_for_url(url, identifier_hack)
    code_filename = get_filename_cache_for_url_response_code(url, identifier_hack)
    if not os.path.isfile(response_filename):
        print(it_is_necessary_to_reload_generic_url(url, identifier_hack))
        print(response_filename)
        print(url)
        print("impossible situation")
        assert False
    response = get_data_from_cache_files(response_filename, code_filename)
    if response == None:
        print(response_filename)
        print(code_filename)
        assert False
    return response

def get_interwiki_article_name_by_id(wikidata_id, target_language, forced_refresh=False):
    if wikidata_id == None:
        return None
    if target_language == None:
        raise ValueError("null pointer exception, target_language==None")
    wikidata_entry = get_data_from_wikidata_by_id(wikidata_id, forced_refresh)
    return get_interwiki_article_name_from_wikidata_data(wikidata_entry, target_language)

def get_interwiki_article_name(source_language_code, source_article_name, target_language, forced_refresh=False):
    wikidata_entry = get_data_from_wikidata(source_language_code, source_article_name, forced_refresh)
    return get_interwiki_article_name_from_wikidata_data(wikidata_entry, target_language)

def get_interwiki_article_name_from_wikidata_data(wikidata_entry, target_language):
    if target_language == None:
        raise ValueError("null pointer exception")
    try:
        wikidata_entry = wikidata_entry['entities']
        id = list(wikidata_entry)[0]
        return wikidata_entry[id]['sitelinks'][target_language+'wiki']['title']
    except KeyError:
        return None
