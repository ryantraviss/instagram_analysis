#instagram_analysis by Ryan Traviss
"""
Notes:
    2017-07-19T08:57:05 was when I made my account in format YYYY-MM-DDThh:mm:ss
    the timezone for my data is always +00:00
    I have liked 8242 posts and 223 comments from 556 diffrent accounts
    I have made 285 comments.
    seen_content "ads_seen", "posts_seen", "videos_watched" are only for more recent period
    example comment: ['2020-04-24T15:39:04+00:00', '@username How much lag is there on that server?', 'username']
"""

"""
To do(code):
    make graphs title properly for all the new types of data.
    add connections data
    use account_history ?
    use 'profile' from media.json ? only 1 thing there
    analyize captions / text of comments?
    maybe add stories_activities but will have small effect
        / may not have been possible since beginning
    use messages data?
    add user data stuff
    fix xticks properly
    Is there any way of getting who I have tagged in an image? 
        Would be VERY useful for best friends...
    I'm still unsure of what chaining_seen even is...
    
"""

"""
Comment Mode Documentation
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
Post Mode Documentation
    This is to explain the variable post_mode which determines how datetimes are extracted from posts.
    It is a string with 2 supported values: ("single" or "multiple")
    
    "single" : This means each post counts as a single datetime regardless of how many photos it contains.
            This is checked by comparing the datetimes (excluding minutes, seconds, timezone) and captions of 
            posts next to each other. 
            (It appears Instagram can record diffrent minutes for diffrent photos in the same post
            and this lead to errors so thus why caption is also used. 
            Captions alone are not neccesarily unique amongst a user's posts.)
            
    "multiple" : Each photo within a post (which can contain up to 10) is counted as a datetime.
    
    I see no reason why posts should have diffrent weightings in the results 
    based on the number of photos they contain so "single" is the default mode.

"""

import json, matplotlib.pyplot as plt, numpy as np, datetime, statistics

