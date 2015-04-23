#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import platform
import subprocess
import re
import time

TRAY_TOOLTIP = "CoChecker"
TIME_TO_WAIT = 30000
REMOTE_ADDRESS = "8.8.4.4"
TIMEOUT = 1000
GREEN_ICON = "icon/green.png"
YELLOW_ICON = "icon/yellow.png"
ORANGE_ICON = "icon/orange.png"
RED_ICON = "icon/red.png"
LIMIT1 = 250
LIMIT2 = 550
LIMIT3 = 880
VERBOUS = True


def create_menu_item(menu, label, func):
	item = wx.MenuItem(menu, -1, label)
	menu.Bind(wx.EVT_MENU, func, id=item.GetId())
	menu.AppendItem(item)
	return item


class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self):
		super(TaskBarIcon, self).__init__()

		self.time_to_wait = TIME_TO_WAIT
		self.remote_address = REMOTE_ADDRESS
		self.timeout = TIMEOUT
		self.limit1 = LIMIT1
		self.limit2 = LIMIT2
		self.limit3 = LIMIT3
		self.green_icon = GREEN_ICON
		self.yellow_icon = YELLOW_ICON
		self.orange_icon = ORANGE_ICON
		self.red_icon = RED_ICON
		self.toogle = True

		self.set_icon(self.green_icon, TRAY_TOOLTIP)
		self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_click)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_end_timmer, self.timer)
		self.timer.Start(self.time_to_wait)

	def CreatePopupMenu(self):
		self.menu = wx.Menu()
		if self.toogle:
			self.menu.AppendItem(wx.MenuItem(self.menu, -1, "Pause"))
		else:
			self.menu.AppendItem(wx.MenuItem(self.menu, -1, "Start"))
		self.menu.AppendItem(wx.MenuItem(self.menu, -1, "Config"))
		self.menu.AppendSeparator()
		self.menu.AppendItem(wx.MenuItem(self.menu, -1, "Exit"))
		self.menu.Bind(wx.EVT_MENU, self.on_click_toogle, id=self.menu.FindItemByPosition(0).GetId())
		self.menu.Bind(wx.EVT_MENU, self.on_click_config, id=self.menu.FindItemByPosition(1).GetId())
		self.menu.Bind(wx.EVT_MENU, self.on_exit, id=self.menu.FindItemByPosition(3).GetId())
		return self.menu

	def set_icon(self, path, label):
		img = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
		img.SetMask(wx.Mask(img, "#D6D6D6"))
		icon = wx.IconFromBitmap(img)
		self.SetIcon(icon, label)

	def on_end_timmer(self, event):
		somme = 0.0
		for i in range(0,5):
			tmp = ping(self.remote_address, self.timeout)
			somme += tmp
		somme /= 5
		if VERBOUS:
			print somme
		if somme < self.limit1:
			self.set_icon(self.green_icon, str(somme)+" ms")
		elif somme < self.limit2:
			self.set_icon(self.yellow_icon, str(somme)+" ms")
		elif somme < self.limit3:
			self.set_icon(self.orange_icon, str(somme)+" ms")
		else:
			self.set_icon(self.red_icon, str(somme)+" ms")

	def on_left_click(self, event):
		if self.timer.IsRunning():
			self.timer.Stop()
			self.timer.Start(self.time_to_wait)
		self.on_end_timmer(None)

	def on_click_toogle(self, event):
		if self.timer.IsRunning():
			self.timer.Stop()
			self.toogle = False
			self.CreatePopupMenu()
		else:
			self.on_end_timmer(None)
			self.timer.Start(self.time_to_wait)
			self.toogle = True
			self.CreatePopupMenu()

	def on_click_config(self, event):
		print "config"

	def on_exit(self, event):
		wx.CallAfter(self.Destroy)


def ping(hostname,timeout):
	if platform.system() == "Windows":
		command = ["ping",hostname,"-n", "1", "-w", str(timeout)]
	else:
		command = ["ping", "-w", str(timeout), "-c", "1", hostname]
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	matches = re.findall(r"time=([0-9\.]+) *ms", process.stdout.read())
	if len(matches) > 0:
		return float(matches[0])
	else:
		return timeout


def main():
	app = wx.PySimpleApp()
	TaskBarIcon()
	app.MainLoop()


if __name__ == "__main__":
	main()
