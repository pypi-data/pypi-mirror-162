from __future__ import annotations

import telebot # https://github.com/eternnoir/pyTelegramBotAPI

class TelegramBot():
    def __init__(self, token:str):
        self.token = token 
        self.tb = telebot.TeleBot(self.token)
    
    def GetMe(self) -> telebot.types.User:
        return self.tb.get_me()
    
    def SetChatID(self, chatid:int) -> TelegramBot:
        self.chatid = chatid
        return self
    
    def SendFile(self, path:str):
        self.tb.send_document(self.chatid, open(path, 'rb')) 

    def SendImage(self, path:str):
        self.tb.send_photo(self.chatid, open(path, 'rb'))

    def SendVideo(self, path:str):
        self.tb.send_video(self.chatid, open(path, 'rb')) 

    def SendAudio(self, path:str):
        self.tb.send_audio(self.chatid, open(path, 'rb')) 

    def SendLocation(self, latitude:float, longitude:float):
        self.tb.send_location(self.chatid, latitude, longitude)

    def SendMsg(self, msg:str):
        if len(msg) <= 4096:
            self.tb.send_message(self.chatid, msg) 
        else:
            for m in telebot.util.smart_split(msg, 4096):
                self.tb.send_message(self.chatid, m) 

if __name__ == "__main__":
    token, chatid = open("TelegramBot.ident").read().strip().split("\n")
    t = TelegramBot(token).SetChatID(int(chatid))
    t.SendMsg("test")