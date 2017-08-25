# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 15:49:30 2017 CST

author: Raynor Li

NetScaler Appliance Slient Upgrade Script
"""

import paramiko
import sys
import time
import os
import pexpect
from pexpect import pxssh

class NS_Slient_Upgrade(object):

    def __init__(self):

        print('Create a NetScaler Silent Upgrade Project!')
        global remotename
        remotename = raw_input('Target NetScaler IP: ')


    def connect(self,remotename,remoteport,loginname,loginpassword):

        try:
            #remotename = raw_input("Target NetScaler IP:")
            sftp = paramiko.Transport(remotename,remoteport)
            print('Connect to NetScaler success!')
        except Exception as e:
            print('Connect failed,reasons are as follows:',e)
            return (0,'connect failed!')
        else:
            try:
                sftp.connect(username = loginname,password = loginpassword)
                print('Login NetScaler success!')

            except Exception as e:
                print('Login failed,reasons are as follows:',e)
                return (0,'login failed!')
            else:
                return (1,sftp)



    def upload(self,remotename,remoteport,loginname,loginpassword,remoteaddress,localaddress):

        sftp = self.connect(remotename,remoteport,loginname,loginpassword)

        sftp = paramiko.SFTPClient.from_transport(sftp[1])

        global build
        build = raw_input("Target Upgrade Firmware: ")
        try:
            sftp.stat(os.path.join(remoteaddress,build))
            print('Target Build EXIST\r\nInstalling......')
			
        except:
            print('Target Build NOT exist on NetScaler\r\nUploading......')

            sftp.put(localaddress+build, remoteaddress+build)
           # end = time.clock()
            print('======================')
            print('Uploaded %s\r\nInstalling......' % build)

            try:
                ssh_command = pxssh.pxssh()
                ssh_command.PROMPT= '> '           #self-defined original prompt 
                ssh_command.login(remotename, loginname, loginpassword,auto_prompt_reset=False)
                ssh_command.prompt()
                ssh_command.sendline('shell')   # run a command
                ssh_command.prompt()
                ssh_command.sendline('mkdir /var/nsinstall/%s && ls -l /var/nsinstall' % build[0:-4])
                ssh_command.prompt()
                ssh_command.sendline('tar xzvf /var/nsinstall/%s -C /var/nsinstall/%s' % (build, build[0:-4]))
                ssh_command.prompt()

            except Exception,e:
                print e

    def upgrade(self):		
        child = pexpect.spawn('ssh -l nsroot %s' % remotename)
        child.expect('Password:')
        child.sendline('nsroot')
        child.expect('>')
        child.sendline('save ns config')
        child.expect('>')
        child.sendline('shell')
        child.expect('#')
        child.sendline('cd /var/nsinstall/%s && installns' % build[0:-4])
        child.expect_exact('Do you want to enable it NOW? [Y/N]')
        child.sendline('No')
        child.expect_exact('Reboot NOW? [Y/N]', timeout=60) #timeout=60 is removed for test
        child.sendline('Y')
        child.expect('#')
        child.sendline('/sbin/reboot')
        time.sleep(5)
        child.expect('#')
        #child.sendline('pwd')
        #child.expect('#')
        print('Slient Upgrade Success......Waiting For Appliance Restart')



def main():
    sftp = NS_Slient_Upgrade()
    sftp.upload(remotename,#'10.158.153.248',
                              remoteport=22,     #SFTP的默认端口号是21
                              loginname = 'nsroot',
                              loginpassword = 'nsroot',
                              remoteaddress='/var/nsinstall/',
                              localaddress = '/mnt/nfs/Share/Netscaler Group/Fireware/')

    sftp.upgrade(#remotename = '10.158.153.248',
				#loginpassword = 'nsroot'
                )	

if __name__ == '__main__':
    main()                
