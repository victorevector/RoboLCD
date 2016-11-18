import shlex
import subprocess
import time
import os
import sysv_ipc
import json
import threading
from binascii import b2a_hex, a2b_hex
import Queue as queue
from kivy.logger import Logger


UPDATE_LOG = "/home/pi/.octoprint/logs/.update_log.log"

# queue key
SEND_QUEUE_KEY = 6102
ACK_START = "#R#"
ACK_END = "#E#"

mqs = None

try:
	mqs = sysv_ipc.MessageQueue(SEND_QUEUE_KEY, sysv_ipc.IPC_CREAT)
	Logger.info('Found mqs')
except Exception as e:
	Logger.info('Not found mqs: {}'.format(e))


def send_msg(msg):
	"""
	Send msessage to server.
	:param msg:
	:return:
	"""
	global mqs

	try:
		# inform RoboLCD there is updates for module.
		json_data = json.dumps(msg)
		Logger.info('json data sent: {}'.format(json_data))
		mqs.send(ACK_START+json_data+ACK_END)
		time.sleep(1)

	except Exception as exp:
		Logger.info('send to kivy is MQ error: {}'.format(exp))
		mqs = None


def update_version_information(update_lists):
	"""
	Make Update information text
	:param msg:
	:return: text
	"""
	# Split with Improvement and bug fix.
	improvements = []
	bug_fix = []

	for index, update_list in enumerate(update_lists):
		update_lines = update_list.split(';')

		infos = ''

		# Get update information from command.
		for index, update_line in enumerate(update_lines):
			if update_line == '*':
				infos = update_lines[index + 1]
				break
			else:
				pass

		improve_bug_infos = str(infos).split(':')

		for index, info in enumerate(improve_bug_infos):
			if index == 0:
				i_str = info.split(',')
				improvements += i_str
				Logger.info('improvements i_str: {}'.format(improvements))
			elif index == 1:
				b_str = info.split(',')
				bug_fix += b_str
				Logger.info('bug_fix b_str: {}'.format(bug_fix))

	return {'improve': improvements, 'bugs': bug_fix}
