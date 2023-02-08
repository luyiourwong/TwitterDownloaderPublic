from twitter import *
import time
import os
from os import system
import json
import sys
import traceback
import requests
import subprocess
import urllib

'''
Elevated access request
'''

# 公開版已移除API資訊，請自行向twitterAPI請求後填上
AUTH_API_KEY = ''
AUTH_API_KEYSECRET = ''
AUTH_BEARERTOKEN = ''
AUTH_ACCESS_TOKEN = ''
AUTH_ACCESS_TOKENSECRET = ''

# 公開版已移除網址
SPEC_USER = '**URL**'

DEFAULT_DOWNLOAD_FOLDER = "ArchTT"
DEFAULT_LOG_FILE = "logtt.txt"
DEFAULT_WAITING_TIME = 10
DEFAULT_LOG_COUNT = 16000
DEFAULT_SPITESYMBOL = "@"

'''
Main class
'''
class MainTtdl():
    def __init__(self):
        self.setup()
        self.loadTT()
        
    def setup(self):
        info('setup start')
        
        info('set outputpath to ' + str(DEFAULT_DOWNLOAD_FOLDER))
        self.directory = DEFAULT_DOWNLOAD_FOLDER + os.path.sep
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        self.t = Twitter(auth=OAuth(AUTH_ACCESS_TOKEN, AUTH_ACCESS_TOKENSECRET, AUTH_API_KEY, AUTH_API_KEYSECRET))
        info('setup finish')
        
    def gettimedir(self, localtime):
        timey = time.strftime('%Y', localtime)
        timem = time.strftime('%m', localtime)
        timed = time.strftime('%d', localtime)
        td = '00'
        if int(timed) >= 20:
            td = '20'
        elif int(timed) >= 10:
            td = '10'
        return self.directory + (str(timey) + '_' + str(timem) + '_' + str(td)) + os.path.sep
    
    def loadTT(self):
        info('loadTT start')
        #init
        self.listTT = []
        
        #load
        for dirpath,dirnames,filenames in os.walk(self.directory):
            for file in filenames:
                if not os.path.isdir(file):
                    if file.endswith('.json') and DEFAULT_SPITESYMBOL in file:
                        ttid = file.split(DEFAULT_SPITESYMBOL)[0]
                        self.listTT.append(ttid)
                    
        info('old TT count: ' + str(len(self.listTT)))
        info('loadTT finish')
    
    def run(self, user):
        #setup
        self.waittime = DEFAULT_WAITING_TIME
        
        #set user
        if user == '':
            user = SPEC_USER
            info('no requirement user, set to default')
        system("title " + user)
        info('start checking twitter: ' + user)
        
        #run
        while 1==1:
            self.checkTimeline(user)
            info('waiting ' + str(self.waittime) + ' second')
            time.sleep(self.waittime)
        
    def checkTimeline(self, user):
        #setup
        localtime = time.localtime()
        timenow = time.strftime('%Y-%m-%d-%H-%M-%S', localtime)
        
        new = False
        
        #check timeline
        info('[' + timenow + '] check twitter: ' + user)
        try:
            timeline = self.t.statuses.user_timeline(screen_name=user)
        except urllib.error.URLError:
            error('get URL error, retry')
            return
        except TwitterHTTPError:
            error('get Twitter error, retry')
            return
        except TimeoutError:
            error('get URL timeout, retry')
            return
        except:
            error('get timeline error, retry')
            return
        
        #get first tweet
        if timeline:
            for tweet in timeline:
                #check is new
                ttid = tweet['id_str']
                if ttid not in self.listTT:
                    new = True
                else:
                    info('no new tweet')
                    break
                
                #download if new
                if new:
                    new = False
                    dirpath = self.gettimedir(localtime)
                    if not os.path.exists(dirpath):
                        os.makedirs(dirpath)
                    
                    info('has new tweet, downloading ' + str(dirpath) + str(ttid))
                    self.saveTweetJson(tweet, ttid, timenow, dirpath)
                    self.saveTweetText(tweet, ttid, timenow, dirpath)
                    self.saveTweetMedia(tweet, ttid, timenow, dirpath)
                    self.saveTweetPhoto(tweet, ttid, timenow, dirpath)
                    self.saveTweetVideo(tweet, ttid, timenow, dirpath)
                    self.saveTweetSpace(tweet, ttid, timenow, dirpath)
        else:
            error('timeline null error')
            return
                
    
    def saveTweetJson(self, tweet, ttid, timenow, dirpath):
        filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + ".json"
        filepath = dirpath + filename
        try:
            with open(filepath, "w") as out_file:
                try:
                    json.dump(tweet, out_file, indent=4)
                except UnicodeEncodeError:
                    logstr = 'save json' + ' UnicodeEncode error, continue'
                    warning(logstr)
            self.listTT.append(ttid)
            logstr = 'save json: ' + str(ttid)
            info(logstr)
            outlog(logstr)
        except IOError:
            logstr = 'save json' + ' IO error, ' + traceback.format_exc()
            error(logstr)
            outlog(logstr)
            sys.exit('download error')
        except:
            logstr = 'save json' + ' unknown error, ' + traceback.format_exc()
            error(logstr)
            outlog(logstr)
            sys.exit('download error')
            
    def saveTweetText(self, tweet, ttid, timenow, dirpath):
        try:
            tttext = tweet['text']
            if tttext:
                filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + "_text" + ".txt"
                filepath = dirpath + filename
                try:
                    with open(filepath, "w", encoding='UTF-8') as out_file:
                        try:
                            out_file.write(str(tttext))
                        except UnicodeEncodeError:
                            logstr = 'save text' + ' UnicodeEncode error, continue'
                            warning(logstr)
                    logstr = 'save text: ' + str(ttid)
                    info(logstr)
                    outlog(logstr)
                except IOError:
                    logstr = 'save text' + ' IO error, ' + traceback.format_exc()
                    error(logstr)
                    outlog(logstr)
                    sys.exit('download error')
                except:
                    logstr = 'save text' + ' unknown error, ' + traceback.format_exc()
                    error(logstr)
                    outlog(logstr)
                    sys.exit('download error')
        except KeyError:
            pass
            
    def saveTweetMedia(self, tweet, ttid, timenow, dirpath):
        try:
            if tweet['entities']:
                medias = tweet['entities']['media']
                if medias:
                    count = 0
                    for media in medias:
                        mediaurl = media['media_url']
                        if mediaurl:
                            count += 1
                            ends = "jpg"
                            if mediaurl.endswith(".png"):
                                ends = "png"
                            filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + "_media_" + str(count) + "." + ends
                            filepath = dirpath + filename
                            try:
                                with open(filepath, "wb") as out_file:
                                    response = requests.get(mediaurl, stream=True)
                                    if not response.ok:
                                        print(response)
                                    for block in response.iter_content(1024):
                                        if not block:
                                            break
                                        out_file.write(block)
                                logstr = 'save media: ' + str(ttid)
                                info(logstr)
                                outlog(logstr)
                            except IOError:
                                logstr = 'save media' + ' IO error, ' + traceback.format_exc()
                                error(logstr)
                                outlog(logstr)
                                sys.exit('download error')
                            except:
                                logstr = 'save media' + ' unknown error, ' + traceback.format_exc()
                                error(logstr)
                                outlog(logstr)
                                sys.exit('download error')
        except KeyError:
            pass
            
    def saveTweetPhoto(self, tweet, ttid, timenow, dirpath):
        try:
            if tweet['extended_entities']:
                medias = tweet['extended_entities']['media']
                if medias:
                    count = 0
                    for media in medias:
                        mediaurl = media['media_url']
                        if mediaurl:
                            count += 1
                            ends = "jpg"
                            if mediaurl.endswith(".png"):
                                ends = "png"
                            largeurl = mediaurl.replace("." + ends, "?format=" + ends + "&name=large")
                            filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + "_photo_" + str(count) + "." + ends
                            filepath = dirpath + filename
                            try:
                                with open(filepath, "wb") as out_file:
                                    response = requests.get(largeurl, stream=True)
                                    if not response.ok:
                                        print(response)
                                    for block in response.iter_content(1024):
                                        if not block:
                                            break
                                        out_file.write(block)
                                logstr = 'save photo ' + str(count) + ':' + str(ttid)
                                info(logstr)
                                outlog(logstr)
                            except IOError:
                                logstr = 'save photo' + str(count) + ':' + ' IO error, ' + traceback.format_exc()
                                error(logstr)
                                outlog(logstr)
                                sys.exit('download error')
                            except:
                                logstr = 'save photo' + str(count) + ':' + ' unknown error, ' + traceback.format_exc()
                                error(logstr)
                                outlog(logstr)
                                sys.exit('download error')
        except KeyError:
            pass
            
    def saveTweetVideo(self, tweet, ttid, timenow, dirpath):
        try:
            if tweet['extended_entities']:
                medias = tweet['extended_entities']['media']
                if medias:
                    for media in medias:
                        if media['video_info']:
                            variants = media['video_info']['variants']
                            if variants:
                                for variant in variants:
                                    if 'video' in variant['content_type']:
                                        bitrate = variant['bitrate']
                                        mediaurl = variant['url']
                                        filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + "_video_" + str(bitrate) + ".mp4"
                                        filepath = dirpath + filename
                                        try:
                                            with open(filepath, "wb") as out_file:
                                                response = requests.get(mediaurl, stream=True)
                                                if not response.ok:
                                                    print(response)
                                                for block in response.iter_content(1024):
                                                    if not block:
                                                        break
                                                    out_file.write(block)
                                            logstr = 'save video in ' + str(bitrate) + ' :' + str(ttid)
                                            info(logstr)
                                            outlog(logstr)
                                        except IOError:
                                            logstr = 'save video' + ' IO error, ' + traceback.format_exc()
                                            error(logstr)
                                            outlog(logstr)
                                            sys.exit('download error')
                                        except:
                                            logstr = 'save video' + ' unknown error, ' + traceback.format_exc()
                                            error(logstr)
                                            outlog(logstr)
                                            sys.exit('download error')
        except KeyError:
            pass
            
    def saveTweetSpace(self, tweet, ttid, timenow, dirpath):
        try:
            if tweet['entities']:
                medias = tweet['entities']['urls']
                if medias:
                    for media in medias:
                        mediaurl = media['expanded_url']
                        if mediaurl:
                            if 'https://twitter.com/i/spaces' in mediaurl:
                                filename = str(ttid) + DEFAULT_SPITESYMBOL + str(timenow) + "_space"
                                filepath = dirpath + filename
                                
                                logstr = 'calling twspace-dl to downloading Space: ' + str(mediaurl)
                                info(logstr)
                                outlog(logstr)
                                
                                cmd = "twspace_dl -k -i " + str(mediaurl) + " -o " + filepath
                                subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                                
                                logstr = 'save Space:' + str(ttid)
                                info(logstr)
                                outlog(logstr)
        except KeyError:
            pass
        except:
            logstr = 'save Space' + ' unknown error, ' + traceback.format_exc()
            error(logstr)
            outlog(logstr)
            sys.exit('download error')
            
'''
LOG class
'''
def debug(msg):
    print('[debug] ' + msg)

def info(msg):
    print('[info] ' + msg)

def warning(msg):
    print('[warning] ' + msg)

def error(msg):
    print('[error] ' + msg)
    
def outlog(msg):
    timenow = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    try:
        filename = DEFAULT_LOG_FILE
        with open(filename, "a") as out_file:
            out_file.write('[' + timenow + ']' + msg + '\n')
    except IOError:
        error('IO error on log !!!')
        return

'''
entry
'''
if __name__ == '__main__':
    mainDl = MainTtdl()
    user = ''
    if len(sys.argv) > 1:
        user = sys.argv[1]
    mainDl.run(user)