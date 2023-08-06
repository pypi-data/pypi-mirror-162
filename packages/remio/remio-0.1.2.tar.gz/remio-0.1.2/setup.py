from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    long_description = long_description.replace(
        "./docs/assets/images", "https://hikki12.github.io/remio/assets/images"
    )
    # patch for unicodes
    long_description = long_description.replace("➶", ">>")
    long_description = long_description.replace("©", "(c)")


setup(
    name="remio",
    packages=["remio"],
    version="0.1.2",
    description="A library for managing concurrent socketio, cv2, and pyserial processes. Useful for making robots or devices with Arduinos and Raspberry Pi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    author="Jason Francisco Macas Mora",
    author_email="franciscomacas3@gmail.com",
    url="https://github.com/Hikki12/remio",
    install_requires=requirements,
    keywords=[
        "OpenCV",
        "Serial",
        "SocketIO",
        "multithreading",
        "multiprocessing",
        "IoT",
        "mjpeg",
        "Arduino",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    scripts=[],
    project_urls={
        "Bug Reports": "https://github.com/Hikki12/remio/issues",
        "Source": "https://github.com/Hikki12/remio",
        "Documentation": "https://hikki12.github.io/remio",
    },
)
