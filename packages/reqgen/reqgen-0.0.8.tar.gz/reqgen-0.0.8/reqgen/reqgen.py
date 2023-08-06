#!/usr/bin/python
# -*- coding: utf-8 -*-

import click
import copy
import fnmatch
import operator
from six import iteritems
import os
import platform
import re
import requirements


def gt(first, second):
    """
    Compare two packages versions
    :param first: The first requirement
    :param second: Te second requirement
    :return: True if the first one is greater than the second
        or is the latest version
    """
    if not first.specs:
        return True
    if not second.specs:
        return False
    return first.specs[0][1] > second.specs[0][1]


def load_deps(filename):
    """
    Reads all the dependencies from a requirements file
    :param filename: The filename to load
    :return: A dict with the requirement name and the requirement object
    """
    reqs = dict()
    with open(filename, 'r') as req_file:
        lines = req_file.readlines()
        for line in lines:
            if not will_install(line):
                continue
            for req in requirements.parse(line):
                if req.name:
                    reqs.update({req.name.upper(): req})
                elif req.vcs:
                    reqs.update({req.uri.upper(): req})
    return reqs


def python_version():
    """
    If the env var TRAVIS_PYTHON_VERSION is defined will return that value,
    else will use the current python version
    :return: String with the python version
    """
    if os.environ.get('TRAVIS_PYTHON_VERSION', False):
        return os.environ.get('TRAVIS_PYTHON_VERSION')
    return platform.python_version()


def will_install(package_line):
    """
    Checks if a package will be installed according to the specification in the requirements file,
    will be installed if:
      - Proper python version is detected
      - Not for windows
      - If no python version is specified and is no specific for windows it will install
    :param package_line: the requirements file line
    :return: True or false according to the previous conditions
    """
    def compare(op, ver1, ver2):
        operators = {
            '<=': operator.le,
            '>=': operator.ge,
            '==': operator.eq,
            '<': operator.lt,
            '>': operator.gt
        }
        return operators[op](ver1, ver2)

    is_win32 = re.search(r'sys_platform\s+(==)\s+\'(.*?)\'', package_line)
    if is_win32:
        return False
    res = re.search(r'python_version\s+(<=?|>=?|==)\s+\'(.*?)\'', package_line)
    if not res:
        return True
    res_groups = res.groups()
    return compare(res_groups[0], python_version(), res_groups[1])


def merge_requirements(merge_to, merge_from, exclude_libs=False):
    """
    Takes a dict of requirements objects and merge
    :param merge_to: The first dict where you want to merge from
    :param merge_from: The second element where we want to merge from
    :return: A dict with the merged elements
    """
    exclude_libs = exclude_libs or []
    res = copy.deepcopy(merge_to)
    for name, req in iteritems(merge_from):
        if name in exclude_libs:
            continue
        if name not in res or gt(req, res.get(name)):
            res.update({name: req})
    return res


def generate_merged_file(dest_file, path, recursive=False, exclude=False,
                         requirements_name='requirements.txt'):
    file_list = search_reqs_files(path, recursive, requirements_name)
    for files in file_list:
        save_requirements(files, dest_file, exclude)


def save_requirements(requirementstxt, filename, exclude_path=False):
    """
    Take the requirements in the first file and save them to the second if they are
    newer or they're no present in the file
    :param requirementstxt: The requirements.txt file to parse
    :param filename: The file where all requirements will be saved
    :return: None. Just generates the file
    """
    if os.path.isfile(filename):
        fullreqs = load_deps(filename)
    else:
        fullreqs = dict()
    reqs = load_deps(requirementstxt)
    if not reqs:
        return
    exclude_libs = []
    if exclude_path and os.path.exists(exclude_path):
        exclude_libs = load_deps(exclude_path).keys()
    fullreqs = merge_requirements(fullreqs, reqs, exclude_libs)
    with open(filename, 'w') as req_file:
        for req in fullreqs.values():
            if req is not None:
                req_file.write(req.line + '\n')


def search_reqs_files(folder_name, recursive=False, requirements_name='requirements.txt'):
    """
    Searchs for all requirements.txt file recursively in the given path
    :param folder_name: the folder where you want to search
    :return: A list with all the files found, empty if none
    """
    res = list()
    for base, directories, files in os.walk(folder_name):
        for file_name in fnmatch.filter(files, requirements_name):
            res.append(os.path.join(base, file_name))
            if not recursive:
                # Clean the directories so the walk doesn't go any further
                del directories[:]
    return res


@click.command()
@click.option('--path',
              default='.',
              type=click.Path(exists=True, readable=True),
              help='Path where you what to search the requirements files'
              )
@click.argument('dest_file',
                type=click.Path(file_okay=True, writable=True))
@click.option("--recursive", is_flag=True, default=False, required=False,
              help="If true, reqgen will retrieve all the requirements in a"
              " path and all it's subdirectories, else, it will stop after"
              " the first requirements.txt found in a path")
@click.option('--exclude_path', default="",
              help='Path where store the requirements_exclude.txt')
def main(dest_file, path, recursive, exclude_path):
    default_exclude = os.path.join(os.path.dirname(dest_file), 'requirements_exclude.txt')
    exclude_path = exclude_path or default_exclude
    generate_merged_file(dest_file, path, recursive, exclude_path)
    return 0
