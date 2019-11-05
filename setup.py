import setuptools

setuptools.setup(
    name="pype",
    version="0.1",
    author="Colin Champney",
    author_email="colinchampney@gmail.com",
    description="A small Python tool to quickly apply code snippets to the lines of a text file.",
    packages=["pype"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
    	'console_scripts': [
    		"pype = pype.__main__:main"
    	]
    },
    python_requires='>=3.6',
)