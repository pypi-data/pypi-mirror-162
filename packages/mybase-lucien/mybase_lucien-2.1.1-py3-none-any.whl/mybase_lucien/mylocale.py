def is_exec():
    import sys
    if getattr(sys, 'frozen', False):
        return True
    else:
        return False
def get_dir(myfile=__file__):
    import os
    if is_exec():
        import sys
        mydir=os.path.dirname(os.path.abspath(sys.executable))
    else:
        mydir=os.path.dirname(os.path.abspath(myfile))
    return mydir