from setuptools import setup
import setuptools

"""with open("README.md","r")as f:
    long_descriptoin = f.read()
"""
setup(
    name="Py_Thanglish",
    version="0.0.4",
    description="Tamil to Thanglish converter in python",
    author="Dayanidi Vadivel",
    keywords=[
        "Thanglish",
        "Tamil to Thanglish in python",
        "Thanglish pip",
    "Py_Thanglish",
    "Py-Thanglish",
    "Py_Thanglish pip",
    "Py-Thanglish pip",
        "pip Py_Thanglish",
        "pip Py-Thanglish",
"py_thanglish",
    "py-thanglish",
"pythanglish",
    "pythanglish"
    ],
    long_description=open("README.md", "r", encoding="utf8").read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    py_modules=["Py_Thanglish"],
    packages=setuptools.find_packages("src"),
    package_dir={"":"src"},
    requires=[
        "pandas"
    ],
    url="",
    license="MIT",
    author_email="dayanidivadivel@gmail.com",

)