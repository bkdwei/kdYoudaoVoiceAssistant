# coding: utf-8
from os.path import realpath,dirname,join,exists,isdir,isfile
from os import makedirs,remove,removedirs
from logging import getLogger
logger = getLogger(__name__)
# LOG.info('Process ID: %s', os.getpid())
# LOG.debug("cache dir: '%s'", args.cachedir)

# 当前包所在的目录
cur_dir = dirname(realpath(__file__))

# 获取包内的文件
def get_file_realpath(file):
    return join(cur_dir,file)
# 创建文件
def check_and_create_file(absolute_file_path):
    path = dirname(absolute_file_path)
    # 检查目录
    if not exists(path) :
        try:
            makedirs(path)
        except Exception as e:
            logger.error("创建目录失败,%s",str(e)) 
    elif not isdir(path) :
        print(path + "不是一个目录，删除并新建相应的目录")
        try:
            remove(path)
            makedirs(path)
        except Exception as e:
            logger.error("创建目录失败,%s",str(e)) 
    # 检查文件
    if not exists(absolute_file_path) :
        with open(absolute_file_path, "w",encoding="utf-8"):
            pass
    elif not isfile(absolute_file_path) :
        try:
            removedirs(absolute_file_path)
            with open(absolute_file_path, "w",encoding="utf-8"):
                pass
        except Exception as e:
            logger.error("创建文件失败,%s",str(e)) 

def check_and_create_dir(absolute_dir_path):
    if not exists(absolute_dir_path) :
        makedirs(absolute_dir_path)
    elif not isdir(absolute_dir_path) :
        print(absolute_dir_path + "不是一个目录，删除并新建相应的目录")
        try:
            remove(absolute_dir_path)
            makedirs(absolute_dir_path)
        except Exception as e:
            logger.error("创建目录失败,%s",str(e)) 
