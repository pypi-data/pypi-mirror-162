#!/usr/bin/env python
import subprocess
import os
from shutil import copyfile


def _cmd(command):
    if 'QCREDTOKEN' in os.environ:
        del os.environ['QCREDTOKEN']
    p = subprocess.Popen(command, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=False)
    output, err = p.communicate()
    return p.returncode, output, err


def is_systemd_supported() -> bool:
    supported = False
    code, stdout, sdterr = _cmd('/usr/bin/systemctl --version')
    if code == 0:
        supported = True
    return supported


def _uninstall():
    systemd_supported = is_systemd_supported()
    if not systemd_supported:
        files = ['/etc/init.d/infiniguard_api',
                 '/etc/httpd/conf.d/infiniguard_api.conf']
        _cmd('/sbin/service infiniguard_api stop')
        _cmd('/sbin/chkconfig --del infiniguard_api')
    else:
        files = ['/etc/httpd/conf.d/infiniguard_api.conf',
                 '/etc/systemd/system/infiniguard_api.service']
        _cmd('/usr/bin/systemctl disable --now infiniguard_api')

    for f in files:
        if os.path.exists(f):
            os.remove(f)


def postinstall():

    basedir = os.path.dirname(os.path.realpath(__file__))
    _uninstall()
    systemd_supported = is_systemd_supported()

    if not systemd_supported:
        src = ['init.infiniguard_api', 'infiniguard_api.conf']
        dst = ['/etc/init.d/infiniguard_api',
               '/etc/httpd/conf.d/infiniguard_api.conf']
    else:
        src = ['infiniguard_api.service', 'infiniguard_api.conf']
        dst = ['/etc/systemd/system/infiniguard_api.service',
               '/etc/httpd/conf.d/infiniguard_api.conf']

    for src_file, dst_file in zip(src, dst):
        copyfile(basedir + '/' + src_file, dst_file)
        os.chmod(dst_file, 0o644)

    if not systemd_supported:
        _cmd('/sbin/chkconfig --add infiniguard_api')
        _cmd('/sbin/chkconfig infiniguard_api on')
        os.chmod('/etc/init.d/infiniguard_api', 0o755)
        code, stdout, stderr = _cmd('/sbin/service infiniguard_api start')
        if code != 0:
            print('Cannot start infiniguard_api service')
            return 1
    else:
        _cmd('/usr/local/sbin/systemctl daemon-reload')
        code, stdout, stderr = _cmd('/usr/local/sbin/systemctl enable --now infiniguard_api')
        if code != 0:
            print('Cannot start infiniguard_api service')
            return 1
    _cmd('/sbin/service httpd restart')

    return 0


def preuninstall():
    _uninstall()
    systemd_supported = is_systemd_supported()
    if not systemd_supported:
        _cmd('/sbin/service httpd restart')
    else:
        _cmd('/usr/bin/systemctl restart httpd')
        _cmd('/usr/local/sbin/systemctl daemon-reload')
    return 0
