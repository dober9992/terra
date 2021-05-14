""" 
Descritption : Terra 2021 Twitter module  
Date : 14-May-2021
Author : Adhrit (github.com/xadhrit/terra)

"""

from datetime import date
import urllib
import sys
import json
import os
import codecs
from bs4 import BeautifulSoup
import twitter
import yaml
from rich.console import Console
from twitter.error import TwitterError 


pc = Console()


class Twitter:
    api = None
    user_id = None
    target_id = None
    verified = False
    following = False
    mentions = None
    target = ""
    writeFile = False
    jsonDump = False

    def __init__(self,target, is_file, is_json):
        self.check_creds()   
        self.setTarget(target)
        self.writeFile = is_file
        self.jsonDump = is_json
    
    
    def check_creds(self):
        try:
            file = "./creds/twitter.yml"
            if not os.path.isfile(file):
                pc.print(" Credentials 'yaml' File not Found", style='red')
                sys.exit(0)
            else:
                tokens = yaml.load(open('./creds/twitter.yml'), Loader=yaml.FullLoader)
                self.api = twitter.Api(consumer_key=tokens['creds']['API_Key'],consumer_secret=tokens['creds']['API_Secret_Key'],access_token_key=tokens['creds']['Access_Token'],access_token_secret=tokens['creds']['Access_Secret_Token'])
                pc.print("\nValidating Your Credentials...", style="green") 
        except Exception as error:
            pc.print(error, style='orange1')

    def setTarget(self, target):
        self.target = target
        user = self.get_user(target)
        self.target_id = user.id
        self.__printTarget__()
        
        
    def reset_target(self):
        pc.print("Enter new Target's username : ", style='bright_yellow')
        user_input = input()
        self.setTarget(user_input)
        return
    
    def __printTarget__(self):
        result = []
        result = self.api.VerifyCredentials()
        my_name = result.screen_name
        pc.print("Logged  as : ",  style="green", end='')
        pc.print(my_name,style='bright_white', end='')
        pc.print(" | Target :  ", style='red', end='')
        pc.print(self.target, style='bright_white', end='')
        pc.print(" | id : ", style='cyan', end='')
        pc.print(self.target_id, style='bright_cyan')
        self.check_following()
        return  
    
    
    def get_user(self, screen_name):
        try:
            content = self.api.GetUser(screen_name=self.target)
            
            if self.writeFile:
                file_name = "./results/twitter/" + self.target + ".txt"
                fp = open(file_name, "w")
                fp.write(str(content))
                fp.close()
            
            user = content     
            return user 
        except (TwitterError) as err:
            for m in err.message:
                for key in m:
                    pc.print(key , ':  ', m[key], style='red')
            sys.exit(2)
    
            
    def write_file(self, flag):
        if flag:
           pc.print("Write to file : ", style="yellow")
           pc.print("enabled" , style="green")
           pc.print("\n")

        else:
           pc.print("Export to JSON :", style="red")
           pc.print("disabled, ", style="red")
           pc.print("\n")

        self.writeFile = flag
    
    def json_dump(self, flag):
        if flag:
            pc.print("Export to JSON: ", style="yellow")
            pc.print("enabled", style="green")
            pc.print("\n")

        else:
            pc.print("Export to JSON : ", style="red")
            pc.print("disabled", style="red")
            pc.print("\n")

        self.jsonDump = flag

    def to_json(self, python_object):
        if isinstance(python_object, bytes):
            return {'__class__':'bytes', '__value__':codecs.encode(python_object, 'base64').decode()
            }
        raise TypeError(repr(python_object) + 'is not JSON parseable !')
    
        
    def from_json(self, json_object):
        if  '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object
  
    #check if you are following target's account
    def check_following(self):
        user=self.api.GetUser(screen_name=self.target)
        check_following = user.following
        if check_following:
            pc.print("You are following {}'s account.".format(self.target), style='green')
        else:
            pc.print("You are not following {}'s account. ".format(self.target), style='orange1')
        return 
    
    def is_protected(self,target):
        user=self.get_user(target)
        self.protected = user.protected
        if self.protected:
            pc.print("{} got a protected account. ".format(self.target), style='bright_cyan', end='')
            print("You need to follow {}'s account first.".format(self.target))
        
    
    def recent_tweets(self):
        """ Get most recent tweets of target
        > Code Flow:
            > make a request to UserTimeline
            > if successful:
                fetch allowed tweets
            > otherwise:
                show some clean error with code.
        """
        pc.print("Fetching latest tweets tweeted by {}".format(self.target))
        
        tweets = self.api.GetUserTimeline(screen_name=self.target)
        tweets_num = len(tweets)
        pc.print("Catched {} tweets of {} .".format(tweets_num, self.target))
        for tweet in tweets:
            #print(tweet)
            try:
               #get date of tweets
               tweeted_on = tweet.created_at
               # text of tweets
               ttweet = tweet.text
               #total likes on each tweetes
               total_fav = tweet.favorite_count
               #retweet of tweet
               rtweet = tweet.retweet_count
               #for id of tweets
               id = tweet.id
               #device or app information
               source = self.remove_tags(tweet.source)
               # mentions in tweet of target
               for mentions in tweet.user_mentions:
                   mentions = mentions.screen_name
               pc.print('tweet id : ', id, style='steel_blue1')  
               pc.print('date : ', tweeted_on, style='sky_blue1')
               pc.print('tweet : ', ttweet, style='bright_white')
               pc.print('retweets : ',rtweet, style='orange1')  
               pc.print('mentions : @',mentions, style='pink1')
               pc.print('favorites : ',total_fav, style='bright_red')
               pc.print('source or device : ',source, style='bright_yellow') 
               print(" ")  
               print("-----------------------------------------------------------------------------------------------------")
               
            except TwitterError as err:
                pc.print("Error : ", style='orange1',end='')
                for m in err.message:
                    for key in m:
                        pc.print(key , ':  ', m[key], style='bright_red')
                pass
            except Exception as err:
                pc.print(err, style='bright_red')
                pass        
        return                

    def remove_tags(self,html):
        """
        > A function for removing data from html get from given data
        > CodeFlow:
            > just basic use of bs4 lib.
        
        """
        soup = BeautifulSoup(html, "html.parser")
        
        for data in soup(['style', 'script']):
            #remove tags from html
            data.decompose()
            
        #return data by retreiving the tag content
        return ''.join(soup.stripped_strings)
    
    
    #function for get target's account overview
    def user_info(self):
        """
        > A function for overviewing target's account
        > Code Flow:
            > request for target's account 
            > iterate data for each field
            > on -f flag save data in text file in results/twitter/ folder
            > on Unexcepted condition:
                        > Show respective error
        """
        try:
            pc.print("Generating {}'s account overview....".format(self.target), style='green3')
            data = self.api.GetUser(screen_name=self.target)
            #print(data)
            pc.print("\n Target's Information: \n", style='green')
            pc.print("\n Username : {} , id : {} ".format(data.screen_name,data.id),style='yellow')
            pc.print("\n Joined on : ", data.created_at, style="red")
            pc.print("\n Full Name : ", data.name, style="bright_cyan")
            pc.print("\n Bio : ", data.description, style="sandy_brown")
            pc.print("\n Url : ", data.url, style="aquamarine1")
            pc.print("\n Geo Location Permission: ", data.geo_enabled, style='turquoise2')
            pc.print("\n Location : " ,data.location, style="orchid2")
            pc.print("\n Total Favourites  : "  ,data.favourites_count, style="bright_yellow")
            pc.print("\n Followers :  ", data.followers_count, style='orange_red1')
            pc.print("\n Following : ", data.friends_count, style='orchid2')
            pc.print("\n Total Tweets : ", data.statuses_count,style='green')
            pc.print("\n Active lists : ", data.listed_count, style='yellow')
            pc.print("\n Verified  : ", data.verified,style='sky_blue3' )
            pc.print("\n Profile Picture Url :  ", data.profile_image_url, style="bright_white")
            pc.print("\n Banner Url : ", data.profile_banner_url, style="bright_white")
            try:
                if self.is_protected(self.target):
                    return
                else:
                    pc.print("\n Recent Tweet : {} at {}".format(data.status.text, data.status.created_at), style='pink1')
                    pc.print("\n Device or Source : {}".format(self.remove_tags(data.status.source)), style="medium_spring_green")
            
            except AttributeError as err:
                pc.print("Showing this error because Target don't have any recent tweet!", style='red', end='')
                pc.print( err ,style='orange1')
            
                
            
            if self.jsonDump:
                user = {
                    "id":data.id,
                    "full_name":data.name,
                    "bio": data.description,
                    "fav_tweets": data.favourites_count,
                    "followers": data.followers_count,
                    "following":data.friends_count,
                    "tweets": data.statuses_count,
                    "lists": data.listed_count,
                    "banner_url": data.profile_banner_url,
                    "profile_pic": data.profile_image_url
                             
                }
                #print(user)
                json_file_name = "./results/twitter/" + self.target + "_.json"  
                with open(json_file_name, 'w') as fp:
                    json.dump(user, fp)
                    
        except TwitterError as err:
            pc.print(err, style="bright_red")
            pass    
      
    def profile_pic(self):
        """Function for downloading target's profile image
        > Code Flow:
                > if traget got profile image:
                    > urllib.request.urlretrieve(url, end)
                    > saveing image in results/twitter/ folder
                > On Unexpected Condition:
                    > Show respective error
        """  
        data = self.api.GetUser(screen_name=self.target)
        profile_pic = data.profile_image_url
        if profile_pic == None:
            pc.print("{} don't have profile picture !\n ".format(self.target) , style='sea_green3')
        else:
            try:
                pc.print("\n Downloading target's profile picture....", style='spring_green3')
                URL = data.profile_image_url
                if URL != "":
                    end = "./results/twitter/" + self.target + "_profile_pic.jpg"
                    urllib.request.urlretrieve(URL,end)
                    pc.print("Photos saved in results/ folder.", style="light_green")
                else:
                    pc.print("Sorry unable to download this time.", style="bright_red")
            except Exception as err:
                pc.print(err, style='red')
            
    def banner_pic(self):
        """Function for downloading target's profile banner
            > Code Flow:
                > if traget got banner:
                    > urllib.request.urlretrieve(url, end)
                    > saveing image in results/twitter/ folder
                > On Unexpected Condition:
                    > Show respective error
        """  
        
        data =self.api.GetUser(screen_name=self.target)    
        banner = data.profile_banner_url
        if banner == None:
            pc.print("{} don't have banner image !n".format(self.target), style='steel_blue1')
        else:
            try:
                pc.print("\n Downloading banner of target's profile...", style='turquoise2') 
                URL = data.profile_banner_url
                if URL != "":
                    end = "./results/twitter/" + self.target + "_banner.jpg" 
                    urllib.request.urlretrieve(URL, end)
                    pc.print("Banner is saved in results/ folder", style='light_green')
                
                else:
                    pc.print("Unable to download banner. Sorry!", style="red")
            except Exception as err:
                pc.print(err, style="red")
        
    
    #  function for getting some likes info of target
    
    
    """ PENDING saving in json and text file is not completed!!!! 
    @xadhrit  
    """
    def recent_fav(self):
        """function for extracting recent likes information of target
          
        """    
        if self.is_protected(self.target):
            return
        
        pc.print("Finding recent favourite tweets by {}...\n".format(self.target),style='sea_green2')
        data = self.api.GetFavorites(screen_name=self.target)
        print(" ")
        
        tweets = len(data)
        pc.print("Catched {} tweets which are liked by target".format(tweets), style="green")
        for tweet in data:
            #print(tweet)
            try:
               #get date of tweets
               tweeted_on = tweet.created_at
               # text of tweets
               ttweet = tweet.text
               # creators of tweets
               tweeted_by = tweet.user.screen_name
               #total likes on each tweetes
               total_fav = tweet.favorite_count
               #for id of tweets
               id = tweet.id
               #device or app information
               source = self.remove_tags(tweet.source)
            
            
               pc.print('tweet id : ', id, style='steel_blue1')  
               pc.print('date : ',tweeted_on, style='sky_blue1')
               pc.print('tweet ',ttweet, style='bright_white')
               pc.print('posted by : ',"@",tweeted_by, style='orange1')  
               pc.print('favorites : ',total_fav, style='bright_red')
               pc.print('source or device : ',source, style='bright_yellow') 
               print(" ")  
               print("*****************************************************************************")
                 
               #print(fav_tweets)  
            except TwitterError as err:
                pc.print("Error : ", style='orange1',end='')
                for m in err.message:
                    for key in m:
                        pc.print(key , ':  ', m[key], style='bright_red')
                pass
            except Exception as err:
                pc.print(err, style='bright_red')        
        """
        if tweets > 0:
            
            if self.writeFile:
                file_name = "../../results/twitter/" + self.target + "_fav_tweets_.txt"
                ffav = open(file_name, "w") 
                ffav.write(str(fav_tweets))
                ffav.close()
                pc.print("All tweets have been saved in results/ folder.", style='green')
            
                
            if self.jsonDump:
            #    json_data['fav_tweets'] = fav_sorted
                json_file_name = "../../results/twitter/" + self.target + "_fav_tweets_.json"
                with open(json_file_name, 'w') as fp:
                    json.dump(json_data, fp)
                    pc.print("All tweets have been save in results/ folder", style="bright_yellow")
                 
        else:
            pc.print("No Tweets found! :(", style='bright_red')   
        """
        return
    
    
    def get_frnds(self):
        """function for getting following of target
        
        """    
        try:
            pc.print("Searching for {}'s following list".format(self.target), style='orange1')
            #get followings of target
            following = self.api.GetFriends(screen_name=self.target)
            following_num = len(following) 
            
            for user in following:
                id = user.id
                username = user.screen_name
                full_name = user.name
                joined = user.created_at
                
                pc.print(" id : ", id, style='green', end='')
                pc.print(" | username : ", username, style='steel_blue1', end='')
                pc.print(" | full name : ", full_name, style='pink1',end='')
                pc.print(" | Joined On : ", joined , style="cyan")
                
                print(" ")
            pc.print('{} follows  {} users. '.format(self.target , following_num), style='bright_white') 
                 
            if self.writeFile:
                
                file_name = "./results/twitter/" + self.target + "_following_.txt"
                file = open(file_name, "w")
                file.write(str(id))
                file.write(str(username))
                file.close()
                pc.print("Results save in results/twitter/ folder.", style='green')
                
        except (Exception, TwitterError) as err:
            pc.print(err,'User have a protected or suspended account!' , style='bright_red')       
                
            
    
    def get_followers(self):    
        """ A function for getting followers of target's account
        > Code Flow:
               > request api for GetFollowers
               > save follower's username, id and full name in json or text file
               > On Unexcepted conditions:
                        if followers exceeds than limit then show simple rate limit exceed error
        
        """
        try:
            pc.print("Fetching {}'s follower list".format(self.target), style='green')
            #get followers of target
            followers = self.api.GetFollowers(screen_name=self.target)
            followers_num = len(followers)
            #print(followers)
            for user in followers:
                id = user.id
                joined = user.created_at
                username = user.screen_name
                full_name = user.name
            
                pc.print(" id : ", id, style='green', end='')
                pc.print(" | username : ", username, style='steel_blue1', end='')
                pc.print(" | full name : ", full_name, style='pink1',end='')
                pc.print(" | Joined On : ", joined , style="cyan")
                print(" ")
            pc.print("{} have {} followers.".format(self.target, followers_num))     
            
        except TwitterError as err:
            pc.print("Error : ", style='orange1',end='')
            for m in err.message:
                for key in m:
                    pc.print(key , ':  ', m[key], style='red')
            pass    
        except Exception as error :
            pc.print( error  , style='orange1')    
            pass     
        
    """
    function for gettting hashtags used by target in it's tweets :) it's limited #lul
    """    
    def get_hashtags(self):
        """
        > first get  tweets and then extract hastags
        > on unexpected condition show error
        """
        pc.print("Searching for hashtags used by {}".format(self.target),style='bright_yellow')
        try:
            tweets = self.api.GetUserTimeline(screen_name=self.target)
            for tweet in tweets:
                for tags in tweet.hashtags:
                    tag = tags.text
                    pc.print('#{}'.format(tag),style='green')
        
        except TwitterError as err:
            pc.print("Error : ", style='orange1',end='')
            pc.print('{} got a protected or suspended account. {}'.format(self.target,err.message),style='red')
            
            
                
      
