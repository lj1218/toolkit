# -*- coding: utf-8 -*-
u"""
Generate download links for files on github.
Author: lj1218
Create: 2019-07-27
Update: 2019-07-27
"""
import os
import sys


def main():
    """Entry."""
    github_username = 'lj1218'  # replace it with your username
    suffix = ['.pdf', '.epub', '.rar', '.zip', '.7z']  # add as needed
    prefix = 'https://github.com/' + github_username + '/'
    insertion = 'raw/master'

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        sys.stderr.write('Usage: %s <directory>\n' % sys.argv[0])
        exit(1)

    if not os.path.isdir(os.path.join(directory, '.git')):
        sys.stderr.write('Error: %s is not root dir of git project\n' % sys.argv[0])
        exit(1)

    __gen_links(directory, prefix, insertion, suffix)


def __gen_links(directory, prefix, insertion, suffix):
    project_name = __get_project_name(directory)
    for file in __get_file_list(directory, suffix=suffix, recursive=True):
        file = file.replace(directory, '', 1)
        print('[' + os.path.basename(file) + ']' + \
       	    '(' + prefix + project_name + insertion + file + ')')


def __get_file_list(directory, files_ignore=None, suffix=None, recursive=False):
    """Get file list."""
    file_list = []
    for f in os.listdir(directory):
        if f.startswith('.'):
            # ignore hidden file and directories.
            continue
        file_path = os.path.join(directory, f)
        if os.path.isdir(file_path):
            if recursive:
                file_list.extend(__get_file_list(file_path, files_ignore,
                                               suffix, recursive))
        else:
            if __suffix_matched(file_path, suffix) and \
                    not __ignore_file(file_path, files_ignore):
                file_list.append(file_path)
    return file_list


def __suffix_matched(file_path, suffix):
    if suffix is not None:
        for sf in suffix:
            if file_path.endswith(sf):
                break
        else:
            return False
    return True


def __ignore_file(file_path, files_ignore):
    if files_ignore is not None:
        if os.path.basename(file_path) in files_ignore:
            return True
    return False


def __get_project_name(directory):
    basename = os.path.basename(directory)
    if basename == '.':
        return os.path.basename(os.getcwd()) + '/'
    return basename + '/'


if __name__ == '__main__':
    project_name = ''
    main()
