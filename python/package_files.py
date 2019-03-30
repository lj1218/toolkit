# -*- coding: utf-8 -*-
u"""
Package files tool.

Author: lj1218
Create: 2019-03-29
Update: 2019-03-29
"""
import os
import sys
import time
from shutil import copy2, rmtree


def main():
    """Entry."""
    compress = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '-c':
            compress = True
        else:
            sys.stderr.write('Error: unknown option %s\n' % sys.argv[1])
            exit(1)
    config = {
        'data.src.root_dir': 'test-data',
        'data.dst.root_dir': '../test-data',
        'data.sub_dirs': [],
        'data.file.suffix': ['.index', '.data', '.plan'],
        'data.file.ignore': [],
        'compress': compress,
    }
    Packager(config).start()


class Configuration(object):
    """Configuration class."""

    def __init__(self, config):
        """Init."""
        self.__config = config
        self.src_root_dir = self.__get_src_root_dir()
        self.dst_root_dir = self.__get_dst_root_dir()
        self.dst_root_dir_basename = os.path.basename(self.dst_root_dir)
        self.dst_root_dir_parent = os.path.dirname(
            os.path.abspath(self.dst_root_dir))
        self.sub_dirs = self.__get_sub_dirs()
        self.suffix = config['data.file.suffix']
        self.files_ignore = config['data.file.ignore']
        self.compress = config['compress']
        self.compressed_file = self.dst_root_dir_basename + '.tar.gz'
        self.__check_config()

    def __get_src_root_dir(self):
        src_root_dir = self.__config['data.src.root_dir']
        if src_root_dir[-1] == '/':
            src_root_dir = src_root_dir[:-1]
        return src_root_dir

    def __get_dst_root_dir(self):
        dst_root_dir = self.__config['data.dst.root_dir']
        if dst_root_dir[-1] == '/':
            dst_root_dir = dst_root_dir[:-1]
        return dst_root_dir

    def __get_sub_dirs(self):
        dirs = self.__config['data.sub_dirs']
        if dirs is None or len(dirs) == 0:
            dirs = ['']
        return dirs

    def __check_config(self):
        if self.dst_root_dir == self.src_root_dir:
            sys.stderr.write('Error: dst_root_dir equals src_root_dir\n')
            exit(1)
        if not os.path.exists(self.src_root_dir):
            sys.stderr.write(
                'Error: src_root_dir %s not exists, please check it\n'
                % self.src_root_dir
            )
            exit(1)
        if not os.path.isdir(self.src_root_dir):
            sys.stderr.write(
                'Error: src_root_dir %s is not a directory, please check it\n'
                % self.src_root_dir
            )
            exit(1)
        if os.path.exists(self.dst_root_dir):
            sys.stderr.write(
                'Error: dst_root_dir %s exists, please remove it first\n'
                % self.dst_root_dir
            )
            exit(1)


class Packager(object):
    """Package files."""

    def __init__(self, config):
        """Init."""
        self.__start_time = time.time()
        self.cfg = Configuration(config)
        self.__src_file_list = self.__get_src_file_list()
        self.__dst_file_list = self.__get_dst_file_list()

    def start(self):
        """Start packager."""
        self.__prepare()
        self.__copy()
        self.__compress()
        self.__print_cost_time('total', self.__start_time)

    def __prepare(self):
        def create_dir(path):
            if path == '':
                return
            if not os.path.exists(path):
                os.makedirs(path)

        def make_dirs(file_list):
            dirs = set()
            for f in file_list:
                dirs.add(os.path.dirname(f))
            for d in dirs:
                create_dir(d)

        start_time = time.time()
        if self.cfg.compress:
            self.__remove_file(os.path.join(
                self.cfg.dst_root_dir_parent, self.cfg.compressed_file
            ))
        create_dir(self.cfg.dst_root_dir)
        make_dirs(self.__dst_file_list)
        self.__print_cost_time('prepare', start_time)

    def __copy(self):
        start_time = time.time()
        total_files = len(self.__src_file_list)
        i = 0
        for src, dst in zip(self.__src_file_list, self.__dst_file_list):
            i += 1
            print('(%d/%d) => %s' % (i, total_files, os.path.basename(src)))
            copy2(src, dst)
        print('%d files copied' % total_files)
        self.__print_cost_time('copy', start_time)

    def __compress(self):
        if not self.cfg.compress:
            return
        print('start compressing...')
        compress_cmd = 'cd %s && tar zcf %s %s && cd - >/dev/null' % (
            self.cfg.dst_root_dir_parent, self.cfg.compressed_file,
            self.cfg.dst_root_dir_basename)
        start_time = time.time()
        os.system(compress_cmd)
        print('compress done')
        self.__print_cost_time('compress', start_time)
        self.__remove_dir(self.cfg.dst_root_dir)

    def __get_src_file_list(self):
        file_list = []
        for sub_dir in self.cfg.sub_dirs:
            try:
                file_list.extend(
                    self.__get_file_list0(
                        os.path.join(self.cfg.src_root_dir, sub_dir),
                        files_ignore=self.cfg.files_ignore,
                        suffix=self.cfg.suffix, recursive=True
                    )
                )
            except OSError as e:
                sys.stderr.write(str(e) + '\n')
                exit(1)

        return file_list

    def __get_dst_file_list(self):
        src_file_list = self.__src_file_list
        root_dir_src = self.cfg.src_root_dir
        root_dir_dst = self.cfg.dst_root_dir
        dst_file_list = []
        for src_file in src_file_list:
            dst_file = src_file.replace(
                root_dir_src, root_dir_dst, 1)
            dst_file_list.append(dst_file)
        return dst_file_list

    @staticmethod
    def __get_file_list0(directory, files_ignore=None,
                         suffix=None, recursive=False):
        file_list = []
        for f in os.listdir(directory):
            file_path = os.path.join(directory, f)
            if os.path.isdir(file_path):
                if recursive:
                    file_list.extend(
                        Packager.__get_file_list0(
                            file_path, files_ignore, suffix, recursive))
            else:
                if Packager.__suffix_matched(file_path, suffix) and \
                        not Packager.__ignore_file(file_path, files_ignore):
                    file_list.append(file_path)
        return file_list

    @staticmethod
    def __suffix_matched(file_path, suffix):
        if suffix is not None:
            for sf in suffix:
                if file_path.endswith(sf):
                    break
            else:
                return False
        return True

    @staticmethod
    def __ignore_file(file_path, files_ignore):
        if files_ignore is not None:
            if os.path.basename(file_path) in files_ignore:
                return True
        return False

    @staticmethod
    def __remove_dir(dir_path):
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            rmtree(dir_path)
            print('remove %s' % dir_path)

    @staticmethod
    def __remove_file(file_path):
        try:
            os.remove(file_path)
            print('remove %s' % file_path)
        except OSError:
            pass

    @staticmethod
    def __print_cost_time(desc, start_time):
        print('[%s] cost %lfs' % (desc, (time.time() - start_time)))


if __name__ == '__main__':
    main()
