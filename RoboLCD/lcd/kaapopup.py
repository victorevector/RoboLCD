from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.effects.scroll import ScrollEffect
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import json
from kaa_command import *


class ULabel(Label):
	pass


def get_update_lists():
	"""
	Get Update Log lists from file when click "updates" button.
	:return:
	"""
	if os.path.isfile(UPDATE_LOG):
		file = open(UPDATE_LOG, 'rb')
		update_binary_lists = a2b_hex(file.read())
		update_lists = str(update_binary_lists).split('\n')
		Logger.info('update_lists: {}'.format(update_lists))
		file.close()
		return update_lists
	else:
		Logger.info('No Update Log File.')
		return ''


class UpdateScreen(BoxLayout):
	"""
	UpdateScreen for Updates Tab.
	"""

	def __init__(self, **kwargs):

		super(UpdateScreen, self).__init__(**kwargs)

		update_lists = get_update_lists()
		if len(update_lists) == 0:
			Logger.info('No Update Log File.')

		else:
			i_text = ''
			b_text = ''
			self.ids.update_grid.add_widget(ULabel(text='[b][size=35]       Improvement:[/size][/b]'))

			infos = update_version_information(update_lists)
			Logger.info('Update informations: {}'.format(infos))

			if len(infos["improve"]) != 0:
				for i_txt in infos["improve"]:
					if str(i_txt) == ' ':
						continue
					i_text = '              -  ' + str(i_txt)
					self.ids.update_grid.add_widget(ULabel(text=i_text))

				self.ids.update_grid.add_widget(ULabel(text='[b][size=35]       Bug_Fix:[/size][/b]'))

			if len(infos["bugs"]) != 0:
				for b_txt in infos["bugs"]:
					if str(b_txt) == ' ':
						continue
					b_text = '              -  ' + str(b_txt)
					self.ids.update_grid.add_widget(ULabel(text=b_text))

	def up_action(self, *args):
		Logger.info('starting up action')
		scroll_distance = 0.4
		Logger.info(self.ids.update_scroll_view.scroll_y)

		# makes sure that user cannot scroll into the negative space
		if self.ids.update_scroll_view.scroll_y + scroll_distance > 1:
			scroll_distance = 1 - self.ids.update_scroll_view.scroll_y
		self.ids.update_scroll_view.scroll_y += scroll_distance

	def down_action(self, *args):
		Logger.info('starting down action')
		scroll_distance = 0.4

		# makes sure that user cannot scroll into the negative space
		Logger.info(self.ids.update_scroll_view.scroll_y)
		if self.ids.update_scroll_view.scroll_y - scroll_distance < 0:
			scroll_distance = self.ids.update_scroll_view.scroll_y
		self.ids.update_scroll_view.scroll_y -= scroll_distance


class RunningPopup(Popup):
	pass


class ErrorPopup(Popup):
	pass


class CompletePopup(Popup):
	pass


class NoupdatePopup(Popup):
	pass


class KaaPopup(Popup):
	msg = NumericProperty()
	update = StringProperty()

	def __init__(self, message=0, update="False", **kwargs):
		super(KaaPopup, self).__init__()

		self.msg = message
		self.update = update

	def handle_commands(self):
		"""
		Handle the shell commands depending on message.
		:return:
		"""
		self.dismiss()

		if self.update == "True":
			new_json_res = {"type": "UPDATE_REQ"}

		else:
			new_json_res = {"type": "NEW_REQ", "id": self.msg, "res": "YES"}

		send_msg(new_json_res)

	def update_later(self):
		self.dismiss()
		new_json_res = {"type": "NEW_REQ", "id": self.msg, "res": "NO"}
		send_msg(new_json_res)