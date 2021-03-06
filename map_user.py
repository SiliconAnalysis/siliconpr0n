#!/usr/bin/env python3

import os
import re
import errno
import subprocess
import datetime
import img2doku
import shutil

# TODO: move to setup_env() in util.py
# but good enough right now
COPYRIGHT_TXT = "/var/www/archive/data/pages/simapper/copyright.txt"
if os.path.exists("/mnt/si"):
    COPYRIGHT_TXT = "/mnt/si" + COPYRIGHT_TXT


def default_copyright(user):
    """
    cat /var/www/archive/data/pages/copyright.txt
    ^ User ^ Copyright ^ Note ^
    | mcmaster | John McMaster, CC-BY |  |
    """
    f = open(COPYRIGHT_TXT, "r")
    f.readline()
    for l in f:
        l = l.strip()
        if not l:
            continue
        _prefix, this_user, copyright, _notes, _postfix = l.split("|")
        this_user = this_user.strip()
        copyright = copyright.strip()
        if user == this_user:
            return copyright
    else:
        raise Exception("Failed to find copyright for " + user)


def run(user, copyright=None, files=[], run_img2doku=True):
    if not copyright:
        copyright = default_copyright(user)
    print("Files")
    for f in files:
        print("  " + f)
    print("")
    print("")
    print("")
    copyright = "&copy; " + str(
        datetime.datetime.today().year) + " " + copyright
    print("Copyright: " + copyright)
    cmd = "pr0nmap -c '%s' %s" % (copyright, " ".join(files))
    print("Running: " + cmd)
    subprocess.check_call(cmd, shell=True)
    print("")
    print("")
    print("")

    if run_img2doku:
        # Only write if the page doesn't already exist
        _out_txt, wiki_page, wiki_url, map_chipid_url, wrote, exists = img2doku.run(
            hi_fns=files, collect=user, write=True, write_lazy=True)
        print("wiki_page: " + wiki_page)
        print("wiki_url: " + wiki_url)
        print("map_chipid_url: " + map_chipid_url)
        print("wrote: " + str(wrote))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate map and template wiki for image')
    parser.add_argument('--user',
                        required=True,
                        help='User name (ie wiki user name)')
    parser.add_argument('--copyright',
                        default=None,
                        help='Copyright release base')
    parser.add_argument('files', nargs="+", help='Images to map')
    args = parser.parse_args()
    run(user=args.user, copyright=args.copyright, files=args.files, run_img2doku=True)


if __name__ == "__main__":
    main()
