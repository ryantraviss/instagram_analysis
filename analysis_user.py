#analysis_user.py by Ryan Traviss
"""
Notes:
    This code has only been tested on Python 3.7.6
    I have liked 8242 posts and 223 comments from 556 diffrent accounts.
    I have made 285 comments.
    seen_content "ads_seen", "posts_seen", "videos_watched" are only for more recent period
    example comment: ['2020-04-24T15:39:04+00:00', '@username How much lag is there on that server?', 'username']
    message includes posts send as messages
    a good setting for making venn diagram of my friends activity:
        AnalysisUser(messages=True,followers=True,following=True,chaining_seen=False)
    I have not attempted to round numbers as its actually really HARD to do properly!
        eg. round(0.0750,2) -> 0.07 which is just wrong
        Just do it yourself and don't be lazy aha.
""" 

"""
Comment Mode (self.comment_mode) Documentation
    This is to explain the variable comment_mode which is used to select the username of a comment you have made.
    It is a string with 3 supported values: ("post", "reply" or "smart")
    
    "post" : This means the username of a comment is the username of the user 
            who made the post on which you have commented. 
            Very often this is your username if you reply to comments on your own posts.
    
    "reply" : This means the username is the 1st word of the comment minus the 1st character
            Comments where you are replying to someone are automatically "@username blah blah..."
            
    "smart" : If the first character of the comment is "@" then "reply" is used 
            else "post" method is used.
            
    Generally, "smart" gives the most informative results so it is the default mode. 
"""

"""
Message Mode User (self.message_mode_user) Documentation
    This is to explain the variable message_mode_user which determines how users are extracted from messages.
    It is a string with 6 supported values: ("sender_individual","sender_group","sender_both","participants_individual","participants_group","participants_both")
    
    "sender_individual" : The users are the senders of messages in chats with only two people in ie. you and them.
    "sender_group" : The users are the senders of messages in groupchats (have more than 2 participants).
    "sender_both" : Both of the above are used.
                    Each user is added once per message they send.
        
    "participants_individual" : The users are anyone who has sent a message to you or you have a message to privately.
    "participants_group" : The users are anyone that you are in a groupchat with. 
    "participants_both" : Both of the above are used.
    
    "sender_individual" is the default mode.
"""

"""
Message Likes Mode User (self.message_likes_mode_user)
    This is to explain the variable message_likes_mode_user which determines how users are extracted from the likes on messages.
    It is a string with 10 supported values: ("my_messages_individual", "my_messages_group", "my_messages_both",
                                             "my_likes_individual", "my_likes_group", "my_likes_both", "my_messages_likes_both"
                                             "all_likes_individual",  "all_likes_group", "all_likes_both")
    
    "my_messages_individual" : The users have liked a message of mine in a chat with only 2 participants.
    "my_messages_group" : The users have a liked a message of mine in a groupchat.
    "my_messages_both" : Both of the above.
    
    "my_likes_individual" : The users have sent a message I liked in a chat with only 2 participants.
    "my_likes_group" : The users have sent a message I liked in a groupchat.
    "my_likes_both" : Both of the above.
    
    "my_messages_likes_both" : Both of "my_messages_both" and "my_likes_both".
    
    "all_likes_individual" : The users have liked a message in a chat with only 2 participants.
    "all_likes_group" : The users have liked a message in a groupchat.
    "all_likes_both" : Both of the above.

    "my_messages_likes_both" is the default mode.    
"""

import json, matplotlib.pyplot as plt, numpy as np, datetime, statistics, util

