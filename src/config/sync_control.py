import os
import crypt
import subprocess
import getpass
import logging.handlers
import socket
import sys

from ntplib import NTPClient, NTPException


logger = logging.getLogger('__main__')

c = NTPClient()

fname = '/etc/chrony/chrony.conf'

pw = None

def get_pw():
    global pw

    print("Enter your password to verify synchronization")

    fault_cnt = 0
    for i in range(5):
        if 'PYCHARM_HOSTED' in os.environ:
            user_password = input('Password: ')
        else:
            user_password = getpass.getpass(prompt='Password: ')

        # 패스워드 검증
        proc = subprocess.Popen(['sudo', '-S', 'cat', '/etc/shadow'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate(input=user_password + '\n')

        sys_password = None

        for line in out.split('\n'):
            try:
                username, password, *rest = line.split(':')
                if username == getpass.getuser():
                    sys_password = password
                    break
            except ValueError as e:
                pass

        if sys_password is not None:
            if crypt.crypt(user_password, sys_password) == sys_password:
                pw = user_password
                break
            else:
                fault_cnt += 1
                logger.warning(f'Access denied. Try again... [{fault_cnt}/5]')
        else:
            logger.error("Can't access to your system.")

    if pw is None:
        logger.warning("Exceeded maximum attempts.")
        logger.warning("Program is shutdown.")
        sys.exit(0)
    else:
        logger.info('Access approved.')

def setup_chrony(ip):
    get_pw()

    with open(fname, 'r') as file:
        file_content = file.readlines()

    add_conf = True
    end_line = None

    for i, line in enumerate(file_content):
        if 'maxsources' in line:
            if not line[0] == '#':
                file_content[i] = '# ' + line.strip() + '\n'
            end_line = i

        if f'server {ip} iburst' in line:
            add_conf = False

    if add_conf and end_line is not None:
        sudo_cmd(f'cp {fname} /etc/chrony/chrony_backup.conf')

        file_content.insert(end_line + 1, f'\nserver {ip} iburst\n')
        file_content.insert(end_line + 2, 'maxdistance 16.0\n')

        with open('chrony.conf', 'w') as file:
            file.writelines(file_content)

        sudo_cmd(f'mv chrony.conf {fname}')
        logger.info(f"Complete synchronization config setup.")

        sudo_cmd('systemctl enable chrony')
        logger.info(f"Enable synchronization service.")

        sudo_cmd('systemctl start chrony')
        logger.info(f"Start synchronization service.")

def sudo_cmd(cmd):
    os.system(f'echo {pw} | sudo -S {cmd}')

def restart_chrony():
    sudo_cmd('systemctl restart chrony')

def get_latency(ip):
    try:
        response = c.request(ip, version=3)

        return response.offset * 1000.0

    except NTPException as e:
        return e
