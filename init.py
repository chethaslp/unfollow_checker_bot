
# UCB_Insta
# Developed BY CLP (Chethas L Pramod)
# IG : @chethas_lp
# Ver: 1.0

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import threading

from time import sleep
import datetime
from pytz import timezone

import InstaHandler
import dataHandler

bot = telebot.TeleBot(dataHandler.credentials["bot_api"])
chat_id = 0
del_msgs =[]
data = None
userData = None
timeout_thread = None
usr_id_admin = 0


####################################################################################
############################ TIMEOUT HANDLER #######################################
####################################################################################

def timeout_callback(message,msgs):
	clearMsg(msgs)
	markup = types.ReplyKeyboardRemove()
	bot.send_message(message.chat.id, dataHandler.texts["request_cancelled"] ,reply_markup=markup)
	bot.send_message(message.chat.id, dataHandler.texts["send_command"])

def timeout(msg=None,msg_id=None):
    global timeout_thread
    if msg != None:
        timeout_thread = threading.Timer(dataHandler.time['timeout_duration'], timeout_callback, args=(msg,msg_id,))
        timeout_thread.start()
        timeout_thread.join()
    else:
    	if timeout_thread is not None:
    		timeout_thread.cancel()

####################################################################################
############################### ADMIN HANDLERS #####################################
####################################################################################


@bot.message_handler(commands=['admin'])
def adminUser(message):
	if dataHandler.get_admin() == 0:
		print("IMP : Admin Login Initiated by "+str(message.chat.id))
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "Authentication Required.",reply_markup=markup)
		bot.register_next_step_handler(message, auth_callback)
		timeout(message,[msg1])
	else:
		bot.send_message(message.chat.id, "Admin already configured.")
		print("IMP : Admin Login Rejected : "+str(message.chat.id))

def auth_callback(message):
	timeout()
	if message.text == dataHandler.credentials['bot_api']:
		print("IMP : Admin Login Success : "+str(message.chat.id))
		bot.send_message(message.chat.id, "Auth Success.")
		dataHandler.set_admin(message.chat.id)
	else:
		bot.send_message(message.chat.id, "Auth Cancelled.")
		print("IMP : Admin Login Rejected : "+str(message.chat.id))

@bot.message_handler(commands=['broadcast'])
def send_broadcast(message):
	if message.chat.id == dataHandler.get_admin():
		print("IMP : Broadcast Initiated by "+str(message.chat.id))
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "Enter Message.",reply_markup=markup)
		bot.register_next_step_handler(message, broadcast_msg_callback)
		timeout(message,[msg1])
	else:
		bot.send_message(message.chat.id, "Broadcasting requires Admin Privilages.")
		print("IMP : Broadcast Request Cancelled : "+str(message.chat.id))
def broadcast_msg_callback(message):
	timeout()
	refreshData()
	print("IMP : Broadcast Sending... : "+str(message.chat.id) + " : " + message.text)
	c = 1
	for cid in data["users_ids"]:
		bot.send_message(cid, "BROADCAST:\n"+message.text)
		c+=1
	print("IMP : Broadcast Sent to "+str(c)+"users. : "+str(message.chat.id))

@bot.message_handler(commands=['sendDM'])
def send_dm(message):
	if message.chat.id == dataHandler.get_admin():
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "Enter ChatID.",reply_markup=markup)
		bot.register_next_step_handler(message, send_dm_callback)
		timeout(message,[msg1])
	else:
		bot.send_message(message.chat.id, "Senting DM messages requires Admin Privilages.")
		print("IMP : DM Request Cancelled : "+str(message.chat.id))
def send_dm_callback(message):
	timeout()
	global usr_id_admin
	usr_id_admin = int(message.text)
	if usr_id_admin not in data["users_ids"]:
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "ERR404: User not Found.",reply_markup=markup)
	else:
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "Enter Message.",reply_markup=markup)
		bot.register_next_step_handler(message, send_dm_msg_callback)
		timeout(message,[msg1])
