#analysis_word.py by Ryan Traviss

import util

print("What is your username?")
USERNAME = input(">>>")

class AnalysisWord:
    def __init__(self,path="",comments_filename = "comments.json", 
                 messages_filename = "messages.json", comments=True, messages=True):
        self.comments = comments
        self.messages = messages
        
        self.comments_json_data = util.read_json(path+comments_filename)
        self.messages_json_data = util.read_json(path+messages_filename)
        
    def _data(self):
        word_data = []
        if self.comments:
            for x in range(len(self.comments_json_data["media_comments"])):
                word_data.extend(self.comments_json_data["media_comments"][x][1].split())
            
        if self.messages:
            for x in range(len(self.messages_json_data)):
                for y in range(len(self.messages_json_data[x]["conversation"])):
                    if self.messages_json_data[x]["conversation"][y]["sender"] == USERNAME:
                        if "text" in self.messages_json_data[x]["conversation"][y].keys():
                            if self.messages_json_data[x]["conversation"][y]["text"] is not None:
                                word_data.extend(self.messages_json_data[x]["conversation"][y]["text"].split())
                            
        return word_data
    
    def top_words(self):
        words = analysis_object._data()
        
        with open("words_to_remove.txt","r") as f: #currently top 100 words in English language
            words_to_remove = f.read().split()
            
        for word in words_to_remove:
            words = list(filter((word).__ne__, words))
                
        util.table(words,sort_by_likes=True,max_rows=100,sort="asc")
        
analysis_object = AnalysisWord(messages=True)
analysis_object.top_words()
