from setuptools import find_packages, setup
from io import open


def read(filename):
   """Прочитаем наш README.md для того, чтобы установить большое описание."""
   with open(filename, "r", encoding="utf-8") as file:
      return file.read()


setup(name="minifunc",
   version="2.0", 
   description="MiniFunc",
   long_description=read("README.txt"), 
   packages=['mini',],
)