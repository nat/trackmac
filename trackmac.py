#!/usr/bin/python
#
# trackmac.py
#
# A simple time tracker for Mac OS X by Nat Friedman (nat@nat.org).
#
# Run this script in a termina. It displays activity statistics 
# from the last 24 hours, like this:
#
# 2m 55s        Google Chrome
# 2m 51s        TextMate
# 1m 7s         Terminal
# 37s           Colloquy
# 
# Time spent at your computer: 7m 30s
# Total time tracked: 7m 30s
# 
# It detects idle time based on the screensaver, so lower your 
# screensaver delay to improve accuracy.
#
# It doesn't save the data, so if you kill the script it loses the
# history.

import time, math, sys
from AppKit import NSWorkspace
from operator import itemgetter

# Sample every 15 seconds
sample_interval = 1
idle_activities = ["loginwindow", "ScreenSaverEngine"]

def friendly_duration(secs):
	minutes, seconds = divmod(secs, 60)
	hours, minutes = divmod(minutes, 60)
	duration = []
	if hours > 0:   duration.append('%dh' % hours)
	if minutes > 0: duration.append('%dm' % minutes)
	if seconds > 0: duration.append('%ds' % seconds)
	return ' '.join(duration)

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
		print "Please wait, gathering data..."
		return

	activities, total_time = gather_activities(samples)
		
	sorted_activities = sorted(activities.items(), key=itemgetter(1))
	sorted_activities.reverse()

	for a in sorted_activities:
		print friendly_duration(a[1]) + "\t\t" + a[0]
	
	if "idle" in activities:
		idle_time = activities["idle"]
	else:
		idle_time = 0

	keyboard_time = total_time - idle_time
	print
	print "Time spent at your computer: " + friendly_duration(keyboard_time)
	print "Total time tracked: " + friendly_duration(keyboard_time)
	
def run_profiler():
	samples = []
	while True:
		activeAppName = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
		samples.append([int(time.time()), activeAppName])
		print_summary(samples)
		time.sleep(sample_interval)

run_profiler()