#instagram_anonymise.py by Ryan Traviss

import json

OLD_FILEPATH = "Instagram_data\\"
NEW_FILEPATH = "anon_data\\anon_"
print("Enter your username below:")
USERNAME = input(">>>")
    
def _read_json(filename):
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
    with open(OLD_FILEPATH+filename, "r", encoding="utf8") as f:
        return json.loads(f.read())
    
def _write_json(data, filename):
    """
    Writes the dictionary data into filename as JSON.

    Parameters
    ----------
    data : dictionary
        The data to be stored.
    filename : string
        The filename of the file.
        
    """
    with open(NEW_FILEPATH+filename, "w") as f:
        f.write(json.dumps(data))
        
def anonymise_likes():
    """
    Anonymises the likes data by removing usernames.
    """
    likes_data = _read_json("likes.json")
    for i in range(len(likes_data["media_likes"])):
        likes_data["media_likes"][i][1] = "username"
    for i in range(len(likes_data["comment_likes"])):
        likes_data["comment_likes"][i][1] = "username"
            
    _write_json(likes_data, "likes.json")

        
def anonymise_comments():
    """
    Anonymises comments data by removing usernames and text.
    """
    comments_data = _read_json("comments.json")
    for i in range(len(comments_data['media_comments'])):
        comments_data['media_comments'][i][1] = ""
        comments_data['media_comments'][i][2] = "username"
        
    _write_json(comments_data, "comments.json")
    
def annonymise_media():
    """
    Annonymises media data by removing captions and locations.
    """
    media_data = _read_json("media.json")
    for i in range(len(media_data["stories"])):
        media_data["stories"][i]["caption"] = ""
        media_data["stories"][i]["path"] = ""
        
    for i in range(len(media_data["photos"])):
        media_data["photos"][i]["caption"] = ""
        media_data["photos"][i]["path"] = ""
        if "location" in media_data["photos"][i].keys():
            media_data["photos"][i]["location"] = ""
        
    for i in range(len(media_data["profile"])):
        media_data["profile"][i]["caption"] = ""
        media_data["profile"][i]["path"] = ""
    
    for i in range(len(media_data["direct"])):
        media_data["direct"][i]["path"] = ""
    
    _write_json(media_data, "media.json")
    
def annonymise_seen_content():
    """
    Anonymises seen_content data by removing usernames.
    """
    seen_content_data = _read_json("seen_content.json")
    for i in range(len(seen_content_data["videos_watched"])):
        seen_content_data["videos_watched"][i]["author"] = "username"
        
    for i in range(len(seen_content_data["ads_seen"])):
        seen_content_data["ads_seen"][i]["author"] = "username"
        
    for i in range(len(seen_content_data["chaining_seen"])):
        seen_content_data["chaining_seen"][i]["username"] = "username"
        
    for i in range(len(seen_content_data["posts_seen"])):
        seen_content_data["posts_seen"][i]["author"] = "username"
        
    _write_json(seen_content_data, "seen_content.json")

def annonymise_messages():
    """
    Annonymises messages by removing everything but datetime.
    Replaces your username with "you" else "username".
    """
    def _key_check(key, replace=""):
        """
        If key is in the dictionary then make value replace.

        Parameters
        ----------
        key : string
            A key that could be in a message.
        replace : string, optional
            What should the value be replaced by. The default is "".
            
        """
        if key in messages_data[i]["conversation"][k].keys():
            messages_data[i]["conversation"][k][key] = replace
            
    messages_data = _read_json("messages.json")
    for i in range(len(messages_data)):
        for j in range(len(messages_data[i]["participants"])):
            messages_data[i]["participants"][j] = "username"
        for k in range(len(messages_data[i]["conversation"])):
            if messages_data[i]["conversation"][k]["sender"] == USERNAME:
                messages_data[i]["conversation"][k]["sender"] = "you"
            else:
                messages_data[i]["conversation"][k]["sender"] = "username"
            messages_data[i]["conversation"][k]["text"] = ""
            if "likes" in messages_data[i]["conversation"][k].keys():
                for l in range(len(messages_data[i]["conversation"][k]["likes"])):
                    if messages_data[i]["conversation"][k]["likes"][l]["username"] == USERNAME:
                        messages_data[i]["conversation"][k]["likes"][l]["username"] = "you"
                    else:
                        messages_data[i]["conversation"][k]["likes"][l]["username"] = "username"
            
            _key_check("media")
            _key_check("media_owner","username")
            _key_check("media_share_caption")
            _key_check("media_share_url")
            _key_check("animated_media_images")
            _key_check("user",{})
            _key_check("media_url")
            _key_check("link")
            _key_check("profile_share_username","username")
            _key_check("profile_share_name")
            _key_check("story_share")
            _key_check("action")
            _key_check("video_call_action")
            _key_check("mentioned_username","username")
            _key_check("voice_media")
            
    _write_json(messages_data, "messages.json")
    
def annonymise_connections():
    """
    Anonymises connections data by removing usernames.
    """
    def _key_replace(data):
        """
        Replaces the keys (which are usernames) with a number.

        Parameters
        ----------
        data : dictionary
            The dictionary to work on.

        """
        key_list = list(data.keys())
        for i in range(len(key_list)):
            old_key = key_list[i]
            data[str(i)] = data.pop(old_key)
        
    connections_data = _read_json("connections.json")
    
    _key_replace(connections_data["following"])
    _key_replace(connections_data["followers"])
    _key_replace(connections_data["blocked_users"])  
    _key_replace(connections_data["close_friends"])
    _key_replace(connections_data["follow_requests_sent"])
    _key_replace(connections_data["dismissed_suggested_users"]) 
    
    _write_json(connections_data, "connections.json")
    
def annonymise_profile():
    """
    Anonymises the profile by removing everything but date created.
    """
    profile_data = _read_json("profile.json")
    
    profile_data["biography"] = ""
    profile_data["email"] = ""
    profile_data["website"] = ""
    profile_data["gender"] = ""
    profile_data["name"] = ""
    profile_data["profile_pic_url"] = ""
    profile_data["username"] = "you"
    profile_data["date_of_birth"] = ""
    
    _write_json(profile_data, "profile.json")

anonymise_likes()
anonymise_comments()
annonymise_media()
annonymise_seen_content()
annonymise_messages()
annonymise_connections()
annonymise_profile()
print("Finished anonymising data")