def send_dm_msg_callback(message):
	timeout()
	global usr_id_admin
	bot.send_message(usr_id_admin, "DM:\n"+message.text)
	usr_id_admin = 0
	markup = types.ReplyKeyboardRemove()
	bot.send_message(message.chat.id, "Message Sent.",reply_markup=markup)
	print("IMP : DM Sent : "+str(message.chat.id) + " : " + message.text)

@bot.message_handler(commands=['removeUser'])
def remove_usr_admin(message):
	if message.chat.id == dataHandler.get_admin():
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "Enter ChatID.",reply_markup=markup)
		bot.register_next_step_handler(message, send_dm_callback)
		timeout(message,[msg1])
	else:
		bot.send_message(message.chat.id, "Remove User requires Admin Privilages.")
		print("IMP : DM Request Cancelled : "+str(message.chat.id))
def remove_usr_admin_callback(message):
	timeout()
	global usr_id_admin
	usr_id_admin = int(message.text)
	if usr_id_admin not in data["users_ids"]:
		markup = types.ForceReply(selective=False)
		msg1 = bot.send_message(message.chat.id, "ERR404: User not Found.",reply_markup=markup)
	else:
		markup = InlineKeyboardMarkup()
		markup.row_width = 2
		markup.add(InlineKeyboardButton("Yes", callback_data="rm_admin_yes"), InlineKeyboardButton("No", callback_data="rm_admin_no"))
		confirm_msg3 = bot.send_message(chat_id, 'Confirm ?', reply_markup=markup)
		global del_msgs
		del_msgs=[confirm_msg3]
		timeout(message,del_msgs)

####################################################################################
############################## USER HANDLERS #######################################
####################################################################################

def clearMsg(msgs):
	for msg in msgs:
		bot.delete_message(msg.chat.id,msg.message_id)

def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            if m.text.lower() == "hii" or m.text.lower() == "hi" or m.text.lower() == "hello" or m.text == '✋':
             	bot.reply_to(m, "Hello " +m.chat.first_name + ", Welcome!")
            try:
            	print(m.chat.first_name + " [" + str(m.chat.id) + "]: "+ str(m.text.encode("utf-8")))
            except Exception as e:
            	print(e)

def refreshData():
	global data
	data = dataHandler.get_data()

def sendReport(report,index):
	# Send Follower datas to users.
	if index == 204:
		msg = "Hello "+report["tg_name"]+",\n"
		msg += "Here is the report for your account @"+report['ig_name']+" !\n\n"
		msg += "Followers : "+str(report['follower_count']) +"\n"
		msg += "Following : "+str(report['following_count']) +"\n"
		msg += "Total Unfollowers in this month : "+str(report['unfollowers_count_month']) +"\n\n"
		msg += "Report for time : "+ report['last_time'] +" to "+ datetime.datetime.now(timezone('Asia/Kolkata')).strftime("%b %d, %Y - %H:%M:%S") +"\n"
		msg += "We've found some unfollwers :"
		bot.send_message(report["chat_id"], msg)
		for unfolwr in report['unfollowers']:
			unfolwr_data = InstaHandler.get_userInfo_fromId(unfolwr)
			caption_txt = unfolwr_data["full_name"] +"\n" + unfolwr_data['username']
			bot.send_photo(report["chat_id"], unfolwr_data['profile_pic_url'],caption_txt)
	elif index == 200:
		msg = "Hello "+report["tg_name"]+",\n"
		msg += "Here is the First report for your account @"+report['ig_name']+" !\n\n"
		msg += "Followers : "+str(report['follower_count']) +"\n"
		msg += "Following : "+str(report['following_count']) +"\n"
		msg += "Total Unfollowers in this month : "+str(report['unfollowers_count_month']) +"\n"
		msg += "Now onwards, you will get notified once someone unfollows you."
		bot.send_message(report["chat_id"], msg)
		bot.send_message(report["chat_id"],"🙂")
	elif index == 202:
		msg = "Hello "+report["tg_name"]+",\n"
		msg += "Here is the report for your account @"+report['ig_name']+" !\n\n"
		msg += "Followers : "+str(report['follower_count']) +"\n"
		msg += "Following : "+str(report['following_count']) +"\n"
		msg += "Total Unfollowers in this month : "+str(report['unfollowers_count_month']) +"\n\n"
		msg += "Report for time : "+ report['last_time'] +" to "+ datetime.datetime.now(timezone('Asia/Kolkata')).strftime("%b %d, %Y - %H:%M:%S") +"\n"
		msg += "Congrats, you have no unfollowers today !"
		bot.send_message(report["chat_id"], msg)
		bot.send_message(report["chat_id"],"😃")
	print("INFO : Report initiated for user : "+str(report["chat_id"]))