class AnalysisUser:
    def __init__(self, path = "", likes_filename = "likes.json", comments_filename = "comments.json", 
                 media_filename = "media.json", seen_content_filename = "seen_content.json", 
                 profile_filename = "profile.json", messages_filename = "messages.json", connections_filename = "connections.json",
                 media_likes = True, comment_likes = True, comments = True, comment_mode = "smart", 
                 stories = True, posts = True, post_mode = "single", 
                 direct = True, chaining_seen = True, messages = True, message_mode_user = "sender_individual", 
                 message_likes = True, message_likes_mode_user = "my_messages_likes_both", followers = False, following = False, print_latex = False):
        """
        Creates an object of from the Likes class.

        Parameters
        ----------
        path : String, optional
            The path of the folder containing the JSON files. The default is "".
        likes_filename : String, optional
            The filename of the likes JSON file. The default is "likes.json".
        comments_filename : String, optional
            The filename of the comments JSON file. The default is "comments.json".
        media_filename : String, optional
            The filename of the posts JSON file. The default is "media.json".
        seen_content_filename : String, optional
            The filename of the seen_content JSON file. The default is "seen_content.json".
        messages_filename : String, optional
            The filename of the messages JSON file. The default is "messages.json".
        connections_filename : String, optional
            The filename of the connections JSON file. The default is "connections.json".
        media_likes : Boolean, optional
            Should likes on posts be used (called media_likes in JSON data). The default is True.
        comment_likes: Boolean, optional
            Should likes on comments be used (called comment_likes in JSON data). The default is True.
        comments : Boolean, optional
            Should comments be used. The default is True.
        comment_mode : String ("post", "reply" or "smart"), optional
            How should the username be identified from comments(See docs at top). The default is "smart".
        stories: Boolean, optional
            Should stories be used (timestamp only). The default is True.
        posts: Boolean, optional
            Should posts be used (timestamp only). The default is True.
        post_mode : String ("single" or "multiple"), optional
            How should the datetime be identified from posts(See docs at top). The default is "single".
        direct : Boolean, optional
            Should pictures sent as direct messages be used. The default is True.
        chaining_seen : Boolean, optional
            Should links followed on Instagram be used. The default is True.
        messages : Boolean, optional
            Should messages be used. The default is True.
        message_mode_user : String ("sender_individual","sender_group","sender_both","participants_individual","participants_group","participants_both"), optional
            How should user be indentified from messages(see docs at top). The default is "sender_individual".
        message_likes : Boolean, optional
            Should when you have liked messages be used. The default is True.
        message_likes_mode_user : String ("my_messages_individual", "my_messages_group", "my_messages_both","my_likes_individual", "my_likes_group", "my_likes_both", "my_messages_likes_both","all_likes_individual",  "all_likes_group", "all_likes_both"), optional
            How should user be identified from message likes(see docs at top). The default is "my_messages_likes_both".
        followers : Boolean, optional
            Should followers be used. The default is False.
        following : Boolean, optional
            Should users you follow be used. The default is False.
        print_latex : Boolean, optional
            Should the latex to make the tables be printed. The default is False.
        Returns
        -------
        None.

        """
        self.media_likes = media_likes
        self.comment_likes = comment_likes
        self.comments = comments
        self.comment_mode = comment_mode
        self.stories = stories
        self.posts = posts
        self.post_mode = post_mode
        self.direct = direct
        self.chaining_seen = chaining_seen
        self.messages = messages
        self.message_mode_user = message_mode_user
        self.message_likes = message_likes
        self.message_likes_mode_user = message_likes_mode_user
        self.followers = followers
        self.following = following
        self.print_latex = print_latex
        

        self.likes_json_data = util.read_json(path+likes_filename)
        self.comments_json_data = util.read_json(path+comments_filename)
        self.media_json_data = util.read_json(path+media_filename)
        self.seen_content_json_data = util.read_json(path+seen_content_filename)
        self.profile_json_data = util.read_json(path+profile_filename)
        self.messages_json_data = util.read_json(path+messages_filename)
        self.connections_json_data = util.read_json(path+connections_filename)
        
        self.account_created_date = self.profile_json_data["date_joined"]
        self.username = self.profile_json_data["username"]
        
    def change_settings(self, media_likes = True, comment_likes = True, comments = True, comment_mode = "smart", stories = True, 
                 posts = True, post_mode = "single", direct = True, chaining_seen = True, messages = True, message_mode_user = "sender_individual",
                 message_likes = True, message_likes_mode_user = "my_messages_likes_both", followers = True, following = True, print_latex = False, settings=()):
        """
        Updates the state of the variables determining which sources of data should be used.

        Parameters
        ----------
        See __init__ documentation.
        settings : Tuple, optional
            A tuple of all the other parameters that is generated from read_settings().

        Returns
        -------
        None.

        """
        if settings != ():
            (self.media_likes, self.comment_likes, self.comments, 
             self.comment_mode, self.stories, self.posts, self.post_mode,
             self.direct, self.chaining_seen, self.messages, self.message_mode_user,
             self.message_likes, self.message_likes_mode_user, 
             self.followers, self.following, self.print_latex) = settings
        else:
            self.media_likes = media_likes
            self.comment_likes = comment_likes
            self.comments = comments
            self.comment_mode = comment_mode
            self.stories = stories
            self.posts = posts
            self.post_mode = post_mode
            self.direct = direct
            self.chaining_seen = chaining_seen
            self.messages = messages
            self.message_mode_user = message_mode_user
            self.message_likes = message_likes
            self.message_likes_mode_user = message_likes_mode_user
            self.followers = followers
            self.following = following
            self.print_latex = print_latex
        
    def read_settings(self):
        """
        Returns all the setttings currently being used as a tuple.

        Returns
        -------
        See __init__() documentation.

        """
        return (self.media_likes, self.comment_likes, self.comments, 
        self.comment_mode, self.stories, self.posts, self.post_mode,
        self.direct, self.chaining_seen, self.messages, self.message_mode_user,
        self.message_likes, self.message_likes_mode_user, 
        self.followers, self.following, self.print_latex)
        
    def _read_json(self, filename):
        """
        Opens the file, reads the data, closes it and turns it into a dictionary. 

        Parameters
        ----------
        filename : string
            The filename of a JSON file to be opened and read.

        Returns
        -------
        Dictionary
            The JSON data in the file as a Python dictionary.

        """
        with open(filename, "r", encoding="utf8") as f:
            return json.loads(f.read())  

    def _extract_user(self, json_data, index_key):
        return_data = []
        for i in range(len(json_data)):
            return_data.append(json_data[i][index_key])
        return return_data   
        
    def _data_user(self):
        """
        This private method deals with getting a list of the users.
        Data is extracted from diffrent sources based on selected settings.

        Returns
        -------
        list 
            A list of users.

        """
        user_data = []
        if self.media_likes:
            user_data.extend(self._extract_user(self.likes_json_data["media_likes"],1))
            #for x in range(len(self.likes_json_data["media_likes"])):
             #   user_data.append(self.likes_json_data["media_likes"][x][1])
                
        if self.comment_likes:
            user_data.extend(self._extract_user(self.likes_json_data["comment_likes"],1))
            #for x in range(len(self.likes_json_data["comment_likes"])):
             #   user_data.append(self.likes_json_data["comment_likes"][x][1])
                
        if self.comments: #see documentation at top of file about comment modes
            for x in range(len(self.comments_json_data["media_comments"])):
                if self.comment_mode == "post":
                    user_data.append(self.comments_json_data["media_comments"][x][2])
                elif self.comment_mode == "reply":
                    #The following line gets the first word of each comment and removes the first character
                    #which should be an @ if you are replying to someone and adds the rest of the word
                    #which should be a username (but isn't always if it is a top level comment)
                    user_data.append(self.comments_json_data["media_comments"][x][1].split(" ")[0][1:])
                elif self.comment_mode == "smart":
                    if self.comments_json_data["media_comments"][x][1].split(" ")[0][0] == "@":
                        user_data.append(self.comments_json_data["media_comments"][x][1].split(" ")[0][1:])
                    else:
                        user_data.append(self.comments_json_data["media_comments"][x][2])
                        
        if self.chaining_seen:
            user_data.extend(self._extract_user(self.seen_content_json_data["chaining_seen"],"username"))
            #for x in range(len(self.seen_content_json_data["chaining_seen"])):
             #   user_data.append(self.seen_content_json_data["chaining_seen"][x]["username"])
                
        if self.messages: #the user message mode is explained in documentation at top
            if self.message_mode_user == "sender_individual" or self.message_mode_user == "sender_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) == 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            user_data.append(self.messages_json_data[x]["conversation"][y]["sender"])
                            
            if self.message_mode_user == "sender_group" or self.message_mode_user == "sender_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) > 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            user_data.append(self.messages_json_data[x]["conversation"][y]["sender"])
                            
            if self.message_mode_user == "participants_individual" or self.message_mode_user == "participants_both":
                 for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) == 2:
                        user_data.append(self.messages_json_data[x]["participants"][0])
                        user_data.append(self.messages_json_data[x]["participants"][1])
                        
            if self.message_mode_user == "participants_group" or self.message_mode_user == "participants_both":
                 for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) > 2:
                        for y in range (len(self.messages_json_data[x]["participants"])):
                            user_data.append(self.messages_json_data[x]["participants"][y])
                            
        if self.message_likes: #message_likes_mode_user is explained in docs at top
            if self.message_likes_mode_user == "my_messages_individual" or self.message_likes_mode_user == "my_messages_both" or self.message_likes_mode_user == "my_messages_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) == 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if self.messages_json_data[x]["conversation"][y]["sender"] == self.username:
                                if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                    for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                        user_data.append(self.messages_json_data[x]["conversation"][y]["likes"][z]["username"])
                                    
            if self.message_likes_mode_user == "my_messages_group" or self.message_likes_mode_user == "my_messages_both" or self.message_likes_mode_user == "my_messages_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) > 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if self.messages_json_data[x]["conversation"][y]["sender"] == self.username:
                                if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                    for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                        user_data.append(self.messages_json_data[x]["conversation"][y]["likes"][z]["username"])
                                        
            if self.message_likes_mode_user == "my_likes_individual" or self.message_likes_mode_user == "my_likes_both" or self.message_likes_mode_user == "my_messages_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) == 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                    if self.messages_json_data[x]["conversation"][y]["likes"][z]["username"] == self.username:
                                        user_data.append(self.messages_json_data[x]["conversation"][y]["sender"])
                                        
            if self.message_likes_mode_user == "my_likes_group" or self.message_likes_mode_user == "my_likes_both" or self.message_likes_mode_user == "my_messages_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) > 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                    if self.messages_json_data[x]["conversation"][y]["likes"][z]["username"] == self.username:
                                        user_data.append(self.messages_json_data[x]["conversation"][y]["sender"])
                                        
            if self.message_likes_mode_user == "all_likes_individual" or self.message_likes_mode_user == "all_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) == 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                    user_data.append(self.messages_json_data[x]["conversation"][y]["likes"][z]["username"])
                                    
            if self.message_likes_mode_user == "all_likes_group" or self.message_likes_mode_user == "all_likes_both":
                for x in range(len(self.messages_json_data)):
                    if len(self.messages_json_data[x]["participants"]) > 2:
                        for y in range(len(self.messages_json_data[x]["conversation"])):
                            if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                                for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                                    user_data.append(self.messages_json_data[x]["conversation"][y]["likes"][z]["username"])
                                        
        if self.followers:
            for key in self.connections_json_data["followers"].keys():
                user_data.append(key)
                
        if self.following:
            for key in self.connections_json_data["following"].keys():
                user_data.append(key)
                
        return user_data
       
    def profile_summary(self):
        """
        Prints a summary of your profile.

        Returns
        -------
        None.

        """
        print("Your name is",self.profile_json_data["name"] + ", you are", self.profile_json_data["gender"],"and you were born on",self.profile_json_data["date_of_birth"]+".")
        if self.profile_json_data["private_account"]:
            print("You joined Instagram at", self.profile_json_data["date_joined"], "and made a private account with the username", self.profile_json_data["username"]+".")
        else:
            print("You joined Instagram at", self.profile_json_data["date_joined"], "and made a public account with the username", self.profile_json_data["username"]+".")
        print("Your bio is:\n"+self.profile_json_data["biography"])
        print("Your email is",self.profile_json_data["email"],"and your website is", self.profile_json_data["website"]+".")
        
    def top_message(self):
        """
        Prints the most liked message in the data.
        (NOTE: Not part of my EMC due to privacy issues.)

        Returns
        -------
        None.

        """
        top_message = ""
        top_message_likes = 0
        for x in range(len(self.messages_json_data)):
            for y in range(len(self.messages_json_data[x]["conversation"])):
                if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                    if len(self.messages_json_data[x]["conversation"][y]["likes"]) > top_message_likes:
                        top_message = self.messages_json_data[x]["conversation"][y]#["text"]
                        top_message_likes = len(self.messages_json_data[x]["conversation"][y]["likes"])
        print(top_message_likes, top_message)
        
    def best_friends(self):
        """
        Conducts best friends analysis.

        Returns
        -------
        None.

        """
        if self.username != "you":
            user_data = self._data_user()
            while self.username in user_data:
                user_data.remove(self.username)
            util.table(user_data,sort_by_likes=True) #add graphs?
        else:
            print("Error: This doesn't work with anonymised data!")
        
    def worst_friends(self):
        """
        Conducts worst friend analysis (basically same as best friend but sorting low to high).

        Returns
        -------
        None.

        """
        if self.username != "you":
            user_data = self._data_user()
            while self.username in user_data:
                user_data.remove(self.username)
            util.table(user_data,sort_by_likes=True,sort="desc")
        else:
            print("Error: This doesn't work with anonymised data!")
            
    def video_calls(self):
        video_call_data = []
        start_time_string = ""
        stop_time_string = ""
        for x in range(len(self.messages_json_data)):#x is chat
            for y in range(len(self.messages_json_data[x]["conversation"])):#y is message in that chat
                message = self.messages_json_data[x]["conversation"][y]
                if "video_call_action" in message.keys():
                    if "started a video call" in message["video_call_action"]:
                        start_time_string = self.messages_json_data[x]["conversation"][y]["created_at"][:19]
                        start_time = datetime.datetime.strptime(start_time_string,"%Y-%m-%dT%H:%M:%S")
                        #print(message)
                    elif "ended a video call" in message["video_call_action"]:
                        stop_time_string = self.messages_json_data[x]["conversation"][y]["created_at"][:19]
                        stop_time = datetime.datetime.strptime(stop_time_string,"%Y-%m-%dT%H:%M:%S")
                        #print(message)
                    else:
                        pass#print(message)
                    if start_time_string != "" and stop_time_string != "":
                        video_call_data.append((stop_time - start_time))
                        start_time_string = ""
                        stop_time_string = ""
                        
        print(video_call_data)
        
#Below are all the public methods of AnalysisUser
analysis_object = AnalysisUser(path="")#, media_likes = False, comment_likes = False, comments = False, stories = False, 
                         #posts = False, direct = False, messages = False, message_likes = True, chaining_seen = False, followers = False, following=False)
#analysis_object.change_settings()
#analysis_object.read_settings()
#analysis_object.profile_summary()
#analysis_object.top_message()
#analysis_object.best_friends()
#analysis_object.worst_friends()
analysis_object.video_calls()

#util.json_file_structure(analysis_object.media_json_data["photos"])
