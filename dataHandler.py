# Author: @CLP (ig: @chethas_lp)
# Created on 30-10-2020
# dataHandlers.py

##############################
# TODO : CHANGE THE VARIABLES.
##############################

import os
from os import path
import json

import time
import datetime
from pytz import timezone

import InstaHandler


credentials = {
	# WARN: DO NOT USE YOUR PERSONEL ACCOUNTS.
	# Primary Instagram Account
	"ac1":{
		"username":"",
		"password":""
	},
	# Secondary Instagram Account
	"ac2":{
		"username":"",
		"password":""
	},
	# Telegram Bot api to be replaced here. (Can be obtained from @BotFather on TG)
	"bot_api":""
}

time = {
	"timeout_duration":30.0,
	# Crawl sleep time for the bot.
	# Checks followers between this iterval. 'Change at your own risk.'
	# Default: 6hrs(60*60*6)
	"checker_sleep_duration": 60*60*6
}

files = {
	"stats":"data/stats.json",
	"users":"data/users.json",
	"usr":"users/%s.usr",
	"log":"data/UCB.log",
	"folws":"followers/%s.usr"
}

# Text Variables.
texts ={
	"welcome0":"Howdy, how are you doing?",
	"welcome":" Welcome to Unfollow Checker Bot for Instagram 🙏 ! \n\n Use /help for more info about me.",
	"info":"Bot developed by CLP. \n So far %s Users are using me.",
	"config_me":"Configure me with the /config command.",
	"malayalam":"Illa.",

	"config_start":"Lets config your account. \n\nNOTE : Please make sure you are entering an account that you have in possession. If not then this can lead to further problems.",
	"enter_ig_us":"Enter your instagram username.",
	"config_ask_confirm":"\nIs this your Account? 🧐",
	"config_404":"Account not found. Config Cancelled. 😔",
	"config_confirmed":"Confirmed. 👍",
	"already_configured":"Account already Configured.",
	"config_cancelled":"Confirm Cancelled.",
	"invalid_input":"Invalid Input. Config Cancelled. 😔",
	"start_again":"Start again.",

	"confim_remove":"Confirm Remove?",
	"removed":"Removed. ",
	"run_config":"Run /config if you want to configure again.",
	"remove_cancelled": "Remove Request Cancelled.",

	"request_cancelled":"Request cancelled due to inactivity.",
	"send_command":"Send command again.",

	"help":"Hello %s,\nThank you for using the bot.\n\nUCB (Unfollow Checker Bot)\n[ver:1.0]\nThis bot is developed by CLP( @im_clp ).\nDM for any queries.\nHope you enjoy using this bot.\n\nIf you wish to remove your account, use /remove."
}

folders = ['users','data','followers']



def set_admin(uid):
	data = get_data()
	data['admin'] = uid
	set_data(data)
def get_admin():
	data = get_data()
	return data['admin']

def set_data(data):
	with open(files['stats'], "w") as stats_f:
		json.dump(data, stats_f)
def get_data():
	try:
		with open(files['stats'], "r") as stats_file:
			return json.load(stats_file)
	except Exception as e:
		print(e)
		initialize()
		with open(files['stats'], "r") as stats_file:
			return json.load(stats_file)

def create_user(resp):
	try:
		with open(files['users'] , "r") as users_f:
			users = json.load(users_f)
		with open(files['stats'] , "r") as stats_f:
			stats = json.load(stats_f)
	except Exception as e:
		print(e)
		initialize()
		with open(files['users'] , "r") as users_f:
			users = json.load(users_f)
		with open(files['stats'] , "r") as stats_f:
			stats = json.load(stats_f)
	stats["UserCount"] += 1
	stats["users_ids"].append(resp['chat_id'])
	set_data(stats)
	with open(files['usr'] % str(resp['chat_id']), "w") as usr_f:
		json.dump(resp, usr_f)
	with open(files['users'], "w") as users_f:
		json.dump(users, users_f)
	print("New User Created : "+ str(resp['chat_id']))
def remove_user(uid):
	# with open(files['users'] , "r") as users_f:
	# 	users = json.load(users_f)
	with open(files['stats'] , "r") as stats_f:
		stats = json.load(stats_f)
	stats["UserCount"] -= 1
	stats["users_ids"].remove(uid)
	with open(files['stats'], "w") as write_file2:
		json.dump(stats, write_file2)
	os.remove(files['usr'] % str(uid))
	os.remove(files['folws'] % str(uid))
	print("Removed User: " + str(uid))
def get_usr_data(uid):
	with open(files['usr'] % str(uid), "r") as usr_file:
		return json.load(usr_file)


def update_usr_followers(uid):
	folwr_data = get_usr_followers(uid)
	usr_data = update_usr_stats(uid)
	cur_followers = InstaHandler.get_usr_followers(usr_data['usid'])
	if folwr_data is None:
		usr_data['status']= 200
	else:
		usr_data['last_time'] = folwr_data['last_time']
		res = list(set(folwr_data['followers']) - set(cur_followers))
		if not res:
			print("No Unfollowers found for " + str(uid))
			usr_data['status']= 202
		else:
			usr_data['unfollowers_count'] += len(res)
			usr_data['unfollowers_count_month'] += len(res)
			usr_data['unfollowers'] = res
			usr_data['status']= 204
			print("Unfollowers found for "+str(uid)+" : "+ str(res))
	folwr_saved_data ={}
	folwr_saved_data["last_time"] = datetime.datetime.now(timezone('Asia/Kolkata')).strftime("%b %d, %Y - %H:%M:%S")
	folwr_saved_data["followers"] = cur_followers
	with open(files['folws'] % str(uid), "w") as wf:
		json.dump(folwr_saved_data, wf)
	new_data = InstaHandler.get_userInfo_fromId(usr_data['usid'])
	usr_data['following_count'] = new_data['following_count']
	usr_data['follower_count'] = new_data['follower_count']
	return usr_data

def update_usr_stats(uid):
	usr_data = get_usr_data(uid)
	new_data = InstaHandler.get_userInfo_fromId(usr_data['usid'])
	usr_data['ig_name'] = new_data['username']
	usr_data['following_count'] = new_data['following_count']
	usr_data['follower_count'] = new_data['follower_count']
	with open(files['usr'] % uid, "w") as usr_f:
		json.dump(usr_data, usr_f)
	return usr_data

def get_usr_followers(uid):
	if path.exists(files['folws'] % str(uid)):
		with open(files['folws'] % str(uid) , "r") as folws_f:
			folws_data = json.load(folws_f)
		return folws_data
	else:
		return None

def initialize():
	for folder in folders:
		if not path.exists(folder):
			os.mkdir(folder)
	for dtfile in files:
		if not path.exists(files[dtfile]):
			if dtfile == "stats":
				sample_dt = {
					"version":"0.1 Beta",
					"UserCount":0,
					"admin":0,
					"me":[],
					"users_ids": []
				}
			elif dtfile == "users":
				sample_dt = {}
			with open(files[dtfile], "w") as dt_file:
				json.dump(sample_dt, dt_file)