@bot.message_handler(commands=['start'])
def send_welcome(message):
	refreshData()
	global chat_id
	chat_id = message.chat.id
	bot.send_message(chat_id, dataHandler.texts["welcome0"])
	bot.send_message(chat_id, dataHandler.texts["welcome"])
	# bot.send_message(chat_id, " What can I do? \n Well, I can sent who unfollowed you from your Instagram Account ! \n 😄 😄\n Sounds Great, isn't it? \n So lets get started.")
	if data['UserCount'] is None or data['UserCount'] == 0:
		about_txt = dataHandler.texts["info"] % "No"
	else:
		about_txt = dataHandler.texts["info"] % str(data['UserCount'])
	bot.send_message(chat_id, about_txt)
	bot.send_message(chat_id, dataHandler.texts["config_me"])

@bot.message_handler(commands=['help'])
def command_help(message):
	bot.send_message(message.chat.id, dataHandler.texts['help'] % message.chat.first_name)

# @bot.message_handler(func=lambda message: message.text.lower() == "hii" or message.text.lower() == "hi" or message.text.lower() == "hello" or message.text == '✋' )

# Informal chat Handlers
# Malayalam is my native language 🙂.
@bot.message_handler(regexp="do you know malayalam")
def command_text_malayalam(m):
    bot.reply_to(m, dataHandler.texts["malayalam"])
@bot.message_handler(regexp="hi")
def command_text_hi(m):
    bot.reply_to(m, "Hello " +m.chat.first_name + ", Welcome!")

@bot.message_handler(commands=['config'])
def configUser(message):
	refreshData()
	global chat_id
	chat_id = message.chat.id
	if data is not None and chat_id in data["users_ids"]:
		bot.send_message(chat_id, dataHandler.texts["already_configured"])
	else:
		bot.send_message(chat_id, dataHandler.texts["config_start"])
		# bot.send_message(chat_id, "NOTE : Please make sure you are entering an account that you have in possession. If not then this can lead to further problems.")
		markup = types.ForceReply(selective=False)
		bot.send_message(chat_id, dataHandler.texts["enter_ig_us"], reply_markup=markup)
		bot.register_next_step_handler(message, ig_name_callback)
def ig_name_callback(message):
	# try:
	chat_id = message.chat.id
	ig_name = message.text
	global userData
	bot.send_chat_action(chat_id, 'typing')
	userData = InstaHandler.validateUserInfo(ig_name)
	userData['chat_id'] = chat_id
	userData["tg_name"] = message.chat.first_name
	if userData["status"] == "ok":
		if userData['private'] :
			# TODO:
			# Implemention for Private Accounts
			bot.send_message(chat_id, "Looks like you have a private account !\nWe are extremely sorry, we do not support private accounts.\n We are working on it. Come back soon.")
		else:
			confirm_msg = bot.send_photo(chat_id, userData["pp_url"],userData["name"])
			reply_markup = types.ReplyKeyboardRemove()
			confirm_msg2 = bot.send_message(chat_id, dataHandler.texts["config_ask_confirm"],reply_markup=reply_markup)
			markup = InlineKeyboardMarkup()
			markup.row_width = 2
			markup.add(InlineKeyboardButton("Yes", callback_data="cg_yes"), InlineKeyboardButton("No", callback_data="cg_no"))
			confirm_msg3 = bot.send_message(chat_id, 'Confirm this?', reply_markup=markup)
			global del_msgs
			del_msgs=[confirm_msg,confirm_msg2,confirm_msg3]
			timeout(message,del_msgs)
	elif userData["status"] == "er404":
		bot.reply_to(message, dataHandler.texts["config_404"])
		reply_markup = types.ReplyKeyboardRemove()
		bot.send_message(chat_id, dataHandler.texts["start_again"],reply_markup=reply_markup)


