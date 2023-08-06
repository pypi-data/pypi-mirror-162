#!/usr/bin/env python3

# Standard libraries
from os.path import expanduser
from pathlib import Path, PurePosixPath

# Components
from ..system.platform import Platform
from .environment import Environment

# Paths class
class Paths:

    # Basename
    @staticmethod
    def basename(data):

        # POSIX path
        path = PurePosixPath(data)

        # Result
        return str(path.name)

    # Expand
    @staticmethod
    def expand(path, env=True, home=True):

        # Expand environment
        if env:
            path = Environment.expand(path)

        # Expand home
        if home:
            path = expanduser(path)

        # Result
        return path

    # Getter
    @staticmethod
    def get(data):

        # POSIX path
        path = PurePosixPath(data)

        # Result
        return str(path)

    # Resolver
    @staticmethod
    def resolve(data):

        # Resolve path
        path = Path(data).resolve()

        # Linux, macOS or Windows path
        if Platform.IS_LINUX or Platform.IS_MAC_OS or Platform.IS_WINDOWS:
            path = str(path)

        # Result
        return path

    # Translator
    @staticmethod
    def translate(data):

        # Double backslash translation
        if data[0:1] == '\\': # pragma: no cover
            data = f'/{data[1:]}'

        # Double slash translation
        if data[0:2] == '//': # pragma: no cover
            data = data[1:]

        # Result
        return data
