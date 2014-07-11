#!/usr/bin/python

import os, sys

def _init_pythonpath():
    abs_path = os.path.dirname(os.path.abspath(__file__))
    
    lib_path = os.path.join(abs_path, "..", "libs")
    lib_path = os.path.normpath(lib_path)
    
    src_path = os.path.join(abs_path, "..", "src")
    src_path = os.path.normpath(src_path)

    prj_lib_path = os.path.join(abs_path, "libs")
    prj_lib_path = os.path.normpath(prj_lib_path)
    
    sys.path.insert(0, src_path)
    sys.path.insert(0, lib_path)
    sys.path.insert(0, prj_lib_path)
    
    print "current dir:%s" % abs_path
    os.chdir(abs_path)
    
def start():
    if len(sys.argv) > 1:
        os.environ['TASK_ID'] = sys.argv[1]
            
    from sailing.common.utils import import_class
    command = "sailing.core.commands.%s.Command" % 'run'
    cmd_cls = import_class(command)

    cmd = cmd_cls()
    cmd.execute("webrobot")

if __name__ == '__main__':
    _init_pythonpath()
    start()
    
    