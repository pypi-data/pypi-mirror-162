import telegram
import os


class BotShynaTelegram:
    token = os.environ.get('bot_token')
    bot = telegram.Bot(token=token)
    news_bot = telegram.Bot(token=os.environ.get('news_bot_token'))
    broadcast_bot = telegram.Bot(token=os.environ.get('broadcast_bot_token'))
    status = False
    master_telegram_chat_id = os.environ.get('master_telegram_chat_id')
    message = "Default"
    shyna_chat = os.environ.get('shyna_chat')

    def bot_send_msg_to_master(self):
        self.status = self.bot.send_message(chat_id=self.master_telegram_chat_id, text=str(self.message))
        return self.status

    def bot_send_news_to_master(self):
        self.status = self.news_bot.send_message(chat_id=self.master_telegram_chat_id, text=str(self.message))
        return self.status

    def bot_send_broadcast_msg_to_master(self):
        self.status = self.broadcast_bot.send_message(chat_id=self.master_telegram_chat_id, text=str(self.message))
        return self.status

    def bot_send_msg_to_shyna(self, message):
        self.status = self.bot.send_message(chat_id=self.shyna_chat, text=str(self.message))
        return self.status

    def bot_send_msg_to_chat_id(self, chat_id):
        self.status = self.bot.send_message(chat_id=chat_id, text=str(self.message))
        return self.status


if __name__ == '__main__':
    BotShynaTelegram().bot_send_msg_to_master()

