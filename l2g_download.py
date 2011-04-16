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
	args = parser.parse_args()

	if args.url[-8:] != ".mp4.xml":
		sys.exit("ERROR: URL is not a video feed")

	loader = l2gURLopener();
	feed = loader.open(args.url).read()

	videos = []
	for match in re.finditer('guid>(.*)</guid', feed):
		videoLink = match.group(1)
		videos.append(videoLink)

	videos.sort()

	downloads = []
	for link in videos:
		page = loader.open(link).read()
		videoFile = re.search(r'(http://lecture2go.uni-hamburg.de/videorep/.*/).+\.jpg',page).group(1) + re.search(r'&file=.+/(.+\.mp4)', page).group(1)
		downloads.append(videoFile)

	for link in downloads:
		filename = re.search(r'.*/(.+mp4)', link).group(1)
		command = [findInPath("axel")]
		command.extend(["-a", "-o", filename, link])
		subprocess.Popen(command, shell=False).wait()

if __name__ == "__main__":
	main()
