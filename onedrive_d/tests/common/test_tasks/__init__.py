import os

def setup_os_mock():
    call_hist = {
        'os.rename': [],
        'os.utime': [],
        'os.chown': []
    }
    os.rename = lambda old, new: call_hist['os.rename'].append((old, new))
    os.utime = lambda fp, tt: call_hist['os.utime'].append((fp, tt))
    os.chown = lambda fp, uid, gid: call_hist['os.chown'].append((fp, uid, gid))
    return call_hist
