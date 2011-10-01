#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 - dasjoe   mail+git@dasjoe.de
#
# Licensed under GPL Version 3 or later

import os
import urllib
import re
import argparse
import sys
import subprocess
import math
from xml.dom.minidom import parse

class l2gURLopener(urllib.FancyURLopener):
	version = "Mozilla 5.0"

def findInPath(prog):
	for path in os.environ["PATH"].split(os.pathsep):
		exe_file = os.path.join(path, prog)
		if os.path.exists(exe_file) and os.access(exe_file, os.X_OK):
			return exe_file
	return False

def main():
	parser = argparse.ArgumentParser(description='Download lectures from lecture2go')
	parser.add_argument('url', help='URL to the lecture\'s video feed')
	parser.add_argument('-l', '--list-cmd', action='store_true', help='Prints list of commands to fetch videos without actually downloading')
	parser.add_argument('-n', '--number', action='store_true', help='Name downloaded files in chronological order')
	args = parser.parse_args()

	if args.url[-8:] != ".mp4.xml":
		sys.exit("ERROR: URL is not a video feed")

	list_cmd = False
	if args.list_cmd:
		list_cmd = True

	number_files = False
	if args.number:
		number_files = True

	loader = l2gURLopener();
	#feed = loader.open(args.url).read()
	feed = loader.open(args.url)

	dom = parse(feed)

	videos = []

	for item in dom.getElementsByTagName("item"):
		videoName = item.getElementsByTagName("title").item(0).firstChild.nodeValue
		videoPage = item.getElementsByTagName("link").item(0).firstChild.nodeValue
		videos.append((videoName, videoPage))

	videos.sort()

	downloads = []
	for (videoName, videoPage) in videos:
		pageText = loader.open(videoPage).read()
		playerParams = re.search(r'showPlayer\(("rtmp",.*)\)',pageText).group(1)
		playerParams = playerParams.replace('","', '|').replace('"', '').split('|')
		videoURL = 'rtmp://fms.rrz.uni-hamburg.de:1935/vod/mp4:/' + playerParams[3] + '/' + playerParams[4]
		downloads.append((videoURL, videoName))

	number = 0
	padding = int(math.log10(len(videos)))+1

	for (videoURL, videoName) in downloads:
		number = number + 1
		num = ""
		if (number_files):
			num = "%0*d-"%(padding, number)
		fileName = num + videoName + ".flv"
		command = [findInPath("rtmpdump")]
		command.extend(["-r", videoURL, "-e", "-o", fileName])
		if list_cmd:
			print ' '.join(command)
		else:
			print "Getting " + fileName
			subprocess.Popen(command, shell=False).wait()

if __name__ == "__main__":
	main()
