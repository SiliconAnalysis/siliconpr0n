import os
import argparse
from time import sleep
from glob import glob

import PIL
from PIL import Image
from watchdog.observers import Observer

# Have to disable DecompressionBombError limits because these images are large
PIL.Image.MAX_IMAGE_PIXELS = None

GALLERY_IMAGES = 20

ALLOWED_ENDINGS = ["png", "jpg", "jpeg"]

PATH = "map/"
THUMBFILELIST = "gallery.txt"

SMALL_MAX_WIDTH = SMALL_MAX_HEIGHT = 300
MEDIUM_MAX_WIDTH = MEDIUM_MAX_HEIGHT = 1024

GENERATE_MEDIUM = False

# Use the first directory that is not called single if no tilemap path can be mapped from the thumbnail name
USEFIRSTDIRNOTSINGLE = False

def thumb(path):

	if ".thumb" in path:
		return

	if path.rsplit(".", 1)[-1].lower() not in ALLOWED_ENDINGS:
		return

	if path.split(os.path.sep)[-2] != "single":
		return

	print("Resizing", path)

	withoutext, ext = path.rsplit(".", 1)

	img = Image.open(path)
	img.thumbnail((SMALL_MAX_WIDTH, SMALL_MAX_HEIGHT), Image.ANTIALIAS)
	img.save(withoutext + ".thumb." + ext)

	if GENERATE_MEDIUM:
		img = Image.open(path)
		img.thumbnail((MEDIUM_MAX_WIDTH, MEDIUM_MAX_HEIGHT), Image.ANTIALIAS)
		img.save(withoutext + ".thumb2." + ext)

def thumbfilelist():
	print("Generating "+THUMBFILELIST)

	thumbpaths = glob("map/**/single/*.thumb.*", recursive=True)

	result = []

	for path in sorted(thumbpaths, key=lambda path:os.path.getmtime(path), reverse=True)[:GALLERY_IMAGES]:
		parentdir = os.path.dirname(os.path.dirname(path))

		tilemappath = "map/" + os.path.sep.join(os.path.basename(path).split(".", 1)[0].split("_", 2))

		if not os.path.isdir(tilemappath):
			tilemappath = None

			if USEFIRSTDIRNOTSINGLE:

				parentdir_contents = os.listdir(parentdir)
				for siblingdir in parentdir_contents:
					if siblingdir != "single":
						tilemappath = os.path.join(parentdir, siblingdir)
						break

			if tilemappath is None:
				raise Exception("Tilemap doesn't exist! " + path)

		bigpath = path.replace(".thumb", "")

		line = parentdir + "\t" + path + "\t"
		if tilemappath:
			line += tilemappath
		elif GENERATE_MEDIUM:
			line += path.replace(".thumb.", ".thumb2.")#bigpath
		else:
			line += path

		result.append(line)

	with open(THUMBFILELIST, "w+") as f:
		f.write("\n".join(result))

class event_handler:
	@staticmethod
	def dispatch(event):
		if event.event_type == "created" and not event.is_directory:
			try:
				thumb(event.src_path)
				thumbfilelist()
			except PIL.UnidentifiedImageError as e:
				print(e)


def mode_observe():
	observer = Observer()
	observer.schedule(event_handler, PATH, recursive=True)
	observer.start()

	try:
		while True:
			sleep(1)
	finally:
		observer.stop()
		observer.join()

def mode_manual():
	paths = []
	for ending in ALLOWED_ENDINGS:
		paths += glob("map/**/*."+ending, recursive=True)

	for path in paths:
		thumb(path)

	thumbfilelist()

if __name__ == "__main__":
	parser = argparse.ArgumentParser("generate image thumbnails and info")
	parser.add_argument("--watch", dest="mode", action="store_const", const=mode_observe, default=mode_manual, help="watch")
	args = parser.parse_args()

	args.mode()
