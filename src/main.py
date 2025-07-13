import os, struct, datetime 
from chat_content import ChatContent
from message import Message

STRINOVA_FOLDER_NAME = "Strinova"
STRINOVA_CHAT_LOCATION = r"Saved\Chat"
STRINOVA_CLANCHAT_LOCATION = r"Saved\ClanChat"

def initial_location() -> str:
    """
    Returns the path to Strinova if everything is OK.
    """
    if not os.name == "nt":
        raise Exception("asd")        
    
    local = os.getenv("LOCALAPPDATA")
    if local is None or len(local) <= 8: # minimum check, that it's atleast C:\Users...
        raise Exception("Failed to find 'AppData\Local' Location")
    
    strinova_base_path = os.path.join(local, STRINOVA_FOLDER_NAME)
    if not os.path.exists(strinova_base_path):
        raise Exception("Could not find Strinova in Local, do you have the game installed?")
    
    chat_location = os.path.join(strinova_base_path, STRINOVA_CHAT_LOCATION)
    clanchat_location = os.path.join(strinova_base_path, STRINOVA_CLANCHAT_LOCATION)

    arr = []
    if os.path.exists(chat_location): arr.append(chat_location)
    if os.path.exists(clanchat_location): arr.append(clanchat_location)
    
    return arr

    
def grab_chats(location: str) -> list:
    """
    Returns all the avaliable chat .jsons
    """
    
    result = []
    
    if location is None or len(location) <= 8:
        return result
    
    users_folders = os.listdir(location)
    
    for folder in users_folders:
        if folder == '0': # some always null id
            continue
        
        users_chat_location = os.path.join(location, folder)
        users_chat_folder = os.listdir(users_chat_location)

        for newchat in users_chat_folder:
            users_newchat_location = os.path.join(users_chat_location, newchat)
            users_newchat_folder = os.listdir(users_newchat_location)

            chat_list = []
            for json in users_newchat_folder:
                chat_list.append(os.path.join(newchat, json))

            result.append(chat_list)    
    return result

def deserialize(chat_file: str) -> ChatContent:
    """
    The actual extraction of chats from the .chat
    """ 
    output = ''
    file_length = 0
    with open(chat_file, 'rb') as b:
        file_length = os.fstat(b.fileno()).st_size
        if file_length == 0:
            print(f"File sie of: {chat_file} is 0")
            return
        
        output = b.read()
    
    # parent_dir = os.path.basename(os.path.dirname(chat_file)) # example output: 4750169_2040155_NewChat
    # chat_user_id = int(parent_dir[0:7])
    # chat_to_id = int(parent_dir[8:15])
    
    # content = ChatContent()
    
    messages = []
    c = 0
    userid = None
    frienduserid = None

    try:
        while c < file_length:
            userid = struct.unpack('<I', output[c:c+4])[0]
            
            c += 4 * 2 # skipping the already read bits + the next row of empty bits 
            
            frienduserid = struct.unpack('<I', output[c:c+4])[0] # TODO: later could make a class and keep them there, but i dont see a use for now
            
            c += 4 * 2
            
            name_len = struct.unpack('<I', output[c:c+4])[0] # some magic bits, idk what they for
            
            c += 4

            name = output[c:c + name_len - 1].decode("utf-8", errors='ignore')
            c += name_len
            
            icon = struct.unpack('<I', output[c:c+4])[0]
            
            c += 4
            
            icon_border = struct.unpack('<I', output[c:c+4])[0]

            c += 4

            testchatBubbleId = struct.unpack('<I', output[c:c+4])[0]
            c += 4 * 2
            
            timestamp = struct.unpack('<I', output[c:c+4])[0]

            c += 4 * 2

            message_len = struct.unpack('<I', output[c:c+4])[0]
            
            c += 4
            
            message = output[c:c+message_len - 1].decode('utf-8', errors='ignore')
            c += message_len
            c += 4
            
            index = struct.unpack('<I', output[c:c+4])[0]
            
            c += 4
            
            messages.append(Message(sender=name, timestamp=timestamp, message=message))           
    except Exception as e:
        print(f"Error in {chat_file} with {e}, skipping...")
        return None
    
    content = ChatContent(userid, frienduserid, messages)
    
    return content

def save_to_file(contents: list):
    dir = os.getcwd()
    
    if not os.path.exists(os.path.join(dir, "output")):
        os.mkdir(os.path.join(dir, "output"))
    
    inside_folder = os.path.join(dir, "output")
    for content in contents:
        if content is None:
            continue
        
        with open(os.path.join(inside_folder, f"{content.user}_{content.to}.txt"), 'w', encoding='utf-8') as f:
            for message in content.messages:
                if message is None:
                    continue
                
                f.write(f"{datetime.datetime.fromtimestamp(message.timestamp)} {message.sender}: {message.message}\n")
        
    
if __name__ == "__main__":
    chat, clanchat = initial_location()
    chats_list = grab_chats(chat)
    clanchat_list = grab_chats(clanchat)

    contents = []
    for newchats in chats_list:
        for newchat in newchats:
            _, ext = os.path.splitext(newchat)
            if ext != '.chat':
                continue
            
            userid = newchat[0:7]
            content = deserialize(os.path.join(chat, userid, newchat))
            contents.append(content)
        
    save_to_file(contents)
    
    
            
    
