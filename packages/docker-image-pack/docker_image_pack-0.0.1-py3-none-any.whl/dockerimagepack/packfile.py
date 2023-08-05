"""Manage a docker-image-pack file"""
import json
import os
import shutil
import subprocess
import zipfile
from typing import Optional, List
from . import dockertool
from .utils import note, warn, die

IMAGE_IDS_FILE = "image-ids.json"
REPO_DIGESTS_FILE = "repo-digests.json"
IMAGE_DIGESTS_FILE = "image-digests.json"


class Image:
    """State and info for a docker image we've checked and saved"""
    def __init__(self):
        self.tags: Optional[List[str]] = None
        self.filename: Optional[str] = None
        self.file_digest: Optional[str] = None
        self.image_id: Optional[str] = None
        self.repo_digest: Optional[str] = None


def list_images(packfile: str) -> List[Image]:
    """List the images in the pack file"""
    images = {}
    with zipfile.ZipFile(packfile, "r") as zf:
        with zf.open(IMAGE_IDS_FILE, mode="r") as fd:
            image_ids = json.load(fd)
        with zf.open(IMAGE_DIGESTS_FILE, mode="r") as fd:
            image_digests = json.load(fd)
        with zf.open(REPO_DIGESTS_FILE, mode="r") as fd:
            repo_digests = json.load(fd)
    for image_id in image_ids:
        image = Image()
        image.image_id = image_id
        image.filename = f"images/{image_id}"
        image.file_digest = image_digests[image_id]
        image.tags = image_ids[image_id]
        for repo_image in repo_digests:
            if repo_digests[repo_image] == image_id:
                image.repo_digest = repo_image

        images[image_id] = image

    return list(images.values())


def unpack_image(packfile: str, image: Image) -> Image:
    """Extract and load an image"""
    with zipfile.ZipFile(packfile, "r") as zf:
        filename = f"images/{image.image_id}"
        with zf.open(filename, "r") as data:
            proc = subprocess.Popen(["docker", "load"], stdin=subprocess.PIPE)
            while True:
                chunk = data.read(1024 * 1024)
                if not chunk:
                    break
                proc.stdin.write(chunk)
            proc.stdin.close()
            proc.wait()
            if not proc.returncode == 0:
                die("failed docker load")
            # if the image had a repodigest, make tag for that
            if image.repo_digest:
                repo_tag = image.repo_digest.split("@", 1)[0]
                dockertool.docker_call(["tag", image.image_id, repo_tag])

            # apply any tags the image had
            for tag in image.tags:
                dockertool.docker_call(["tag", image.image_id, tag])

    return image

def pack_images(packfile: str, images: List[Image]):
    """Save one or more images into a packfile"""
    image_ids = {}
    image_digests = {}
    repo_digests = {}
    for image in images:
        if image.image_id not in image_ids:
            image_ids[image.image_id] = []
        image_ids[image.image_id].extend(image.tags)
        image_digests[image.image_id] = image.file_digest
        if image.repo_digest:
            repo_digests[image.repo_digest] = image.image_id

    with zipfile.ZipFile(packfile, "w") as pack:
        # save the image_ids and repo_digests json
        with pack.open(IMAGE_IDS_FILE, mode="w") as fd:
            fd.write(json.dumps(image_ids, indent=1).encode("utf-8"))
        with pack.open(IMAGE_DIGESTS_FILE, mode="w") as fd:
            fd.write(json.dumps(image_digests, indent=1).encode("utf-8"))
        with pack.open(REPO_DIGESTS_FILE, mode="w") as fd:
            fd.write(json.dumps(repo_digests, indent=1).encode("utf-8"))
        for image in images:
            with pack.open(f"images/{image.image_id}", mode="w", force_zip64=True) as fd:
                with open(image.filename, "rb") as img_fd:
                    shutil.copyfileobj(img_fd, fd)

def gather_images(folder: str, image_list: List[str]) -> List[Image]:
    """For each image in image_list, save it on disk in the given directory and return the list of image details"""
    os.makedirs(folder, exist_ok=True)
    images: List[Image] = []
    for image in image_list:
        note(f"saving image {image} ..")
        repo_image = None
        src_image_id = None
        if dockertool.is_repo_image(image):
            repo_image = dockertool.validate_repo_image_digest(image)
            src_image_id = dockertool.get_id_from_image(repo_image)
        elif dockertool.is_image_id(image):
            src_image_id = dockertool.validate_image_id()
        else:
            warn(f"requested image {image} is not a full repo digest or image id")
            src_image_id = dockertool.get_id_from_image(image)
        tags = dockertool.get_tags_from_image(src_image_id)
        note(f"tags           :")
        for tag in tags:
            note(f" {tag}")
        note(f"registry digest: {repo_image}")
        note(f"image id       : {src_image_id}")
        filename, image_file_digest = dockertool.save_image_from_id(src_image_id, folder)
        note(f"saved digest   : {image_file_digest}")
        img = Image()
        img.tags = tags
        img.image_id = src_image_id
        img.repo_digest = repo_image
        img.file_digest = image_file_digest
        img.filename = filename
        images.append(img)

    return images

