# Scripts

A collection of Python scripts to scrape the [Apple Open Source website](https://opensource.apple.com) and convert them into Git repositories. If there's a project you'd like uploaded but is missing from this organization, let me know and I'll run these scripts to generate one for it.

## Usage

If you'd like to run this locally, first pick the project you want to download. The project name is the "project" part of a https://opensource.apple.com/tarballs/project/ URL. Then run the project downloader script:

```console
$ ./project_downloader project
```

If you already have a somewhat up-to-date project folder, run it with an argument specifying the latest version you have and the downloader will skip past that version number:

```console
$ ./project_downloader project version
```

The project downloader will create a Git repository in a folder named after the project name, and commits will be have an author date of the newest file in the project tarball for that version.

Then, to tag the project commits with their appropriate release, first download a list of all the releases (or grab the possibly out-of-date one from [here](https://github.com/apple-open-source-mirror/releases)):

```console
$ ./release_downloader.py releases.txt
```

Then, run the tagger script:

```console
$ ./apple-open-source-downloader.py project releases.txt
```

Note that the project folder must match the project name for this script to work correctly.
