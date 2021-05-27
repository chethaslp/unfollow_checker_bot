import os
from time import sleep
import datetime
from pytz import timezone
import json

import dataHandler
import instabot
from igramscraper.instagram import Instagram

bot1 = None
bot2 = None

# PLEASE NOTE THAT THIS BOT DOES NOT WORK PROPERLY.
# The advantage - The accounts handled by 'instabot' lib do not get detected by Instagram and not get banned.
# But the major problem is that 'instabot' works abnormally while collecting follower datas and is not accurate.
# Considering that collecting followers data is a important step of this bot, I need to exclude some functions 'instabot' lib in this bot.
# Instead I used 'igramscraper' which is accurate in collecting follower datas but the accounts are getting banned really quick(<3hrs).
# I didn't find any other working libs, So I left hope in this project.
# Thank you.(@CLP)


def initiate():
	# Uses two different instagram bot libs.
	global bot1
	global bot2
	bot1 = instabot.Bot(save_logfile=False)
	bot1.login(username=dataHandler.credentials["ac1"]["username"], password=dataHandler.credentials["ac1"]["password"], is_threaded=True)
	bot2 = Instagram()
	bot2.with_credentials(dataHandler.credentials["ac1"]["username"], dataHandler.credentials["ac1"]["password"])
	bot2.login(force=False,two_step_verificator=True)
	print("INFO : Instabot INIT")
	sleep(2)

def get_userInfo(us):
	if bot1 is None:
		initiate()
	uid = bot1.get_user_id_from_username(us)
	return bot1.get_user_info(uid)
def get_userInfo_fromId(uid):
	if bot1 is None:
		initiate()
	return bot1.get_user_info(uid)

def get_usr_followers(uid):
	if bot1 is None:
		initiate()
	current_folwr = []
	folwrs = bot2.get_followers(uid, 15000, 100, delayed=True)
	for folwr in folwrs['accounts']:
		current_folwr.append(folwr.identifier)
	return current_folwr

def validateUserInfo(us):
	# Stores only essential datas.
	if bot1 is None:
		initiate()
	respData = {}
	respData["parentAccount"] = dataHandler.credentials["ac1"]["username"]

	try:
		resp = get_userInfo(us)
		respData["status"] = 'ok'
		respData["usid"] = resp['pk']
		respData["ig_name"] = resp['username']
		respData["name"] = resp['full_name']
		respData["private"] = resp['is_private']
		respData["is_verified"] = resp["is_verified"]
		respData["pp_url"] = resp['profile_pic_url']
		# resp['hd_profile_pic_url_info']['url']
		respData["media_count"] = resp["media_count"]
		respData["follower_count"] = resp["follower_count"]
		respData["following_count"] = resp["following_count"]
		respData["unfollowers_count"] = 0
		respData["unfollowers_count_month"] = 0
	except TypeError:
		del respData
		respData = {}
		respData["parentAccount"] = dataHandler.credentials["ac1"]["username"]
		respData["status"] = 'er404'

	return respData