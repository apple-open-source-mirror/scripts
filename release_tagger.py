#!/usr/bin/env python3

import collections
import os
import pathlib
import re
import subprocess
import sys


def system(command, check=True):
	process = subprocess.run(command, shell=True, capture_output=True)
	if check and process.returncode:
		sys.stderr.write(str(process))
		sys.exit(1)


def match_releases(project, release_file):
	print("Reading release file...")
	releases = map(lambda release: release.split(":"), re.sub(r"#\n", "", pathlib.Path(release_file).read_text()).split())
	print("Matching project through each release...")
	mapping = collections.defaultdict(list)
	for (release, projects) in releases:
		for p in projects.split(","):
			if p.startswith(project + "-"):
				print(release + " shipped with " + p)
				mapping[p].append(release)
				break
	return mapping


def tag_releases(mapping):
	print("Tagging releases...")
	tags = subprocess.run("git tag", shell=True, capture_output=True).stdout.decode().split()
	commits = dict(map(lambda commit: commit.split(":")[::-1], subprocess.run("git log --pretty='format:%H:%s'", shell=True, capture_output=True).stdout.decode().split()))
	for (version, releases) in mapping.items():
		for release in releases:
			if release in tags:
				print(release + " is already tagged, skipping...")
			else:
				print("Tagging " + release + "...")
				system("git tag " + release + " " + commits[version])


if __name__ == "__main__":
	if len(sys.argv) == 3:
		releases = match_releases(*sys.argv[1:3])
		os.chdir(sys.argv[1])
		tag_releases(releases)
	else:
		print("Usage: ./apple-open-source-downloader.py project releasefile")
