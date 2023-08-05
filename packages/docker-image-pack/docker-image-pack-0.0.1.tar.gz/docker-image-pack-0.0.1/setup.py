from setuptools import setup

setup(
    name="docker-image-pack",
    version="0.0.1",
    description="Manage docker images for offline use",
    long_description="""Manage and verify integrity of docker images when transferring them between machines without network access""",
    url="https://gitlab.com/cunity/docker-image-pack",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=[
        "dockerimagepack",
    ],
    python_requires=">=3.8, <4",
    entry_points={
        "console_scripts": [
            "docker-image-pack=dockerimagepack.tool:run"
        ]
    }
)
