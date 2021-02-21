#analysis_time.py by Ryan Traviss
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
    I have not attempted to round numbers as its actually really HARD to do properly!
        eg. round(0.0750,2) -> 0.07 which is just wrong
        Just do it yourself and don't be lazy aha.
""" 

"""
Post Mode (self.post_mode) Documentation
    This is to explain the variable post_mode which determines how datetimes are extracted from posts.
    It is a string with 2 supported values: ("single" or "multiple")
    
    "single" : This means each post counts as a single datetime regardless of how many photos it contains.
            This is checked by comparing the datetimes (excluding minutes, seconds, timezone) of 
            posts next to each other. 
            (It appears Instagram can record diffrent minutes for diffrent photos in the same post
            and this lead to errors so thus only down to hours is used)
            
    "multiple" : Each photo within a post (which can contain up to 10) is counted as a datetime.
    
    I see no reason why posts should have different weightings in the results 
    based on the number of photos they contain so "single" is the default mode.
"""

import json, numpy as np, datetime
import util
import copy

class AnalysisTime:
    def __init__(self, path = "", likes_filename = "likes.json", comments_filename = "comments.json", 
                 media_filename = "media.json", seen_content_filename = "seen_content.json", 
                 profile_filename = "profile.json", messages_filename = "messages.json", connections_filename = "connections.json",
                 media_likes = True, comment_likes = True, comments = True,
                 stories = True, posts = True, post_mode = "single", 
                 direct = True, chaining_seen = True, messages = True,
                 message_likes = True, followers = False, following = False, print_latex = False):
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
        message_likes : Boolean, optional
            Should when you have liked messages be used. The default is True.
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
        self.stories = stories
        self.posts = posts
        self.post_mode = post_mode
        self.direct = direct
        self.chaining_seen = chaining_seen
        self.messages = messages
        self.message_likes = message_likes
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
        self.min_year, self.max_year = self._min_max_year()
        
        self.ylabel = "Activity"
        #This is an attribute so it can be altered easily by methods 
        #which set certain data sources to be used such as connections()
        #without needing to be passed as a parameter to every other method
        self.print_lists = True
        
    def _min_max_year(self):
        """
        Returns the oldest year and most recent year in the selected data.

        Returns
        -------
        int, int
            oldest year, most recent year

        """
        years = self._data_time(slice(10,11), "T", slice(0,4), return_ints=True)
        if years != []:
            years = np.unique(years, return_counts=False)
            return min(years), max(years)
        else:
            print("Error: No data")
            return 0,0
        
    def change_settings(self, media_likes = True, comment_likes = True, comments = True, stories = True, 
                 posts = True, post_mode = "single", direct = True, chaining_seen = True, messages = True,
                 message_likes = True, followers = True, following = True, print_latex = False, settings=()):
        """
        Updates the state of the variables determining which sources of data should be used.

        Parameters
        ----------
        See __init__ documentation.
        settings : Tuple, optional
            A tuple of all the other parameters that is generated from read_settings().

        """
        if settings != ():
            (self.media_likes, self.comment_likes, self.comments, 
             self.stories, self.posts, self.post_mode,
             self.direct, self.chaining_seen, self.messages,
             self.message_likes, self.followers, self.following, 
             self.print_latex) = settings
        else:
            self.media_likes = media_likes
            self.comment_likes = comment_likes
            self.comments = comments
            self.stories = stories
            self.posts = posts
            self.post_mode = post_mode
            self.direct = direct
            self.chaining_seen = chaining_seen
            self.messages = messages
            self.message_likes = message_likes
            self.followers = followers
            self.following = following
            self.print_latex = print_latex
        
        self.min_year, self.max_year = self._min_max_year()
        
    def read_settings(self):
        """
        Returns all the setttings currently being used as a tuple.

        Returns
        -------
        See __init__() documentation.

        """
        return (self.media_likes, self.comment_likes, self.comments, 
        self.stories, self.posts, self.post_mode,
        self.direct, self.chaining_seen, self.messages,
        self.message_likes,
        self.followers, self.following, self.print_latex)
    
    def _extract_data(self, json_data, slice_match, match, slice_keep):
        return_data = []
        for i in range(len(json_data)):
            if json_data[i][0][slice_match] == match:
                return_data.append(json_data[i][0][slice_keep])
        return return_data   
        
    def _data_time(self, slice_match, match, slice_keep, return_ints=True):
        """
        Extracts the right part of the timestamp from the data

        Parameters
        ----------
        slice_match : Slice
            The slice of the datetime to compare (if match == "" then set to slice(10,11)).
        match : String
            What should the datetime fragment equal (if "" then set to "T").
        slice_keep : Slice
            What slice of the datetime should be returned.
        return_ints : Boolean, optional
            Should the list being returned be a list of integers. The default is True.

        Returns
        -------
        List (if return_ints then integers else strings)
            A list of selected fragments of the datetime.

        """
        if match == "":
            slice_match = slice(10,11)
            match = "T"
        time_data = []
        
        if self.media_likes:
            time_data.extend(self._extract_data(self.likes_json_data["media_likes"],slice_match, match, slice_keep))

        if self.comment_likes:
            time_data.extend(self._extract_data(self.likes_json_data["comment_likes"],slice_match, match, slice_keep))
           
        if self.comments:
            time_data.extend(self._extract_data(self.comments_json_data["media_comments"],slice_match, match, slice_keep))
                   
        if self.stories:
            for x in range(len(self.media_json_data["stories"])):
                if self.media_json_data["stories"][x]["taken_at"][slice_match] == match:
                    time_data.append(self.media_json_data["stories"][x]["taken_at"][slice_keep])
                    
        if self.posts: #see documentation at top about post modes
            previous_datetime = ""
            for x in range(len(self.media_json_data["photos"])):
                if self.post_mode == "multiple": 
                    if self.media_json_data["photos"][x]["taken_at"][slice_match] == match:
                        time_data.append(self.media_json_data["photos"][x]["taken_at"][slice_keep])
                elif self.post_mode == "single":
                    current_datetime = self.media_json_data["photos"][x]["taken_at"][0:13]
                    if current_datetime[slice_match] == match and current_datetime != previous_datetime:
                        time_data.append(self.media_json_data["photos"][x]["taken_at"][slice_keep])
                    previous_datetime = current_datetime
                        
        
        if self.direct:
            for x in range(len(self.media_json_data["direct"])):
                if self.media_json_data["direct"][x]["taken_at"][slice_match] == match:
                    time_data.append(self.media_json_data["direct"][x]["taken_at"][slice_keep])
        
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
        
    def data_sources(self):#this is done in an awful way!
        def get_all_time_data(self,true_index,data_source,settings):
            settings[true_index] = True
            self.change_settings(settings = settings)
            return [data_source]*len(self._data_time(slice(10,11),"T",slice(0,4)))
        
        original_settings = self.read_settings()
        data_sources_array = []
        false_settings = [False, False, False, False, 
                          False, "single", False, False, False,
                          False, False, False, False]
        
        data_sources_array.extend(get_all_time_data(self,0,"media_likes",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,1,"comment_likes",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,2,"comments",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,3,"stories",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,4,"posts - single",false_settings.copy()))
        false_settings[5] = "multiple"
        data_sources_array.extend(get_all_time_data(self,4,"posts - multiple",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,6,"direct",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,7,"chaining_seen",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,8,"messages",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,9,"message_likes",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,10,"followers",false_settings.copy()))
        data_sources_array.extend(get_all_time_data(self,11,"following",false_settings.copy()))
        
        self.change_settings(original_settings)
        util.table(data_sources_array,sort_by_likes=True)
        
    def timezone_test(self):
        """
        Prints all of the timezones when I liked a post/comment.

        """
        timezones = self._data_time(slice(10,11), "T", slice(19,26), return_ints=False)
        print("This is a list of all the times zones for which there is a piece of data:")
        print(np.unique(timezones, return_counts=False))
        
    def date_range(self):
        """
        Prints the oldest and most recent piece of data and the time between.

        """
        dates = self._data_time(slice(10,11), "T", slice(0,19), return_ints=False)
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

        """
        time_data = self._data_time(slice(0,len(year_month_day)),year_month_day,slice(11,16),return_ints=False)
        #util.graph(time_data,year_month_day,"Hour:Minute")
        util.table(time_data,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def hours(self,year_month_day):
        """
        Conducts analysis on hours.

        Parameters
        ----------
        year_month_day : string
            The data to match - can be YYYY-MM-DD, YYYY-MM, YYYY or empty for all time..

        """
        time_data = self._data_time(slice(0,len(year_month_day)),year_month_day,slice(11,13))
        util.graph_histogram(time_data,util.date_to_time_period(year_month_day),"Hour", self.ylabel)
        util.table(time_data,missing_data_items=(24-len(np.unique(time_data))), print_latex=self.print_latex, print_lists=self.print_lists)
        util.graph_boxplot(time_data,util.date_to_time_period(year_month_day),"Hour",xtick_max=24)
    
    def day_of_week_hours(self,year_month,graph_per_day=False):
        """
        Conducts hours analysis by day of week (optional) and weekday vs weekend.

        Parameters
        ----------
        year_month : string
            The data to match YYYY or YYYY-MM.
        graph_per_day : boolean, optional
            Should a graph/table be produced for each day of the week. The default is False.

        """
        days_of_week = []
        
        
        time_data = self._data_time(slice(0,len(year_month)),year_month,slice(0,13),return_ints=False)
        for date_time in time_data:
            day_datetime = datetime.date(int(date_time[:4]),int(date_time[5:7]),int(date_time[8:10]))
            days_of_week.append([day_datetime.isoweekday(),date_time[-2:]])
        
        if year_month == "":
            year_month = "all time"
        
        hours = [[],[],[],[],[],[],[]]
        for day_of_week in range(1,8):
            for day_of_week_hour in days_of_week:
                if day_of_week_hour[0] == day_of_week:
                    hours[day_of_week-1].append(day_of_week_hour[1])
            hours[day_of_week-1] = list(map(int,hours[day_of_week-1]))
            if graph_per_day:
                util.graph_histogram(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)),self.ylabel)
                util.graph_boxplot(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)),xtick_max=24)
                print("Day of week",day_of_week)
                util.table(hours[day_of_week-1],missing_data_items=(24-len(np.unique(hours[day_of_week-1]))),print_latex=self.print_latex, print_lists=self.print_lists)
        
        workday_hours = hours[0]+hours[1]+hours[2]+hours[3]+hours[4]
        util.graph_histogram(workday_hours,year_month,"hour during the week(Monday-Friday)",self.ylabel)
        util.graph_boxplot(workday_hours,year_month,"hour during the week(Monday-Friday)",xtick_max=24)
        print("Weekdays(Monday-Friday)")
        util.table(workday_hours,missing_data_items=(24-len(np.unique(workday_hours))),print_latex=self.print_latex, print_lists=self.print_lists)
        
        weekend_hours = hours[5] + hours[6]
        util.graph_histogram(weekend_hours,year_month,"hour during the weekend",self.ylabel)
        util.graph_boxplot(weekend_hours,year_month,"hour during the weekend",xtick_max=24)
        print("Weekend")
        util.table(weekend_hours,missing_data_items=(24-len(np.unique(weekend_hours))),print_latex=self.print_latex, print_lists=self.print_lists)
        
    
    def day_of_week(self,year_month):
        """
        Conducts analysis by day of week.

        Parameters
        ----------
        year_month : string
            The data to match YYYY or YYYY-MM.

        """
        day_of_week = []
        time_data = self._data_time(slice(0,len(year_month)),year_month,slice(0,10),return_ints=False)
        for date in time_data:
            day_datetime = datetime.date(int(date[:4]),int(date[5:7]),int(date[8:10]))
            day_of_week.append(day_datetime.isoweekday())
        util.graph_histogram(day_of_week,year_month,"Day of Week",self.ylabel, xtick_min =1, xtick_max=8)#,style = "xb")
        util.table(day_of_week,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def days(self,year_month):
        """
        Conducts analysis on days.

        Parameters
        ----------
        year_month : string
            The data to match - YYYY-MM.

        """
        time_data = self._data_time(slice(0,7),year_month,slice(8,10))
        util.graph(time_data,year_month,"Day",ylabel=self.ylabel)
        util.graph_boxplot(time_data,year_month,"Day")
        util.table(time_data,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def top_days(self,number_of_days=25):
        """
        Prints a table of the dates of the days with the most activity.
        
        Parameters
        ----------
        number_of_days : string, optional
            The number of days to display. The default is 25.

        """
        time_data = self._data_time(slice(10,11),"T",slice(0,10),return_ints=False)
        util.table(time_data,max_rows=number_of_days,sort_by_likes=True,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def days_range(self,start_date,finish_date): 
        """ 
        Conducts analysis on all days between start_date and finish_date inclusive.

        Parameters
        ----------
        start_date : string
            The date to match - YYYY-MM-DD.
        finish_date : string
            The date to match - YYYY-MM-DD.

        """
        time_data = []
        for year in range(int(start_date[:4]),int(finish_date[:4])+1):
            if year == int(start_date[:4]):
                start_month = int(start_date[5:7])
            else:
                start_month = 1
            if year == int(finish_date[:4]):
                finish_month = int(finish_date[5:7])
            else:
                finish_month = 12
                
            for month in range(start_month,finish_month+1):
                year_month = str(year) +"-" + "0"*(2-len(str(month))) + str(month)
            
                if year_month == start_date[0:7]:
                    start_day = int(start_date[8:10])
                else:
                    start_day = 1
                    
                if year_month == finish_date[0:7]:
                    finish_day = int(finish_date[8:10])
                else:
                    finish_day = 31
        
                for day in range(start_day, finish_day+1):
                    date = year_month + "-" + "0"*(2-len(str(day))) + str(day)
                    time_data += self._data_time(slice(0,10),date,slice(0,10),return_ints=False)
        
        util.graph(time_data,start_date+" to "+finish_date,"Day",ylabel=self.ylabel)
        #util.graph_boxplot(time_data,start_date+" to "+finish_date,"Day")
        print("Between",start_date,"and",finish_date,"inclusive:")
        util.table(time_data,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def events(self,event_list):
        """
        Conducts analysis on a list of events using days_range.

        Parameters
        ----------
        event_list : List of tuples of strings
            Each tuple in the list is made up of the start date and finish date of the event.

        Returns
        -------
        None.

        """
        for i in range(len(event_list)):
            self.days_range(event_list[i][0],event_list[i][1])
        
    def months(self,year):
        """
        Conducts analysis on months.

        Parameters
        ----------
        year : string
            The data to match - can be YYYY or empty for all time.

        """
        time_data = self._data_time(slice(0,len(year)),year,slice(5,7))
        if len(year) == 4:
            util.graph(time_data,year,"Month",xtick_min=1,xtick_max=13,ylabel=self.ylabel)
        else:
            year = "all time"
            util.graph(time_data,year,"Month",xtick_min=1,xtick_max=13,ylabel=self.ylabel)
        #util.graph_boxplot(time_data,year,"Month")
        util.table(time_data,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def years(self):
        """
        Conducts analysis on years.
        """
        time_data = self._data_time(slice(10,11),"T",slice(0,4))
        util.graph(time_data,"all time","Year",xtick_min=self.min_year,xtick_max=self.max_year+1,ylabel=self.ylabel)
        util.table(time_data,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def connections(self,year,followers=True,following=True):
        """
        Conducts analysis on connections.

        Parameters
        ----------
        year : string
            The year (or all time if empty) to analyise.
        followers : boolean, optional
            Should followers be used. The default is True.
        following : boolean, optional
            Should following be used. The default is True.

        """
        original_settings = self.read_settings()
        if followers and following:
            print("Connections Analysis")
            self.change_settings(settings=(False, False, False, False, False, "", False, False, False, False, True, True, False))
            self.ylabel = "Connections"
        elif followers:
            print("Followers Analysis")
            self.change_settings(settings=(False, False, False, False, False, "", False, False, False, False, True, False, False))
            self.ylabel = "Followers"
        elif following:
            print("Following Analysis")
            self.change_settings(settings=(False, False, False, False, False, "", False, False, False, False, False, True, False))
            self.ylabel = "Following"
        else:
            print("Error: followers or following must be used")
            return
            
        if len(year) == 4:
            self.months(year)
        else:
            self.years()
            
        self.change_settings(settings=original_settings)
        self.ylabel = "Activity"
        
    def breaks(self,date,min_break=datetime.timedelta(days=1)):
        """
        Conducts analysis on breaks I have taken from Instagram.

        Parameters
        ----------
        date : string
            When should the analysis cover - empty string for all time.
        min_break : datetime.timedelta, optional
            What is the minimum break that should be included. The default is datetime.timedelta(days=1).

        """
        time_data = self._data_time(slice(0,len(date)),date, slice(0,19),return_ints=False)
        time_data.sort(reverse=True)
        time_data = [datetime.datetime.strptime(datestamp, "%Y-%m-%dT%H:%M:%S") for datestamp in time_data]
        
        max_break = datetime.timedelta(seconds=0)
        break_start = ""
        breaks = ([],[])
        
        for i in range(len(time_data)-1):
            break_length = time_data[i] - time_data[i+1]
            break_length_hours = break_length.days * 24 + break_length.seconds//3600
            if break_length > min_break:
                breaks[0].append(time_data[i].strftime("%Y-%m-%d"))
                breaks[1].append(break_length_hours)
                
        breaks[0].reverse()
        breaks[1].reverse()
        util.graph(breaks,util.date_to_time_period(date), "day", ylabel="hours break",unique=True)
        util.table(breaks,sort_by_likes=True,unique=True,print_latex=self.print_latex, print_lists=self.print_lists)
        
    def daily_correlation(self):
        """
        Determines the pmcc between days since account creation and usage + displays linegraph with line of best fit.
        """
        delta = datetime.datetime(2020, 4, 27) - datetime.datetime(2017, 7, 19) + datetime.timedelta(days=1)
        daily_data = self._data_time(slice(0,1), "", slice(0,10), return_ints=False)
        days_since_account_creation = list(range(delta.days))
        daily_activity = []
        for i in range(delta.days):
            date = datetime.datetime.strftime(datetime.datetime(2017, 7, 19)+datetime.timedelta(days=i), "%Y-%m-%d")
            #print(date, i, daily_data.count(date))
            daily_activity.append(daily_data.count(date))
        
        print(self.ylabel, round(np.corrcoef(days_since_account_creation, daily_activity)[0][1], 4))
        
        util.graph((days_since_account_creation, daily_activity), "all time", "Day", ylabel=self.ylabel, unique=True, line_of_best_fit=True)
        
        util.graph_histogram_2(daily_activity, ylabel=self.ylabel)
        
    def yearly_analysis(self, year):
        """
        Conducts all analysis for a year.

        Parameters
        ----------
        year : string
            The year to be analyised.

        """
        self.hours(year)
        self.day_of_week_hours(year)
        self.day_of_week(year)
        self.months(year)
        self.connections(year)
        self.breaks(year)
            
    def auto_analysis(self):
        """
        Conducts all analysis for all time and yearly for each year.
        """
        self.timezone_test()
        #do all time analysis here
        self.hours("")
        self.day_of_week_hours("")
        self.day_of_week("")
        self.months("")
        self.year()
        self.top_days()
        self.connections("")
        self.breaks("")

        for year in range(self.min_year,self.max_year+1):
            self.yearly_analysis(str(year))

        print("#"*10,"Automated Analysis Finished","#"*10)
        
#Below are all the public methods of Analysis
analysis_time_object = AnalysisTime()#media_likes = False, comment_likes = False, comments = False, stories = False, 
                         #posts = False, direct = False, messages = False, message_likes = False, chaining_seen = False, followers = True, following=True, print_latex=False)
event_list = [("2018-01-27","2018-01-28"),("2018-04-06","2018-04-14"),("2018-05-11","2018-05-13"),("2018-06-08","2018-06-10"),("2018-07-12","2018-07-13"),
              ("2018-07-20","2018-07-22"),("2018-07-29","2018-08-05"),("2018-08-13","2018-08-16"),("2018-08-20","2018-08-22"),("2018-09-15","2018-09-16"),
              ("2018-09-21","2018-09-22"),("2018-10-05","2018-10-07"),("2018-11-02","2018-11-03"),("2018-12-28","2019-01-05"),("2019-02-22","2019-02-24"),
              ("2019-03-01","2019-03-03"),("2019-03-30","2019-03-31"),("2019-06-19","2019-06-20"),("2019-06-21","2019-06-23"),("2019-07-12","2019-07-14"),
              ("2019-08-03","2019-08-05"),("2019-08-09","2019-08-17"),("2019-09-21","2019-09-23"),("2019-10-04","2019-10-06"),("2019-10-21","2019-10-24"),
              ("2019-12-28","2020-01-04")]

event_day_either_side_list = [("2018-01-26","2018-01-29"),("2018-04-05","2018-04-15"),("2018-05-10","2018-05-14"),("2018-06-07","2018-06-11"),("2018-07-11","2018-07-14"),
              ("2018-07-19","2018-07-23"),("2018-07-28","2018-08-06"),("2018-08-12","2018-08-17"),("2018-08-19","2018-08-23"),("2018-09-14","2018-09-17"),
              ("2018-09-20","2018-09-23"),("2018-10-04","2018-10-08"),("2018-11-01","2018-11-04"),("2018-12-27","2019-01-06"),("2019-02-21","2019-02-25"),
              ("2019-02-28","2019-03-04"),("2019-03-29","2019-04-01"),("2019-06-18","2019-06-21"),("2019-06-20","2019-06-24"),("2019-07-11","2019-07-15"),
              ("2019-08-02","2019-08-06"),("2019-08-08","2019-08-18"),("2019-09-20","2019-09-24"),("2019-10-03","2019-10-07"),("2019-10-20","2019-10-25"),
              ("2019-12-27","2020-01-05")]
#analysis_time_object.change_settings()
#analysis_time_object.read_settings()
#analysis_time_object.data_sources()
#analysis_time_object.timezone_test()
#analysis_time_object.date_range()
#analysis_time_object.hours_minutes()
#analysis_time_object.hours("")
#analysis_time_object.day_of_week_hours("")
#analysis_time_object.days_range("2018-04-05","2018-04-15")#("2019-08-08","2019-08-18")#("2019-10-03", "2019-10-07")##("2019-01-01","2019-12-31")##
#analysis_time_object.day_of_week("2020")
#analysis_time_object.days("2017-07")
#analysis_time_object.top_days(number_of_days=40)
#("2017-07-20","2017-12-31")## #AMC 2019
#analysis_time_object.events(event_list)
#analysis_time_object.months("2020")
#analysis_time_object.years()
#analysis_time_object.connections("2020",followers=True,following=True)
#analysis_time_object.breaks("",min_break=datetime.timedelta(hours=24))
#analysis_time_object.daily_correlation()
#analysis_time_object.yearly_analysis("2017")
analysis_time_object.auto_analysis()

#util.json_file_structure(analysis_time_object.seen_content_json_data["chaining_seen"])
