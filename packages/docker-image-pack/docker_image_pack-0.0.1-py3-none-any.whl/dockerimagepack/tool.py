"""Create/Use packed and checked docker images"""

import argparse
import os
import tempfile
from typing import Optional, Iterable
from .packfile import pack_images, gather_images, list_images, unpack_image
from .utils import note, die


def list_cmd(opts: argparse.Namespace):
    images = list_images(opts.FILE)
    for image in images:
        tags = image.tags
        if image.repo_digest:
            tags.insert(0, image.repo_digest)
        note(f"{image.image_id}  {image.tags}")


def load_cmd(opts: argparse.Namespace):
    images = list_images(opts.FILE)
    extracted = None
    image_def = opts.IMAGE
    for image in images:
        if image_def == image.image_id or image_def == image.repo_digest or image_def in image.tags:
            # match the image, extract it
            extracted = unpack_image(opts.FILE, image)
        else:
            continue
    if extracted:
        print(f"Loaded {image_def} as image {extracted.image_id}")
    else:
        die(f"Could not find an image matching {image_def} in {opts.FILE}")

def save_cmd(opts: argparse.Namespace):
    newfile = os.path.abspath(opts.FILE)
    if os.path.exists(newfile):
        raise FileExistsError(newfile)
    newfolder = os.path.dirname(newfile)
    os.makedirs(newfolder, exist_ok=True)
    note(f"Create new docker pack file {newfile} ..")
    with tempfile.TemporaryDirectory(dir=newfolder) as td:
        note(f"Collecting docker images: {opts.IMAGE} ..")
        collected = gather_images(td, opts.IMAGE)
        note(f"Building pack file {newfile} ..")
        pack_images(newfile, collected)


parser = argparse.ArgumentParser(description=__doc__, prog="docker-image-pack")
parser.set_defaults(func=None)
subs = parser.add_subparsers()

lister = subs.add_parser("list")
lister.add_argument("FILE", type=str, help="Image archive to read")
lister.set_defaults(func=list_cmd)

load = subs.add_parser("load")
load.add_argument("FILE", type=str, help="Image archive to read")
load.add_argument("IMAGE", type=str, help="Image to load from FILE")
load.set_defaults(func=load_cmd)

save = subs.add_parser("save")
save.add_argument("FILE", type=str, help="Image archive to create")
save.add_argument("IMAGE", type=str, nargs="+", help="Image(s) to save")
save.set_defaults(func=save_cmd)


def run(args: Optional[Iterable[str]] = None):
    opts = parser.parse_args(args=args)
    if not opts.func:
        parser.print_usage()
    else:
        opts.func(opts)


