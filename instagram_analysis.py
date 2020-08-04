#instagram_analysis.py by Ryan Traviss
"""
Notes:
    This code has only been tested on Python 3.7.6
    2017-07-19T08:57:05 was when I made my account in format YYYY-MM-DDThh:mm:ss
    the timezone for my data is always +00:00
    I have liked 8242 posts and 223 comments from 556 diffrent accounts.
    I have made 285 comments.
    seen_content "ads_seen", "posts_seen", "videos_watched" are only for more recent period
    example comment: ['2020-04-24T15:39:04+00:00', '@username How much lag is there on that server?', 'username']
    message includes posts send as messages
    a good setting for making venn diagram of my friends activity:
        Analysis(messages=True,followers=True,following=True,chaining_seen=False)
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
Post Mode (self.post_mode) Documentation
    This is to explain the variable post_mode which determines how datetimes are extracted from posts.
    It is a string with 2 supported values: ("single" or "multiple")
    
    "single" : This means each post counts as a single datetime regardless of how many photos it contains.
            This is checked by comparing the datetimes (excluding minutes, seconds, timezone) and captions of 
            posts next to each other. 
            (It appears Instagram can record diffrent minutes for diffrent photos in the same post
            and this lead to errors so thus why caption is also used. 
            Captions alone are not neccesarily unique amongst a user's posts.)
            
    "multiple" : Each photo within a post (which can contain up to 10) is counted as a datetime.
    
    I see no reason why posts should have different weightings in the results 
    based on the number of photos they contain so "single" is the default mode.
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

import json, matplotlib.pyplot as plt, numpy as np, datetime, statistics

class Analysis:
    def __init__(self, path = "", likes_filename = "likes.json", comments_filename = "comments.json", 
                 posts_filename = "media.json", seen_content_filename = "seen_content.json", 
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
        posts_filename : String, optional
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
        

        self.likes_json_data = self.__read_json__(path+likes_filename)
        self.comments_json_data = self.__read_json__(path+comments_filename)
        self.posts_json_data = self.__read_json__(path+posts_filename)
        self.seen_content_json_data = self.__read_json__(path+seen_content_filename)
        self.profile_json_data = self.__read_json__(path+profile_filename)
        self.messages_json_data = self.__read_json__(path+messages_filename)
        self.connections_json_data = self.__read_json__(path+connections_filename)
        
        self.account_created_date = self.profile_json_data["date_joined"]
        self.username = self.profile_json_data["username"]
        self.min_year, self.max_year = self.__min_max_year__()
        
    def __min_max_year__(self):
        """
        Returns the oldest year and most recent year in the selected data.

        Returns
        -------
        int, int
            oldest year, most recent year

        """
        years = self.__data_time__(slice(10,11), "T", slice(0,4), return_ints=True)
        if years != []:
            years = np.unique(years, return_counts=False)
            return min(years), max(years)
        else:
            print("Error: No data")
            return 0,0
        
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
        
        self.min_year, self.max_year = self.__min_max_year__()
        
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
        
    def __read_json__(self, filename):
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
        file_handle = open(filename,"r",encoding="utf8")
        raw_data = file_handle.read()
        file_handle.close()
        return json.loads(raw_data)
        
    def __data_time__(self, slice_match, match, slice_keep, return_ints=True):
        """
        This private method deals with extracting the right part of the timestamp from the data

        Parameters
        ----------
        slice_match : Slice
            The slice of the datetime to compare.
        match : String
            What should the datetime fragment equal.
        slice_keep : Slice
            What slice of the datetime should be returned.
        return_ints : Boolean, optional
            Should the list being returned be a list of integers. The default is True.

        Returns
        -------
        List (if return_ints then integers else strings)
            A list of selected fragments of the datetime.

        """
        time_data = []
        if self.media_likes:
            for x in range(len(self.likes_json_data["media_likes"])):
                if self.likes_json_data["media_likes"][x][0][slice_match] == match:
                    time_data.append(self.likes_json_data["media_likes"][x][0][slice_keep])
        if self.comment_likes:
            for x in range(len(self.likes_json_data["comment_likes"])):
                if self.likes_json_data["comment_likes"][x][0][slice_match] == match:
                    time_data.append(self.likes_json_data["comment_likes"][x][0][slice_keep])
           
        if self.comments:
            for x in range(len(self.comments_json_data["media_comments"])):
                if self.comments_json_data["media_comments"][x][0][slice_match] == match:
                    time_data.append(self.comments_json_data["media_comments"][x][0][slice_keep])
                    
        if self.stories:
            for x in range(len(self.posts_json_data["stories"])):
                if self.posts_json_data["stories"][x]["taken_at"][slice_match] == match:
                    time_data.append(self.posts_json_data["stories"][x]["taken_at"][slice_keep])
                    
        if self.posts: #see documentation at top about post modes
            previous_datetime = ""
            previous_caption = ""
            for x in range(len(self.posts_json_data["photos"])):
                if self.post_mode == "multiple": 
                    if self.posts_json_data["photos"][x]["taken_at"][slice_match] == match:
                        time_data.append(self.posts_json_data["photos"][x]["taken_at"][slice_keep])
                elif self.post_mode == "single":
                    current_datetime = self.posts_json_data["photos"][x]["taken_at"][0:13]
                    current_caption = self.posts_json_data["photos"][x]["caption"]
                    if current_datetime[slice_match] == match and current_datetime != previous_datetime and current_caption != previous_caption:
                        time_data.append(current_datetime[slice_keep])
                    previous_datetime = current_datetime
                    previous_caption = current_caption
                        
        
        if self.direct:
            for x in range(len(self.posts_json_data["direct"])):
                if self.posts_json_data["direct"][x]["taken_at"][slice_match] == match:
                    time_data.append(self.posts_json_data["direct"][x]["taken_at"][slice_keep])
        
        if self.chaining_seen:
            for x in range(len(self.seen_content_json_data["chaining_seen"])):
                if self.seen_content_json_data["chaining_seen"][x]["timestamp"][slice_match] == match:
                    time_data.append(self.seen_content_json_data["chaining_seen"][x]["timestamp"][slice_keep])
                    
        if self.messages: #see documentation at top about messages
            for x in range(len(self.messages_json_data)):
                for y in range(len(self.messages_json_data[x]["conversation"])):
                    if self.messages_json_data[x]["conversation"][y]["created_at"][slice_match] == match and self.messages_json_data[x]["conversation"][y]["sender"] == self.username:
                        time_data.append(self.messages_json_data[x]["conversation"][y]["created_at"][slice_keep])
                    
        if self.message_likes:
             for x in range(len(self.messages_json_data)):
                for y in range(len(self.messages_json_data[x]["conversation"])):
                    if "likes" in self.messages_json_data[x]["conversation"][y].keys():
                        for z in range(len(self.messages_json_data[x]["conversation"][y]["likes"])):
                            if self.messages_json_data[x]["conversation"][y]["likes"][z]["date"][slice_match] == match and self.messages_json_data[x]["conversation"][y]["likes"][z]["username"] == self.username:
                                time_data.append(self.messages_json_data[x]["conversation"][y]["likes"][z]["date"][slice_keep])
                                #print(self.messages_json_data[x]["conversation"][y]["likes"])

        if self.followers:
            for key in self.connections_json_data["followers"].keys():
                if self.connections_json_data["followers"][key][slice_match] == match:
                    time_data.append(self.connections_json_data["followers"][key][slice_keep])
        
        if self.following:
            for key in self.connections_json_data["following"].keys():
                if self.connections_json_data["following"][key][slice_match] == match:
                    time_data.append(self.connections_json_data["following"][key][slice_keep])

        if return_ints:
            return list(map(int,time_data)) #turns list of strings into list of integers
        else:
            return time_data
        
    def __data_user__(self):
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
            for x in range(len(self.likes_json_data["media_likes"])):
                user_data.append(self.likes_json_data["media_likes"][x][1])
                
        if self.comment_likes:
            for x in range(len(self.likes_json_data["comment_likes"])):
                user_data.append(self.likes_json_data["comment_likes"][x][1])
                
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
            for x in range(len(self.seen_content_json_data["chaining_seen"])):
                user_data.append(self.seen_content_json_data["chaining_seen"][x]["username"])
                
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
    
    def __graph__(self,time_data,date,xlabel,style = "-b",unique = False, xtick_max = 0):
        """
        This private method plots the line graph of the data with nice formatting.

        Parameters
        ----------
        time_data : tuple or list
            The data to be plotted.
        date : string
            The period the data covers to add to the title.
        xlabel : string
            Self-explanatory.
        style : string, optional
            How the graph should look(shape of crosses, line graph vs scatter ect). The default is "-b".
        unique : Boolean, optional
            If np.unique been not been done already?. The default is False.
        xtick_max : integer, optional
            What should the xticks go up to from 0 (if 0 default behaviour is used). The default is 0.

        Returns
        -------
        None.

        """
        if time_data == [] or time_data == ([],[]):
            print("Error: No data to plot a line graph")
            return
        if unique:
            time,like_counts = time_data
        else:
            time,like_counts = np.unique(time_data, return_counts=True)
            
        plt.plot(time,like_counts,style)
        if xtick_max != 0:
            plt.xticks(range(0,24))
        #plt.xticks((time[0],time[5],time[10],time[15],time[20]))
        
        plt.xlabel(xlabel)
 
        plt.title("Activity per " +xlabel+ " in "+date)
        plt.ylabel("Activity")
        
        plt.show()
        #plt.savefig("F:\ExeterMathsSchool\My Data Individual EMC\graphs\media_likes_months_"+year)
        
    def __graph_boxplot__(self,time_data,date,xlabel):
        """
        This private method plots the boxplot of the data with nice formatting.

        Parameters
        ----------
        time_data : list of integers
            The data to be plotted.
        date : string
            When the data is from.
        xlabel : string
            Self-explanatory.

        Returns
        -------
        None.

        """
        if time_data == []:
            print("Error: No data to make a boxplot")
            return
        plt.boxplot(time_data,vert=False)
        plt.xticks(range(0,24))
        #plt.xticks(range(min(time_data),max(time_data)))
        plt.xlabel(xlabel)
        plt.title("Activity per " +xlabel+ " in "+date)
        plt.ylabel("Activity")
        plt.show()
        
    def __table__(self, data, missing_data_items=0, sort_by_likes=False, sort="asc", max_rows=100):
        """
        Produces a full table of the selected data including summary statistics.

        Parameters
        ----------
        data : list of integers
            The data being analized.
        missing_data_items : integer, optional
            The number of missing 0's. The default is 0.
        sort_by_likes : boolean, optional
            Should the table be sorted by like counts. The default is False.
        max_rows : integer, optional
            The maximum number of rows that should be displayed. The default is 100.
            
        Returns
        -------
        None.

        """
        if data == []:
            print("Error: No data to make table")
            return
        data_item, data_frequency = np.unique(data, return_counts=True)
        if sort_by_likes:
            data_frequency, data_item = zip( *sorted( zip(data_frequency, data_item), reverse=True ) )
            
        print("data_item data_frequency")
        if sort == "asc":
            for i in range(min(len(data_item),max_rows)):
                print(data_item[i],data_frequency[i])
        else:   #descending order
            for i in range(len(data_item)-1,(len(data_item)-max_rows),-1):
                print(data_item[i],data_frequency[i])
        
        if missing_data_items == 0:
            print("Please enter the amount of missing data items for the table above:")
            print("Enter 0 if all the data items appear")
            missing_data_items = int(input(">>>"))
        for x in range(0,missing_data_items):
            data_frequency = np.append(data_frequency,[0])
        
        print("Total", sum(data_frequency))
        print("n",len(data_item))
        print("Mean", np.mean(data_frequency))
        print("Median", statistics.median(data_frequency))
        print("SD",statistics.pstdev(data_frequency)) #population standard deviation
        print("Range",max(data_frequency)-min(data_frequency))
        print("Note:", missing_data_items,"missing 0's were added for the purpose of calulations")
        
        if self.print_latex:
            print("\n","#"*20,"Latex","#"*20)
            print("""\\begin{table}[h]\n\centering\n\caption{TBC}\n\label{table:1}\n\\begin{tabular}{ |c|c| } \n \hline TBC & TBC""")
            if sort == "asc":
                for i in range(min(len(data_item),max_rows)):
                    print(data_item[i],"&",data_frequency[i],"\\\\",end="")
            else:   #descending order
                for i in range(len(data_item)-1,(len(data_item)-max_rows),-1):
                    print(data_item[i],"&",data_frequency[i],"\\\\",end="")
            print("\hline Total &",sum(data_frequency),"\\\\")
            print("\hline Mean &",np.mean(data_frequency),"\\\\")
            print("\hline n &",len(data_item),"\\\\")
            print("Median &", statistics.median(data_frequency),"\\\\")
            print("SD & ",statistics.pstdev(data_frequency),"\\\\")
            print("Range & ",max(data_frequency)-min(data_frequency),"\\\\")
            print(""" \hline\n\end{tabular}\n\end{table}""")
            
    def json_file_structure(self, json_data, tabs=0):
        """
        Prints the file structure of a JSON file that has been opened using recursion.

        Parameters
        ----------
        json_data : dictionary
            An opened JSON file eg likes_json_data.
        tabs : integer, optional
            How many tabs should be displayed. The default is 0.

        Returns
        -------
        None.

        """
        if type(json_data) is dict:
            for key in json_data.keys():
                print("\t"*tabs+key)
                self.json_file_structure(json_data[key],tabs=tabs+1)
        elif type(json_data) is list:
            keys = []
            for i in range(len(json_data)):
                if type(json_data[i]) is dict:
                    if json_data[i].keys() not in keys:
                        keys.append(json_data[i].keys())
                        
                        self.json_file_structure(json_data[i],tabs=tabs+1)
                        print("\t"*tabs+str(json_data[i].keys()))
                else:
                    print("\t"*tabs+"["+ str(i) +"]")
                    self.json_file_structure(json_data[i],tabs=tabs+1)
            if len(keys) > 1:
                print("\t"*tabs+str(keys))
            
            
        else:
            print("\t"*tabs+str(json_data).replace("\n","\\\\"))
            
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
        
    def timezone_test(self):
        """
        Prints all of the timezones when I liked a post/comment.

        Returns
        -------
        None.

        """
        timezones = self.__data_time__(slice(10,11), "T", slice(19,26), return_ints=False)
        print("This is a list of all the times zones for which there is a piece of data:")
        print(np.unique(timezones, return_counts=False))
        
    def date_range(self):
        """
        Prints the oldest and most recent piece of data and the time between.

        Returns
        -------
        None.

        """
        dates = self.__data_time__(slice(10,11), "T", slice(0,19), return_ints=False)
        dates = np.unique(dates, return_counts=False)
        dates = [datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S") for date in dates]
        
        print("The oldest datetime in selected data:",min(dates))
        print("The most recent datetime in selected data:",max(dates))
        print("The time between the most recent and oldest datetimes in selected data:",max(dates)-min(dates))
          
    def hours_minutes(self,year_month_day):
        """
        Produces table for Hours:Minutes

        Parameters
        ----------
        year_month_day : string
            The data to match - can be YYYY-MM-DD, YYYY-MM or empty for all time.

        Returns
        -------
        None.

        """
        if len(year_month_day) == 10:
            time_data = self.__data_time__(slice(0,10),year_month_day,slice(11,16),return_ints=False)
        elif len(year_month_day) == 7:#year-month
            time_data = self.__data_time__(slice(0,7),year_month_day,slice(11,16),return_ints=False)
        else:
            time_data = self.__data_time__(slice(10,11),"T",slice(11,16),return_ints=False)
        #self.__graph__(time_data,year_month_day,"Hour:Minute")
        self.__table__(time_data)
        
    def hours(self,year_month_day):
        """
        Conducts analysis on hours.

        Parameters
        ----------
        year_month_day : string
            The data to match - can be YYYY-MM-DD, YYYY-MM, YYYY or empty for all time..

        Returns
        -------
        None.

        """
        if len(year_month_day) == 10:#year-month-day
            time_data = self.__data_time__(slice(0,10),year_month_day,slice(11,13))
        elif len(year_month_day) == 7:#year-month
            time_data = self.__data_time__(slice(0,7),year_month_day,slice(11,13))
        elif len(year_month_day) == 4:#year
            time_data = self.__data_time__(slice(0,4),year_month_day,slice(11,13))
        else:#all of time
            time_data = self.__data_time__(slice(10,11),"T",slice(11,13))
            year_month_day = "all time"
            
        self.__graph__(time_data,year_month_day,"Hour",xtick_max=24)
        self.__table__(time_data,missing_data_items=(24-len(np.unique(time_data))))
        self.__graph_boxplot__(time_data,year_month_day,"Hour")
    
    def day_of_week_hours(self,year_month,graph_per_day=False):
        """
        Conducts hours analysis by day of week (optional) and weekday vs weekend.

        Parameters
        ----------
        year_month : string
            The data to match YYYY or YYYY-MM.
        graph_per_day : boolean, optional
            Should a graph/table be produced for each day of the week. The default is False.

        Returns
        -------
        None.

        """
        days_of_week = []
        if len(year_month) == 4:
            time_data = self.__data_time__(slice(0,4),year_month,slice(5,13),return_ints=False)#,return_counts=True)
            for month_day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:5]))
                days_of_week.append([day_datetime.isoweekday(),month_day[-2:]])
        else:
            time_data = self.__data_time__(slice(0,7),year_month,slice(8,13),return_ints=False)        
            for day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(year_month[5:7]),int(day[:2]))
                days_of_week.append([day_datetime.isoweekday(),day[-2:]])
                
        hours = [[],[],[],[],[],[],[]]
        for day_of_week in range(1,8):
            for day_of_week_hour in days_of_week:
                if day_of_week_hour[0] == day_of_week:
                    hours[day_of_week-1].append(day_of_week_hour[1])
            hours[day_of_week-1] = list(map(int,hours[day_of_week-1]))
            if graph_per_day:
                self.__graph__(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)),xtick_max=24)
                self.__graph_boxplot__(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)))
                print("Day of week",day_of_week)
                self.__table__(hours[day_of_week-1],missing_data_items=(24-len(np.unique(hours[day_of_week-1]))))
        
        workday_hours = hours[0]+hours[1]+hours[2]+hours[3]+hours[4]
        self.__graph__(workday_hours,year_month,"hour during the week(Monday-Friday)",xtick_max=24)
        self.__graph_boxplot__(workday_hours,year_month,"hour during the week(Monday-Friday)")
        print("Weekdays(Monday-Friday)")
        self.__table__(workday_hours,missing_data_items=(24-len(np.unique(workday_hours))))
        
        weekend_hours = hours[5] + hours[6]
        self.__graph__(weekend_hours,year_month,"hour during the weekend",xtick_max=24)
        self.__graph_boxplot__(weekend_hours,year_month,"hour during the weekend")
        print("Weekend")
        self.__table__(weekend_hours,missing_data_items=(24-len(np.unique(weekend_hours))))
        
    
    def day_of_week(self,year_month):
        """
        Conducts analysis by day of week.

        Parameters
        ----------
        year_month : string
            The data to match YYYY or YYYY-MM.

        Returns
        -------
        None.

        """
        day_of_week = []
        if len(year_month) == 4:
            time_data = self.__data_time__(slice(0,4),year_month,slice(5,10),return_ints=False)
            for month_day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:]))
                day_of_week.append(day_datetime.isoweekday())
        else:
            time_data = self.__data_time__(slice(0,7),year_month,slice(8,10),return_ints=False)        
            for day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(year_month[5:7]),int(day))
                day_of_week.append(day_datetime.isoweekday())
        self.__graph__(day_of_week,year_month,"Day of Week")#,style = "xb")
        self.__table__(day_of_week)
        
    def days(self,year_month):
        """
        Conducts analysis on days.

        Parameters
        ----------
        year_month : string
            The data to match - YYYY-MM.

        Returns
        -------
        None.

        """
        time_data = self.__data_time__(slice(0,7),year_month,slice(8,10))
        self.__graph__(time_data,year_month,"Day")
        self.__graph_boxplot__(time_data,year_month,"Day")
        self.__table__(time_data)
        
    def top_days(self,number_of_days=25):
        """
        Prints a table of the dates of the days with the most activity.
        
        Parameters
        ----------
        number_of_days : string, optional
            The number of days to display. The default is 25.

        Returns
        -------
        None.

        """
        time_data = self.__data_time__(slice(10,11),"T",slice(0,10),return_ints=False)
        self.__table__(time_data,max_rows=number_of_days,sort_by_likes=True)
        
    def days_range(self,start_date,finish_date): 
        """ 
        Conducts analysis on all days between start_date and finish_date inclusive.
        start_date and finish_date MUST be in same year
        (or start_date in December and finish_date in January of following year).

        Parameters
        ----------
        start_date : string
            The date to match - YYYY-MM-DD.
        finish_date : string
            The date to match - YYYY-MM-DD.

        Returns
        -------
        None.

        """
        time_data = []
        if start_date[0:5] == finish_date[0:5]:
            for month in range(int(start_date[5:7]),int(finish_date[5:7])+1):
                month = str(month)
                month = "0"*(2-len(month)) + month
                if start_date[5:7] == finish_date[5:7]: #if same month
                    for day in range(int(start_date[8:10]),int(finish_date[8:10])+1):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == start_date[5:7]: #if on starting month
                    for day in range(int(start_date[8:10]),32):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == finish_date[5:7]: #if on finishing month
                    for day in range(1,int(finish_date[8:10])+1):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                else:
                    for day in range(0,32): #include all days in month
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
        else:
            for day in range(int(start_date[8:10]),32): #include all days in starting month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = start_date[0:8] + day
                time_data += self.__data_time__(slice(0,10),match_date,slice(0,10),return_ints=False)
            for day in range(1,int(finish_date[8:10])+1): #include all days in finishing month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = finish_date[0:8] + day
                time_data += self.__data_time__(slice(0,10),match_date,slice(0,10),return_ints=False)
            
        self.__graph__(time_data,start_date+" to "+finish_date,"Day")
        #self.__graph_boxplot__(time_data,start_date+" to "+finish_date,"Day")
        print("Between",start_date,"and",finish_date,"inclusive:")
        self.__table__(time_data)
        
    def months(self,year):
        """
        Conducts analysis on months.

        Parameters
        ----------
        year : string
            The data to match - can be YYYY or empty for all time.

        Returns
        -------
        None.

        """
        if len(year) == 4:
            time_data = self.__data_time__(slice(0,4),year,slice(5,7))
        else:
            time_data = self.__data_time__(slice(10,11),"T",slice(0,7),return_ints=False)
            year = "all time"
        self.__graph__(time_data,year,"Month")
        #self.__graph_boxplot__(time_data,year,"Month")
        self.__table__(time_data)
        
    def best_friends(self):
        """
        Conducts best friends analysis.

        Returns
        -------
        None.

        """
        user_data = self.__data_user__()
        while self.username in user_data:
            user_data.remove(self.username)
        self.__table__(user_data,sort_by_likes=True) #add graphs?
        
    def worst_friends(self):
        """
        Conducts worst friend analysis (basically same as best friend but sorting low to high).

        Returns
        -------
        None.

        """
        user_data = self.__data_user__()
        while self.username in user_data:
            user_data.remove(self.username)
        self.__table__(user_data,sort_by_likes=True,sort="desc")
        
    def auto_analysis_time(self):
        """
        Conducts all time analysis for all time and yearly for each year.

        Returns
        -------
        None.

        """
        self.timezone_test()
        #do all time analysis here
        self.hours("")
        self.months("")
        self.top_days()

        for year in range(self.min_year,self.max_year+1):
            year = str(year)
            self.hours(year)
            self.day_of_week_hours(year)
            self.day_of_week(year)
            self.months(year)
        print("#"*10,"Automated Analysis Finished","#"*10)
        
#Below are all the public methods of Analysis
analysis_object = Analysis()#media_likes = False, comment_likes = False, comments = False, stories = False, 
                 #posts = False, direct = False, messages = False, chaining_seen = False, followers = False)
#analysis_object.change_settings()
#analysis_object.read_settings()
#analysis_object.json_file_structure(analysis_object.messages_json_data[0]["conversation"])
#analysis_object.profile_summary()
#analysis_object.top_message()
#analysis_object.timezone_test()
#analysis_object.date_range()
#analysis_object.hours_minutes()
#analysis_object.hours()
#analysis_object.day_of_week_hours()
#analysis_object.day_of_week()
#analysis_object.days()
#analysis_object.top_days()
#analysis_object.days_range("2018-12-27","2019-01-06") #AMC 2018 ("2019-12-27","2020-01-05") #AMC 2019
#analysis_object.months("")
#analysis_object.best_friends()
#analysis_object.worst_friends()
analysis_object.auto_analysis_time()

"""
settings test code
settings1 = analysis_object.read_settings()
print(settings1)
analysis_object.change_settings(media_likes=False)
settings2 = analysis_object.read_settings()
print(settings2)
analysis_object.change_settings(settings = settings1)
settings3 = analysis_object.read_settings()
print(settings3)
"""

#below code does hours analysis on every day individually in 2020
#for x in range(1,5):
#    for y in range(1,32):
#        analysis_object.hours("2020-"+(2-len(str(x)))*"0"+str(x)+"-"+(2-len(str(y)))*"0"+str(y))
