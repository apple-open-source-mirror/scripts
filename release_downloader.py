#!/usr/bin/env python3

import re
import sys
import time
import urllib.request


def get_releases():
	try:
		html = urllib.request.urlopen("https://opensource.apple.com/").read().decode()
	except urllib.error.HTTPError:
		sys.stderr.write("Cannot find not find Apple Open Source page!")
		sys.exit(1)
	return list(dict.fromkeys(re.findall(re.compile("/release/(.*)\\.html"), html)).keys())


def get_projects(release):
	try:
		html = urllib.request.urlopen("https://opensource.apple.com/release/" + release + ".html").read().decode()
	except urllib.error.HTTPError:
		sys.stderr.write("Cannot find not find release page for " + release + "!")
		sys.exit(2)
	return list(dict.fromkeys(re.findall(re.compile("/source/.*/(.*)/"), html)).keys())


def download_releases(release_file):
	with open(release_file, 'w') as file:
		for release in get_releases():
			print("Finding projects for release " + release + "...")
			file.write(release + ":" + ",".join(get_projects(release)) + "\n")
			# Let's be nice
			time.sleep(1)


if __name__ == "__main__":
	if len(sys.argv) == 2:
		download_releases(sys.argv[1])
	else:
		print("Usage: ./apple-open-source-downloader.py releasefile")
