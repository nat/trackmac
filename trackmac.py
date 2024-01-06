#!/usr/bin/python
#
# trackmac.py
#
# A simple time tracker for Mac OS X by Nat Friedman (nat@nat.org).
#
# Written May 6, 2010 in Munich, while a soft rain fell.
#
# Run this script in a terminal. It displays activity statistics 
# from the last 24 hours, like this:
#
# 1h 8m57s  70%  Google Chrome
#   14m17s  14%  Mail
#    8m11s   8%  iChat
#    3m16s   3%  Colloquy
#    1m28s   1%  1Password
#      43s   0%  Terminal
#      12s   0%  TextMate
#       4s   0%  Finder
#       4s   0%  SecurityAgent
#
# 1h37m12s Sitting at the computer
# 3h37m16s Doing something else
# 5h14m28s Total
# 
# It detects idle time based on the screensaver, so lower your 
# screensaver delay to improve accuracy.
#
# It doesn't save the data, so if you kill the script it loses the
# history. You might want to kill it every day or so, so it doesn't
# get too big (it keeps all the old samples around).

import time, math, sys
from AppKit import NSWorkspace
from operator import itemgetter

# Sample every second
sample_interval = 1
idle_activities = ["loginwindow", "ScreenSaverEngine"]

def friendly_duration(secs):
	minutes, seconds = divmod(secs, 60)
	hours, minutes = divmod(minutes, 60)
	duration = []
	if hours > 0:   
		duration.append('%2dh' % hours)
	else:
		duration.append('   ')

	if minutes > 0: 
		duration.append('%2dm' % minutes)
	else:
		duration.append('   ')
		
	if seconds > 0: 
		duration.append('%2ds' % seconds)
	else:
		duration.append('   ')
		
	return ''.join(duration)

def gather_activities(samples):
	# Skip past all samples older than 24 hours
	now = time.time()
	for i in range(len(samples) - 1, 0, -1):
		if (now - samples[i][0]) < 24 * 60 * 60:
			first_i = i

	total_time = samples[len(samples) - 1][0] - samples[first_i][0]

	# Count up all the activities
	activities = {}
	for i in range(first_i + 1, len(samples)):
		activity = samples[i - 1][1]
		duration = samples[i][0] - samples[i - 1][0]

		# If the screen was locked or the computer was suspended
		# (or the script was not running), count that as idle time.
		if activity in idle_activities or duration > (sample_interval + 3):
			activity = "idle"
		
		if activity in activities:
			activities[activity] += duration
		else:
			activities[activity] = duration

	return activities, total_time

def print_summary(samples):
	sys.stdout.write("\033[2J\033[H")
	if len(samples) < 3:
		print ("Please wait, gathering data...")
		return

	activities, total_time = gather_activities(samples)
		
	sorted_activities = sorted(activities.items(), key=itemgetter(1))
	sorted_activities.reverse()

	if "idle" in activities:
		idle_time = activities["idle"]
	else:
		idle_time = 0
	keyboard_time = total_time - idle_time

	for a in sorted_activities:
		if a[0] != "idle":
			print (friendly_duration(a[1]) + " " + ('%3d' % (a[1] * 100 / keyboard_time)) + "%  " + a[0])
	
	print
	print (friendly_duration(keyboard_time) + " Sitting at the computer")
	if (idle_time > 0):
		print (friendly_duration(idle_time) + " Doing something else")
		print (friendly_duration(total_time) + " Total")
	
def run_profiler():
	samples = []
	while True:
		activeAppName = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
		samples.append([int(time.time()), activeAppName])
		print_summary(samples)
		time.sleep(sample_interval)

run_profiler()