class Analysis:
    def __init__(self, path = "", likes_filename = "likes.json", comments_filename = "comments.json", 
                 posts_filename = "media.json", seen_content_filename = "seen_content.json", profile_filename = "profile.json",
                 likes_media = True, likes_comment = True, comments = True, comment_mode = "smart", stories = True, 
                 posts = True, post_mode = "single", direct = True, chaining_seen = True, print_latex = False):
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
        likes_media : Boolean, optional
            Should likes on posts be used (called media_likes in JSON data). The default is True.
        likes_comment: Boolean, optional
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
        direct: Boolean, optional
            Should pictures sent as direct messages be used. The default is True.
        chaining_seen: Boolean, optional
            Should links followed on Instagram be used. The default is True.
        print_latex : Boolean, optional
            Should the latex to make the tables be printed. Default False.
        Returns
        -------
        None.

        """
        self.likes_media = likes_media
        self.likes_comment = likes_comment
        self.comments = comments
        self.comment_mode = comment_mode
        self.stories = stories
        self.posts = posts
        self.post_mode = post_mode
        self.direct = direct
        self.chaining_seen = chaining_seen
        self.print_latex = print_latex
        

        self.likes_json_data = self.__read_json__(path+likes_filename)
        self.comments_json_data = self.__read_json__(path+comments_filename)
        self.posts_json_data = self.__read_json__(path+posts_filename)
        self.seen_content_json_data = self.__read_json__(path+seen_content_filename)
        self.profile_json_data = self.__read_json__(path+profile_filename)
        
        self.account_created_date = self.profile_json_data["date_joined"]
        self.min_year, self.max_year = self.__min_max_year__()
        
    def change_settings(self, likes_media = True, likes_comment = True, comments = True, comment_mode = "smart", stories = True, 
                 posts = True, post_mode = "single", direct = True, chaining_seen = True, print_latex = False):
        """
        Updates the state of the variables determining which sources of data should be used.

        Parameters
        ----------
        See __init__ documentation.

        Returns
        -------
        None.

        """
        self.likes_media = likes_media
        self.likes_comment = likes_comment
        self.comments = comments
        self.comment_mode = comment_mode
        self.stories = stories
        self.posts = posts
        self.post_mode = post_mode
        self.direct = direct
        self.chaining_seen = chaining_seen
        self.print_latex = print_latex
        
        self.min_year, self.max_year = self.__min_max_year__()
        
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
            DESCRIPTION.
        match : String
            DESCRIPTION.
        slice_keep : Slice
            DESCRIPTION.
        return_ints : Boolean, optional
            Should the list being returned be a list of integers. The default is True.

        Returns
        -------
        List (if return_ints then integers else strings)
            A list of selected fragments of the datetime.

        """
        like_times = []
        if self.likes_media:
            for x in range(len(self.likes_json_data["media_likes"])):
                if self.likes_json_data["media_likes"][x][0][slice_match] == match:
                    like_times.append(self.likes_json_data["media_likes"][x][0][slice_keep])
        if self.likes_comment:
            for x in range(len(self.likes_json_data["comment_likes"])):
                if self.likes_json_data["comment_likes"][x][0][slice_match] == match:
                    like_times.append(self.likes_json_data["comment_likes"][x][0][slice_keep])
           
        if self.comments:
            for x in range(len(self.comments_json_data["media_comments"])):
                if self.comments_json_data["media_comments"][x][0][slice_match] == match:
                    like_times.append(self.comments_json_data["media_comments"][x][0][slice_keep])
                    
        if self.stories:
            for x in range(len(self.posts_json_data["stories"])):
                if self.posts_json_data["stories"][x]["taken_at"][slice_match] == match:
                    like_times.append(self.posts_json_data["stories"][x]["taken_at"][slice_keep])
        if self.posts:
            previous_datetime = ""
            previous_caption = ""
            for x in range(len(self.posts_json_data["photos"])):
                if self.post_mode == "multiple": #see documentation at top about post modes
                    if self.posts_json_data["photos"][x]["taken_at"][slice_match] == match:
                        like_times.append(self.posts_json_data["photos"][x]["taken_at"][slice_keep])
                elif self.post_mode == "single":
                    current_datetime = self.posts_json_data["photos"][x]["taken_at"][0:13]
                    current_caption = self.posts_json_data["photos"][x]["caption"]
                    if current_datetime[slice_match] == match and current_datetime != previous_datetime and current_caption != previous_caption:
                        like_times.append(current_datetime[slice_keep])
                    previous_datetime = current_datetime
                    previous_caption = current_caption
                        
        
        if self.direct:
            for x in range(len(self.posts_json_data["direct"])):
                if self.posts_json_data["direct"][x]["taken_at"][slice_match] == match:
                    like_times.append(self.posts_json_data["direct"][x]["taken_at"][slice_keep])
        
        if self.chaining_seen:
            for x in range(len(self.seen_content_json_data["chaining_seen"])):
                if self.seen_content_json_data["chaining_seen"][x]["timestamp"][slice_match] == match:
                    like_times.append(self.seen_content_json_data["chaining_seen"][x]["timestamp"][slice_keep])

        if return_ints:
            return list(map(int,like_times)) #turns list of strings into list of integers
        else:
            return like_times
        
    def __data_user__(self):
        """
        This private method deals with getting a list of the users.
        Data is extracted from diffrent sources based on selected settings.

        Returns
        -------
        list 
            A list of users.

        """
        likes_users = []
        if self.likes_media:
            for x in range(len(self.likes_json_data["media_likes"])):
                likes_users.append(self.likes_json_data["media_likes"][x][1])
                
        if self.likes_comment:
            for x in range(len(self.likes_json_data["comment_likes"])):
                likes_users.append(self.likes_json_data["comment_likes"][x][1])
                
        if self.comments:
            for x in range(len(self.comments_json_data["media_comments"])):
                if self.comment_mode == "post": #see documentation at top of file about comment modes
                    likes_users.append(self.comments_json_data["media_comments"][x][2])
                elif self.comment_mode == "reply":
                    #The following line gets the first word of each comment and removes the first character
                    #which should be an @ if you are replying to someone and adds the rest of the word
                    #which should be a username (but isn't always if it is a top level comment)
                    likes_users.append(self.comments_json_data["media_comments"][x][1].split(" ")[0][1:])
                elif self.comment_mode == "smart":
                    if self.comments_json_data["media_comments"][x][1].split(" ")[0][0] == "@":
                        likes_users.append(self.comments_json_data["media_comments"][x][1].split(" ")[0][1:])
                    else:
                        likes_users.append(self.comments_json_data["media_comments"][x][2])
                        
        if self.chaining_seen:
            for x in range(len(self.seen_content_json_data["chaining_seen"])):
                likes_users.append(self.seen_content_json_data["chaining_seen"][x]["username"])
                
        return likes_users
    
    def __graph__(self,like_times,date,xlabel,style = "-b",unique = False):#, xticks = range(min(like_times),max(like_times))):
        """
        This private method plots the line graph of the data with nice formatting.

        Parameters
        ----------
        like_times : tuple or list
            The data to be plotted.
        date : string
            The period the data covers to add to the title.
        xlabel : string
            Self-explanatory.
        style : string, optional
            How the graph should look(shape of crosses, line graph vs scatter ect). The default is "-b".
        unique : Boolean, optional
            If np.unique been not been done already?. The default is False.

        Returns
        -------
        None.

        """
        if like_times == [] or like_times == ([],[]):
            print("Error: No data to plot a line graph")
            return
        if unique:
            time,like_counts = like_times
        else:
            time,like_counts = np.unique(like_times, return_counts=True)
            
        plt.plot(time,like_counts,style)
        #plt.xticks((time[0],time[5],time[10],time[15],time[20]))
        plt.xticks(range(0,24))
        plt.xlabel(xlabel)
        if self.likes_media and self.likes_comment:
            plt.title("Number of posts & comments liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Posts & Comments Liked")
        elif self.likes_media:
            plt.title("Number of posts liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Posts Liked")
        elif self.likes_comment:
            plt.title("Number of comments liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Comments Liked")
        plt.show()
        #plt.savefig("F:\ExeterMathsSchool\My Data Individual EMC\graphs\likes_media_months_"+year)
        
    def __graph_boxplot__(self,like_times,date,xlabel):
        """
        This private method plots the boxplot of the data with nice formatting.

        Parameters
        ----------
        like_times : list of integers
            The data to be plotted.
        date : string
            When the data is from.
        xlabel : string
            Self-explanatory.

        Returns
        -------
        None.

        """
        if like_times == []:
            print("Error: No data to make a boxplot")
            return
        plt.boxplot(like_times,vert=False)
        plt.xticks(range(0,24))
        #plt.xticks(range(min(like_times),max(like_times)))
        if self.likes_media and self.likes_comment:
            plt.title("Number of posts & comments liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Posts & Comments Liked")
        elif self.likes_media:
            plt.title("Number of posts liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Posts Liked")
        elif self.likes_comment:
            plt.title("Number of comments liked per " +xlabel+ " in "+date)
            plt.ylabel("Number of Comments Liked")
        plt.xlabel(xlabel)
        plt.show()
        
    def __table__(self,like_times,missing_times=0,sort_by_likes=False,max_rows=1000):
        """
        Produces a full table of the selected data including summary statistics.

        Parameters
        ----------
        like_times : list of integers
            The data being analized.
        missing_times : integer, optional
            The number of missing 0's. The default is 0.
        max_rows : integer, optional
            The maximum number of rows that should be displayed. The default is 1000.
            
        Returns
        -------
        None.

        """
        if like_times == []:
            print("Error: No data to make table")
            return
        time, like_counts = np.unique(like_times, return_counts=True)
        if sort_by_likes:
            like_counts, time = zip( *sorted( zip(like_counts, time), reverse=True ) )
            
        print("time like_counts")
        for i in range(min(len(time),100)): #only prints first 100 results
            print(time[i],like_counts[i])
        
        if missing_times == 0:
            print("Please enter the amount of missing times for the table above:")
            print("Enter 0 if all the times/dates appear")
            missing_times = int(input(">>>"))
        for x in range(0,min(missing_times,max_rows)):
            like_counts = np.append(like_counts,[0])
        
        print("Total", sum(like_counts))
        print("Mean", statistics.mean(like_counts))
        print("Median", statistics.median(like_counts))
        print("SD",statistics.pstdev(like_counts)) #population standard deviation
        print("Range",max(like_counts)-min(like_counts))
        print("Note:", missing_times,"missing 0's were added for the purpose of calulations")
        
        if self.print_latex:
            print("\n","#"*20,"Latex","#"*20)
            print("""\\begin{table}[h]\n\centering\n\caption{TBC}\n\label{table:1}\n\\begin{tabular}{ |c|c| } \n \hline TBC & TBC""")
            for i in range(min(len(time),max_rows)):
                print(time[i],"&",like_counts[i],"\\\\",end="")
            print("\hline Total &",sum(like_counts),"\\\\")
            print("\hline Mean &",statistics.mean(like_counts),"\\\\")
            print("Median &", statistics.median(like_counts),"\\\\")
            print("SD & ",statistics.pstdev(like_counts),"\\\\")
            print("Range & ",max(like_counts)-min(like_counts),"\\\\")
            print(""" \hline\n\end{tabular}\n\end{table}""")
            
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
            like_times = self.__data_time__(slice(0,10),year_month_day,slice(11,16),return_ints=False)
        elif len(year_month_day) == 7:#year-month
            like_times = self.__data_time__(slice(0,7),year_month_day,slice(11,16),return_ints=False)
        else:
            like_times = self.__data_time__(slice(10,11),"T",slice(11,16),return_ints=False)
        #self.__graph__(like_times,year_month_day,"Hour:Minute")
        self.__table__(like_times)
        
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
            like_times = self.__data_time__(slice(0,10),year_month_day,slice(11,13))
        elif len(year_month_day) == 7:#year-month
            like_times = self.__data_time__(slice(0,7),year_month_day,slice(11,13))
        elif len(year_month_day) == 4:#year
            like_times = self.__data_time__(slice(0,4),year_month_day,slice(11,13))
        else:#all of time
            like_times = self.__data_time__(slice(10,11),"T",slice(11,13))
            year_month_day = "all time"
            
        self.__graph__(like_times,year_month_day,"Hour")
        self.__table__(like_times,missing_times=(24-len(np.unique(like_times))))
        self.__graph_boxplot__(like_times,year_month_day,"Hour")
    
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
            like_times = self.__data_time__(slice(0,4),year_month,slice(5,13),return_ints=False)#,return_counts=True)
            for month_day in like_times:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:5]))
                days_of_week.append([day_datetime.isoweekday(),month_day[-2:]])
        else:
            like_times = self.__data_time__(slice(0,7),year_month,slice(8,13),return_ints=False)        
            for day in like_times:
                day_datetime = datetime.date(int(year_month[:4]),int(year_month[5:7]),int(day[:2]))
                days_of_week.append([day_datetime.isoweekday(),day[-2:]])
                
        hours = [[],[],[],[],[],[],[]]
        for day_of_week in range(1,8):
            for day_of_week_hour in days_of_week:
                if day_of_week_hour[0] == day_of_week:
                    hours[day_of_week-1].append(day_of_week_hour[1])
            hours[day_of_week-1] = list(map(int,hours[day_of_week-1]))
            if graph_per_day:
                self.__graph__(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)))
                self.__graph_boxplot__(hours[day_of_week-1],year_month,("hour for each Day of Week: "+str(day_of_week)))
                print("Day of week",day_of_week)
                self.__table__(hours[day_of_week-1],missing_times=(24-len(np.unique(hours[day_of_week-1]))))
        
        workday_hours = hours[0]+hours[1]+hours[2]+hours[3]+hours[4]
        self.__graph__(workday_hours,year_month,"hour during the week(Monday-Friday)")
        self.__graph_boxplot__(workday_hours,year_month,"hour during the week(Monday-Friday)")
        print("Weekdays(Monday-Friday)")
        self.__table__(workday_hours,missing_times=(24-len(np.unique(workday_hours))))
        
        weekend_hours = hours[5] + hours[6]
        self.__graph__(weekend_hours,year_month,"hour during the weekend")
        self.__graph_boxplot__(weekend_hours,year_month,"hour during the weekend")
        print("Weekend")
        self.__table__(weekend_hours,missing_times=(24-len(np.unique(weekend_hours))))
        
    
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
            like_times = self.__data_time__(slice(0,4),year_month,slice(5,10),return_ints=False)
            for month_day in like_times:
                day_datetime = datetime.date(int(year_month[:4]),int(month_day[:2]),int(month_day[3:]))
                day_of_week.append(day_datetime.isoweekday())
        else:
            like_times = self.__data_time__(slice(0,7),year_month,slice(8,10),return_ints=False)        
            for day in like_times:
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
        like_times = self.__data_time__(slice(0,7),year_month,slice(8,10))
        self.__graph__(like_times,year_month,"Day")
        self.__graph_boxplot__(like_times,year_month,"Day")
        self.__table__(like_times)
        
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
        like_times = self.__data_time__(slice(10,11),"T",slice(0,10),return_ints=False)
        self.__table__(like_times,max_rows=number_of_days,sort_by_likes=True)
        
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
        like_times = []
        if start_date[0:5] == finish_date[0:5]:
            for month in range(int(start_date[5:7]),int(finish_date[5:7])+1):
                month = str(month)
                month = "0"*(2-len(month)) + month
                if start_date[5:7] == finish_date[5:7]: #if same month
                    for day in range(int(start_date[8:10]),int(finish_date[8:10])+1):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        like_times += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == start_date[5:7]: #if on starting month
                    for day in range(int(start_date[8:10]),32):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        like_times += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                elif month == finish_date[5:7]: #if on finishing month
                    for day in range(1,int(finish_date[8:10])+1):
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        like_times += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
                else:
                    for day in range(0,32): #include all days in month
                        day = str(day)
                        day = "0"*(2-len(day)) + day
                        match_date = start_date[0:5] + month + "-" +day
                        like_times += self.__data_time__(slice(0,10),match_date,slice(5,10),return_ints=False)
        else:
            for day in range(int(start_date[8:10]),32): #include all days in starting month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = start_date[0:8] + day
                like_times += self.__data_time__(slice(0,10),match_date,slice(0,10),return_ints=False)
            for day in range(1,int(finish_date[8:10])+1): #include all days in finishing month
                day = str(day)
                day = "0"*(2-len(day)) + day
                match_date = finish_date[0:8] + day
                like_times += self.__data_time__(slice(0,10),match_date,slice(0,10),return_ints=False)
            
        self.__graph__(like_times,start_date+" to "+finish_date,"Day")
        #self.__graph_boxplot__(like_times,start_date+" to "+finish_date,"Day")
        print("Between",start_date,"and",finish_date,"inclusive:")
        self.__table__(like_times)
        
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
            like_times = self.__data_time__(slice(0,4),year,slice(5,7))
        else:
            like_times = self.__data_time__(slice(10,11),"T",slice(0,7),return_ints=False)
            year = "all time"
        self.__graph__(like_times,year,"Month")
        #self.__graph_boxplot__(like_times,year,"Month")
        self.__table__(like_times)
        
    def best_friends(self):
        """
        Conducts best friends Analysis.

        Returns
        -------
        None.

        """
        like_friends = self.__data_user__()
        self.__table__(like_friends,sort_by_likes=True)
        #add graphs?
        
    def auto_analysis_time(self):
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
        

analysis_object = Analysis()
#analysis_object.months("")
#analysis_object.days_range("2018-12-27","2019-01-06") #AMC 2018
#analysis_object.days_range("2019-12-27","2020-01-05") #AMC 2019
#analysis_object.best_friends()
#analysis_object.weekdays_hours("2020-03")
analysis_object.auto_analysis_time()
#analysis_object.timezone_test()
#analysis_object.hours("2020-01")
#analysis_object.top_days()
#analysis_object.profile_summary()

#for x in range(1,5):
#    for y in range(1,32):
#        analysis_object.hours("2020-"+(2-len(str(x)))*"0"+str(x)+"-"+(2-len(str(y)))*"0"+str(y))
