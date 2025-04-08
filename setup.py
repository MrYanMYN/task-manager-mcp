from setuptools import setup, find_packages

setup(
    name="terminal-task-tracker",
    version="0.1.0",
    description="A terminal-based task tracking application with a three-pane layout",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tasktracker=main:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities"
    ],
)