"""Wrapper functions for running docker and parsing output"""
import os.path
from os import close
from typing import Dict, Any, List, Union, Tuple, Optional
import hashlib
import subprocess
import json
import tempfile

class DockerError(Exception):
    def __init__(self, msg: str, inner: Exception):
        super(DockerError, self).__init__()
        self.message = msg
        self.inner = inner


class InvalidImageId(Exception):
    def __init__(self, msg: str):
        self.message = msg


def docker_call(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    cmdline = ["docker"] + args
    try:
        proc = subprocess.run(cmdline,
                              shell=False,
                              capture_output=True,
                              encoding="utf-8",
                              check=True,
                              **kwargs)
        return proc
    except subprocess.CalledProcessError as cpe:
        raise DockerError(f"failed running {cmdline}", cpe)


def docker_json(args: List[str]) -> Union[List, Dict]:
    """Run docker and parse it's stdout as json, raise on error"""
    proc = docker_call(args)
    return json.loads(proc.stdout)


def inspect_image(image: str) -> Dict[str, Any]:
    """Run docker inspect and return the output as a dictionary"""
    data = docker_json(["inspect", str(image)])
    if not len(data) == 1:
        raise ValueError(f"unexpected response frm docker inspect: {data}")
    return data[0]


def validate_image_id(image_id: str) -> str:
    """Check that image_id is a valid digest identifier shaXXX:ABCD"""
    return validate_sha_string(image_id)


def validate_repo_image_digest(image: str) -> str:
    """Check that image is a valid image string with repo digest identifier eg: image@shaXXX:ABCD"""
    if "@" in image:
        repo_image, digest = image.split("@", 1)
        try:
            digest = validate_sha_string(digest)
            if ":" in repo_image:
                # discard the tag if one was given
                repo_image = repo_image.split(":", 1)[0]

            return f"{repo_image}@{digest}"
        except InvalidImageId:
            pass
    raise InvalidImageId(image)


def validate_sha_string(text: str) -> str:
    """Check that text is a valid digest identifier shaXXX:ABCD"""
    if text and ":" in text:
        text = text.lower()
        hashtype, digest = text.split(":", 1)
        try:
            int(digest, 16)
            if hashtype == "sha256":
                if len(digest) == 64:
                    return text
            elif hashtype == "sha512":
                if len(digest) == 128:
                    return text
        except ValueError:
            pass

    raise InvalidImageId(text)


def is_repo_image(image: str) -> bool:
    """Return True if the image string is a repo image and digest"""
    try:
        validate_repo_image_digest(image)
        return True
    except InvalidImageId:
        return False


def is_image_id(image: str) -> bool:
    """Return True if the image string is just an image id (digest)"""
    try:
        validate_image_id(image)
        return True
    except InvalidImageId:
        return False


def get_id_from_image(image: str):
    """Given an image, return it's image ID"""
    pull = False
    if is_repo_image(image):
        image = validate_repo_image_digest(image)
        pull = True
    elif not image_exists_locally(image):
        pull = True
    if pull:
        docker_call(["image", "pull", image])
    data = inspect_image(image)
    return data.get("Id", None)


def image_exists_locally(image: str) -> bool:
    try:
        inspect_image(image)
        return True
    except DockerError:
        return False


def get_tags_from_image(image: str):
    """Get the tags on this image"""
    image = validate_image_id(image)
    data = inspect_image(image)
    return data.get("RepoTags", [])


def save_image_from_id(image: str, folder: str, hashtype: Optional[str] = "sha256") -> Tuple[str, str]:
    """Given an image ID, compute the hash of the file, save it in the given folder and return the path and digest"""
    if hashtype != "sha256":
        raise NotImplementedError(hashtype)
    image_id = validate_image_id(image)
    filename = os.path.join(folder, image_id)
    if os.path.exists(filename):
        os.unlink(filename)
    os.makedirs(folder, exist_ok=True)
    # ensure we get a safe file all to ourself that we can use to save and hash
    # the image tar file.
    safe_fd, safe_name = tempfile.mkstemp(dir=folder)
    close(safe_fd)
    hasher = hashlib.sha256()
    try:
        docker_call(["save", image_id, "-o", safe_name])
        with open(safe_name, "rb") as saved:
            while True:
                chunk = saved.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        digest = hasher.hexdigest()
        os.rename(safe_name, filename)
        return filename, digest
    finally:
        if os.path.exists(safe_name):
            os.unlink(safe_name)

