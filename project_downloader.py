#!/usr/bin/env python3

import datetime
import operator
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request


broken = [
	"libdispatch-187.7", # tarfile appears to be duplicate of 187.5
]


def system(command, check=True, env=None):
	process = subprocess.run(command, shell=True, capture_output=True, env=env)
	if check and process.returncode:
		sys.stderr.write(str(process))
		sys.exit(1)


def get_versions(project):
	try:
		html = urllib.request.urlopen("https://opensource.apple.com/tarballs/" + project).read().decode()
	except urllib.error.HTTPError:
		sys.stderr.write("Can't find project " + project + "!")
		sys.exit(2)
	versions = list(set(re.findall(re.compile(project + "-([0-9.]+)\\.tar\\.gz"), html)))
	versions.sort(key=lambda version: tuple(map(int, version.split("."))))
	return versions


def download_project(project, min_version=None):
	print("Downloading project " + project + "...")
	versions = get_versions(project)
	print("Found versions: " + ", ".join(versions))
	if min_version:
		try:
			index = versions.index(min_version)
		except ValueError:
			sys.stderr.write("Could not find version " + min_version + "!")
			sys.exit(3)
		versions = versions[index + 1:]
		print("Skipping past version " + min_version + "...")
	temporary_directory = tempfile.mkdtemp()
	print("Creating temporary directory at " + temporary_directory + "...")
	if not os.path.exists(project):
		print("Making directory " + project + "...")
		os.makedirs(project)
	os.chdir(project)
	if not os.path.exists(".git"):
		print("Initializing git repository...")
		system("git init")
	for version in versions:
		release = project + "-" + version
		if release in broken:
			print(release + " has been marked as broken. Skipping...")
			continue
		print("Adding " + release + "...")
		file_name = release + ".tar.gz"
		compressed_file = os.path.join(temporary_directory, file_name)
		url = "https://opensource.apple.com/tarballs/" + project + "/" + file_name
		urllib.request.urlretrieve(url, compressed_file)
		tar = tarfile.open(compressed_file)
		date = datetime.datetime.fromtimestamp(max(map(operator.attrgetter("mtime"), tar.getmembers()))).isoformat()
		tar.extractall(path=temporary_directory)
		system("git rm -rf .", False)
		system("git clean -fxd", False)
		project_directory = os.path.join(temporary_directory, release)
		for file in os.listdir(project_directory):
			shutil.move(os.path.join(project_directory, file), file)
		system("git add -A")
		env = os.environ.copy()
		env["GIT_AUTHOR_DATE"] = date
		system("git commit --allow-empty -am '" + release + "' -m 'Imported from " + url + "'", env=env)
		# Let's be nice
		time.sleep(1)
	print("Removing temporary directory")
	shutil.rmtree(temporary_directory)


if __name__ == "__main__":
	if 2 <= len(sys.argv) <= 3:
		download_project(*sys.argv[1:])
	else:
		print("Usage: ./apple-open-source-downloader.py project [version]")
