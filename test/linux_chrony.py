# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-ch', '--chrony', action='store_true', help='chrony installation on/off')
parser.add_argument('-i', '--ip', type=str, help='server ip to sync (ex.10.252.101.xxx)')
parser.add_argument('-r', '--run', action='store_true', help='run chrony and check synchronization')
parser.add_argument('-b', '--bashrc', action='store_true', help='set keyboard shortcuts')
args = parser.parse_args()

# chrony 설치
if args.chrony:
    print('[INFO] Install chrony')
    os.system("apt-get update")
    os.system("apt install chrony")
    print('-' * 100)

# chrony.conf 내용 수정
if args.ip is not None:
    print('[INFO] Edit ''chrony.conf'' file')
    file_name = '/etc/chrony/chrony.conf'
    with open(file_name, 'r') as file:
        file_content = file.readlines()

    for i, line in enumerate(file_content):
        if 'maxsources' in line:
            file_content[i] = '# ' + line.strip() + '\n'
            end_line = i

    file_content.insert(end_line+1, 'server ' + args.ip + ' iburst\n')
    file_content.insert(end_line+2, 'maxdistance 16.0\n')

    with open(file_name, 'w') as file:
        file.writelines(file_content)
    print('-' * 100)

# chrony 자동 실행 설정 및 시간 동기화 확인
if args.run:
    print('[INFO] Setting chrony auto start')
    os.system("systemctl enable chrony")
    os.system("systemctl start chrony")
    print('-' * 100)
    print('[INFO] Check System clock synchronized (yes)')
    os.system("timedatectl")
    print('-' * 100)
    if args.ip is not None:
        print('[INFO] Check Source state (*) / IP address (' + args.ip + ')')
    else:
        print('[INFO] Check Source state (*) / IP address')

    os.system("chronyc sources -v")
    print('-' * 100)

# chrony 재실행 및 시간 동기화 확인 단축키 추가
if args.bashrc:
    print('[INFO] Setting keyboard shortcuts')
    print('[INFO] Shortcut1 < chrony > : restart chrony')
    print('[INFO] Shortcut2 < offset > : offset from server to client')
    os.system("echo \"alias chrony='sudo systemctl restart chrony'\" >> ~/.bashrc")
    os.system("echo \"alias offset='chronyc sources -v'\" >> ~/.bashrc")
    os.system("/bin/bash")
    os.system("bash -c 'source ~/.bashrc'")