@bot.message_handler(commands=['remove'])
def removeUser(message):
	refreshData()
	markup = InlineKeyboardMarkup()
	markup.row_width = 2
	markup.add(InlineKeyboardButton("Yes", callback_data="rm_yes"), InlineKeyboardButton("No", callback_data="rm_no"))
	confirm_msg = bot.send_message(message.chat.id, dataHandler.texts["confim_remove"], reply_markup=markup)
	timeout(message,[confirm_msg.message_id])

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    timeout()
    if call.data == "rm_yes":
    	dataHandler.remove_user(chat_id)
    	bot.delete_message(chat_id,call.message.message_id)
    	bot.send_message(chat_id, dataHandler.texts["removed"])
    	bot.send_message(chat_id, "😔")
    	bot.send_message(chat_id, dataHandler.texts["run_config"])
    	bot.answer_callback_query(call.id, dataHandler.texts["removed"])
    elif call.data == "rm_no":
    	bot.delete_message(chat_id,call.message.message_id)
    	bot.answer_callback_query(call.id, dataHandler.texts["remove_cancelled"])
    	bot.send_message(chat_id, dataHandler.texts["remove_cancelled"])

    elif call.data == "cg_yes":
    	clearMsg(del_msgs)
    	bot.answer_callback_query(call.id, dataHandler.texts["config_confirmed"])
    	bot.send_message(chat_id, dataHandler.texts["config_confirmed"])
    	dataHandler.create_user(userData)
    	report_data = dataHandler.update_usr_followers(chat_id)
    	sendReport(report_data,report_data['status'])
    	bot.send_message(chat_id, dataHandler.texts['help'] % call.message.chat.first_name)
    	refreshData()
    elif call.data == "cg_no":
    	clearMsg(del_msgs)
    	bot.answer_callback_query(call.id, dataHandler.texts["config_cancelled"])
    	bot.send_message(chat_id, dataHandler.texts["config_cancelled"])

    elif call.data == "rm_admin_yes":
    	clearMsg(del_msgs)
    	dataHandler.remove_user(usr_id_admin)
    	bot.send_message(usr_id_admin, "You have been kicked from using the bot for violating our 'Terms and Conditions'.\nYou will no longer recieve updates.")
    	bot.answer_callback_query(call.id, "Removed user : "+ str(usr_id_admin))
    	bot.send_message(chat_id,"Removed user : "+ str(usr_id_admin))
    elif call.data == "rm_admin_no":
    	clearMsg(del_msgs)
    	bot.answer_callback_query(call.id, "Remove user cancelled.")
    	bot.send_message(chat_id, "Remove user cancelled.")

####################################################################################
############################## MAIN FUNCTIONS #######################################
####################################################################################

# logger = telebot.logger
# logging.basicConfig(filename=dataHandler.files['log'], filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
# telebot.logger.setLevel(logging.ERROR)

print("INFO : Bot INIT")
dataHandler.initialize()
refreshData()
def check_for_unfollowers():
	if data["users_ids"]:
		while True:
			print("INFO : Follower update INIT")
			for uid in data["users_ids"]:
				report_data = dataHandler.update_usr_followers(uid)
				sendReport(report_data,report_data['status'])
			print("INFO : Follower update EXIT")
			sleep(dataHandler.time['checker_sleep_duration'])

checker_thread = threading.Thread(target=check_for_unfollowers)
checker_thread.start()
bot.set_update_listener(listener)
bot.infinity_polling(30)