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
                        time_data.append(current_datetime[slice_keep])
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
        if len(year_month_day) == 10:
            time_data = self._data_time(slice(0,10),year_month_day,slice(11,16),return_ints=False)
        elif len(year_month_day) == 7:#year-month
            time_data = self._data_time(slice(0,7),year_month_day,slice(11,16),return_ints=False)
        else:
            time_data = self._data_time(slice(10,11),"T",slice(11,16),return_ints=False)
        #util.graph(time_data,year_month_day,"Hour:Minute")
        util.table(time_data,print_latex=self.print_latex)
        
    def hours(self,year_month_day):
        """
        Conducts analysis on hours.

        Parameters
        ----------
        year_month_day : string
            The data to match - can be YYYY-MM-DD, YYYY-MM, YYYY or empty for all time..

        """
        if len(year_month_day) == 10:#year-month-day
            time_data = self._data_time(slice(0,10),year_month_day,slice(11,13))
        elif len(year_month_day) == 7:#year-month
            time_data = self._data_time(slice(0,7),year_month_day,slice(11,13))
        elif len(year_month_day) == 4:#year
            time_data = self._data_time(slice(0,4),year_month_day,slice(11,13))
        else:#all of time
            time_data = self._data_time(slice(10,11),"T",slice(11,13))
            year_month_day = "all time"
            
        util.graph(time_data,year_month_day,"Hour",xtick_max=24,ylabel=self.ylabel)
        util.table(time_data,missing_data_items=(24-len(np.unique(time_data))),print_latex=self.print_latex)
        util.graph_boxplot(time_data,year_month_day,"Hour",xtick_max=24)
    
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
        if len(year_month) == 4:
            time_data = self._data_time(slice(0,4),year_month,slice(5,13),return_ints=False)#,return_counts=True)
            for month_day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:5]))
                days_of_week.append([day_datetime.isoweekday(),month_day[-2:]])
        else:
            time_data = self._data_time(slice(0,7),year_month,slice(8,13),return_ints=False)        
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
                util.graph(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)),xtick_max=24,ylabel=self.ylabel)
                util.graph_boxplot(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)),xtick_max=24)
                print("Day of week",day_of_week)
                util.table(hours[day_of_week-1],missing_data_items=(24-len(np.unique(hours[day_of_week-1]))),print_latex=self.print_latex)
        
        workday_hours = hours[0]+hours[1]+hours[2]+hours[3]+hours[4]
        util.graph(workday_hours,year_month,"hour during the week(Monday-Friday)",xtick_max=24,ylabel=self.ylabel)
        util.graph_boxplot(workday_hours,year_month,"hour during the week(Monday-Friday)",xtick_max=24)
        print("Weekdays(Monday-Friday)")
        util.table(workday_hours,missing_data_items=(24-len(np.unique(workday_hours))),print_latex=self.print_latex)
        
        weekend_hours = hours[5] + hours[6]
        util.graph(weekend_hours,year_month,"hour during the weekend",xtick_max=24,ylabel=self.ylabel)
        util.graph_boxplot(weekend_hours,year_month,"hour during the weekend",xtick_max=24)
        print("Weekend")
        util.table(weekend_hours,missing_data_items=(24-len(np.unique(weekend_hours))),print_latex=self.print_latex)
        
    
    def day_of_week(self,year_month):
        """
        Conducts analysis by day of week.

        Parameters
        ----------
        year_month : string
            The data to match YYYY or YYYY-MM.

        """
        day_of_week = []
        if len(year_month) == 4:
            time_data = self._data_time(slice(0,4),year_month,slice(5,10),return_ints=False)
            for month_day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:]))
                day_of_week.append(day_datetime.isoweekday())
        else:
            time_data = self._data_time(slice(0,7),year_month,slice(8,10),return_ints=False)        
            for day in time_data:
                day_datetime = datetime.date(int(year_month[:4]),int(year_month[5:7]),int(day))
                day_of_week.append(day_datetime.isoweekday())
        util.graph(day_of_week,year_month,"Day of Week",ylabel=self.ylabel)#,style = "xb")
        util.table(day_of_week,print_latex=self.print_latex)
        
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
        util.table(time_data,print_latex=self.print_latex)
        
    def top_days(self,number_of_days=25):
        """
        Prints a table of the dates of the days with the most activity.
        
        Parameters
        ----------
        number_of_days : string, optional
            The number of days to display. The default is 25.

        """
        time_data = self._data_time(slice(10,11),"T",slice(0,10),return_ints=False)
        util.table(time_data,max_rows=number_of_days,sort_by_likes=True,print_latex=self.print_latex)
        
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
                        time_data += self._data_time(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == start_date[5:7]: #if on starting month
                    for day in range(int(start_date[8:10]),32):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self._data_time(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == finish_date[5:7]: #if on finishing month
                    for day in range(1,int(finish_date[8:10])+1):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self._data_time(slice(0,10),match_date,slice(5,10),return_ints=False)
                else:
                    for day in range(0,32): #include all days in month
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        time_data += self._data_time(slice(0,10),match_date,slice(5,10),return_ints=False)
        else:
            for day in range(int(start_date[8:10]),32): #include all days in starting month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = start_date[0:8] + day
                time_data += self._data_time(slice(0,10),match_date,slice(0,10),return_ints=False)
            for day in range(1,int(finish_date[8:10])+1): #include all days in finishing month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = finish_date[0:8] + day
                time_data += self._data_time(slice(0,10),match_date,slice(0,10),return_ints=False)
            
        util.graph(time_data,start_date+" to "+finish_date,"Day",ylabel=self.ylabel)
        #util.graph_boxplot(time_data,start_date+" to "+finish_date,"Day")
        print("Between",start_date,"and",finish_date,"inclusive:")
        util.table(time_data,print_latex=self.print_latex)
        
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
        if len(year) == 4:
            time_data = self._data_time(slice(0,4),year,slice(5,7))
            util.graph(time_data,year,"Month",xtick_min=1,xtick_max=13,ylabel=self.ylabel)
        else:
            time_data = self._data_time(slice(10,11),"T",slice(0,7),return_ints=False)
            year = "all time"
            util.graph(time_data,year,"Month",ylabel=self.ylabel)
        #util.graph_boxplot(time_data,year,"Month")
        util.table(time_data,print_latex=self.print_latex)
        
    def years(self):
        """
        Conducts analysis on years.
        """
        time_data = self._data_time(slice(10,11),"T",slice(0,4))
        util.graph(time_data,"all time","Year",xtick_min=self.min_year,xtick_max=self.max_year+1,ylabel=self.ylabel)
        util.table(time_data,print_latex=self.print_latex)
        
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
            
    def auto_analysis(self):
        """
        Conducts all analysis for all time and yearly for each year.
        """
        self.timezone_test()
        #do all time analysis here
        self.hours("")
        self.months("")
        self.year()
        self.top_days()
        self.connections("")

        for year in range(self.min_year,self.max_year+1):
            self.yearly_analysis(str(year))

        print("#"*10,"Automated Analysis Finished","#"*10)
        
#Below are all the public methods of Analysis
# "anon_data//anon_"
analysis_time_object = AnalysisTime(path="")#, media_likes = False, comment_likes = False, comments = False, stories = False, 
                         #posts = False, direct = False, messages = False, message_likes = False, chaining_seen = False, followers = False, following=True)
event_list = [("2018-01-27","2018-01-28"),("2018-04-06","2018-04-14"),("2018-05-11","2018-05-13"),("2018-06-08","2018-06-10"),("2018-07-12","2018-07-13"),
              ("2018-07-20","2018-07-22"),("2018-07-29","2018-08-05"),("2018-08-13","2018-08-16"),("2018-08-20","2018-08-22"),("2018-09-15","2018-09-16"),
              ("2018-09-21","2018-09-22"),("2018-10-05","2018-10-07"),("2018-11-02","2018-11-03"),("2018-12-28","2019-01-05"),("2019-02-22","2019-02-24"),
              ("2019-03-01","2019-03-03"),("2019-03-30","2019-03-31"),("2019-06-19","2019-06-20"),("2019-06-21","2019-06-23"),("2019-07-12","2019-07-14"),
              ("2019-08-03","2019-08-05"),("2019-08-09","2019-08-17"),("2019-09-21","2019-09-23"),("2019-10-04","2019-10-06"),("2019-10-21","2019-10-24"),
              ("2019-12-28","2020-01-04")]
#analysis_time_object.change_settings()
#analysis_time_object.read_settings()
#analysis_time_object.data_sources()
#analysis_time_object.timezone_test()
#analysis_time_object.date_range()
#analysis_time_object.hours_minutes()
#analysis_time_object.hours("")
#analysis_time_object.day_of_week_hours()
#analysis_time_object.day_of_week()
#analysis_time_object.days("2020-01")
#analysis_time_object.top_days()
#analysis_time_object.days_range("2018-12-27","2019-01-06") #AMC 2018 ("2019-12-27","2020-01-05") #AMC 2019
#analysis_time_object.events(event_list)
#analysis_time_object.months("")
#analysis_time_object.years()
#analysis_time_object.connections("2017",followers=True,following=True)
#analysis_time_object.yearly_analysis("2017")
#analysis_time_object.auto_analysis()

#util.json_file_structure(analysis_time_object.media_json_data["photos"])
