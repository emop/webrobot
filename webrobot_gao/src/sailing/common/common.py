import os, shutil, glob, re, time, datetime, sys, traceback
import StringIO
import fnmatch
import hashlib
import zipfile
import subprocess

#### OS PATH File

def join_path(*args):
    return os.path.normpath(os.path.join(*args))

def current_path():
    return os.getcwd()

def dir_name(path):
    return os.path.dirname(path)

def base_name(path):
    return os.path.basename(path)

def norm_path(path):
    return os.path.normpath(path)

def exists_path(path):
    return os.path.exists(path)

def is_file(path):
    return os.path.isfile(path)

def is_dir(path):
    return os.path.isdir(path)

def is_empty_dir(path):
    return is_dir(path) and len(os.listdir(path)) == 0

def file_ctime(path):
    return os.stat(path).st_ctime

def file_mtime(path):
    return os.stat(path).st_mtime

def file_size(path):
    return exists_path(path) and os.stat(path).st_size or 0
    
def make_path(path):
    not exists_path(path) and os.makedirs(path)

def make_path_as_lock(path, raise_exception=False):
    try:
        os.makedirs(path)
    except:
        if raise_exception:
            raise Exception, trackable('Could not create %s' % path)
        else:
            return False
    else:
        return True

def copy_to(src, dst):
    shutil.copyfile(src, dst)
    
def move_to(src, dst):
    import os
    if os.sep == '\\':
        data = read_from_file(src)
        write_to_file(dst, data)
        remove_path(src)
    else:
        shutil.move(src, dst)

def move_to_dir(src, dst):
    make_path(dst)
    move_to(src, dst)
            
def remove_path(path):
    if is_file(path):
        os.remove(path)
    elif is_dir(path):
        shutil.rmtree(path)
    else:
        pass

def read_from_file(path):
    f = open(path, 'r')
    content = f.read()
    f.close()
    return content
    
def write_to_file(path, content='', mode='w'):
    make_path(dir_name(path))
    f = open(path, mode)
    f.write(content)
    f.close()

def extract_file(self, todir, name):
    if name in self.namelist():
        try:
            f = open(join_path(todir, name), 'wb')
            f.write(self.read(name))
            f.close()
        except IOError:
            pass
zipfile.ZipFile.extract_file = extract_file
    
#### Time

def sleep(t):
    time.sleep(t)

def now():
    return datetime.datetime.now()

def strnow():
    return str(datetime.datetime.now())
    
def time_to_str(f='%Y%m%d%H%M%S', t=None):
    if t:
        return time.strftime(f, t)
    else:
        return time.strftime(f)

def str_time_add_day(t, delta, f='%Y%m%d'):
    return (datetime.datetime.strptime(t, '%Y%m%d') + datetime.timedelta(days=delta)).strftime(f)

#### Exception

def trackable(msg):
    return '%s\n%s' % (type(msg) == type('') and msg or str(msg), traceback.format_exc())
    
def safe_call(func, args, message, logger=None, level='TRACE', level_in_error='WARN'):
    try:
        func(*args)
        logger and logger.log('Success - %s' % message, level)
        return True
    except:
        logger and logger.log(trackable('Failed - %s' % message), level_in_error)
        return False

def run_command(command, logger, level='DEBUG', working_dir=None):
    try:
        temp_path = join_path(logger.path, '.%s.run_command.out' % time_to_str())
        f = open(temp_path, 'w')
        if working_dir:
            subprocess.call(command, shell=True, stdout=f, stderr=f, cwd=working_dir)
        else:
            subprocess.call(command, shell=True, stdout=f, stderr=f)
    except:
        raise
        return logger.log(trackable('Run command failed\n%s\n%s' % (command, output)))
    finally:
        try:
            f.close()
        except:
            pass
    output = read_from_file(temp_path).strip()
    try:
        remove_path(temp_path)
    except:
        pass
    return logger.log('Run command\n%s\n%s' % (command, output), level)

#### Others 

def user_input(prompt):
    return raw_input(prompt).replace('\r', '').replace('\n', '')

def fn_match(s, p):
    return fnmatch.fnmatch(s, p)
    
def hash_code(s):
    return hashlib.md5(s).hexdigest()

class Notifier(object):
    def __init__(self):
        pass
    
    def notify(self, source, msg):
        print 'Notification: source = %s; message = %s' % (source, msg)

#### Testing
if __name__ == '__main__':
    pass