#!/usr/bin/python

import re
import subprocess
import os
import socket

# -*- coding: utf-8 -*-

# Project Name: PackageMon
# File Name:    packagemon

__author__ = 'delgaka'


def atualiza():
    """
    Updating the system packages repo (apt-get update -qq).
    """

    subprocess.call(["apt-get", "update", "-qq"])


def setting_system_date():
    """
    Get the system date (date -u)
    """

    date_system = subprocess.Popen(["date", "-u"], stdout=subprocess.PIPE)
    date_system, date_err = date_system.communicate()
    date_system = date_system.replace("\n", "")
    return date_system


def setting_local_hostname():
    """
    Getting hostname.
    """

    local_hostname = subprocess.Popen(["hostname"], stdout=subprocess.PIPE)
    local_hostname, local_hostname_err = local_hostname.communicate()
    local_hostname = local_hostname.replace("\n", "")
    return local_hostname


def setting_host_ip():
    """
    Getting ip address (hostname -I)
    """

    ip = subprocess.Popen(["hostname", "-I"], stdout=subprocess.PIPE)
    ip, iperr = ip.communicate()
    # ip = ip.replace("\n", "")
    ip = re.search(".*\..*\..*\..*(?=\s+)", ip).group(0)
    ip = ip.replace(" ", "")
    return ip


def setting_system_info():
    """
    Running the lsb_release -a for system OS distribution
    """

    global output_shell
    try:
        shell1 = subprocess.Popen(["lsb_release", "-a"],
                                  stdout=subprocess.PIPE)
        shell2 = subprocess.Popen(["cut", "-f", "2"],
                                  stdin=shell1.stdout, stdout=subprocess.PIPE)
        output_shell, err = shell2.communicate()
        shell2.stdout.close()
        # output,err = shell1.communicate()
        shell1.stdout.close()
        output_shell = output_shell.split("\n")
    except Exception, e:
        print("Somethin goes wrong on the definir_pacotes_security()", e)

    if '' in output_shell:
        output_shell.remove('')

    """
    Output:
    0 - Distributor ID
    1 - Description
    2 - Release
    3 - Codename
    """

    dist_id = output_shell[0]
    print(dist_id)
    description = output_shell[1]
    print(description)
    release = output_shell[2]
    print(release)
    codename = output_shell[3]
    print(codename)

    print(output_shell)


def setting_security_packages():
    """
    Running the apt-show-versions to list upgreadables pacakges.
    Formatting the result in comma separated.
    (package,architecture,repo,current_version,new_version)
    """

    global output_shell
    try:
        shell1 = subprocess.Popen(["apt-show-versions", "-u"],
                                  stdout=subprocess.PIPE)
        # shell2 = subprocess.Popen(["grep", "\-security"],
        #    stdin = shell1.stdout, stdout = subprocess.PIPE)
        # output_shell,err = shell2.communicate()
        # shell2.stdout.close()
        output_shell, err = shell1.communicate()
        shell1.stdout.close()
        output_shell = output_shell.split("\n")
    except Exception, e:
        print("Package apt-show-versions not installed")
        subprocess.call(["apt-get", "install", "-qq", "apt-show-versions"])
        setting_security_packages()

    text = []

    # removing the blank item (garbage).
    if '' in output_shell:
        output_shell.remove('')

    # formatting the result
    for x in output_shell:
        package = re.search("^([^:]+)", x).group(0)
        platform = re.search("(?<=:)\w+", x).group(0)
        repository_temp = re.search("(?<=\/)\S+", x).group(0)

        try:
            # print(repository_temp)
            temp = repository_temp.split("-")
            repository = repository_temp
            if temp[0] == "Security":
                repo_type = str(1)
            else:
                repo_type = str(0)
        except Exception, e:
            repository = repository_temp
            repo_type = 0

        atual = re.search("(?<=\s)\S+", x).group(0)
        if atual == "*manually*":
            versao_atual = re.search("(?<=from )\S+", x).group(0)
            manual = str(1)
        else:
            versao_atual = atual
            manual = str(0)

        versao_nova = re.search("(?<= to ).*", x).group(0)

        '''
        Fields:
        package, platform, repository, repo_type, versao_atual,versao_nova
        '''
        a = (package + "," + platform + "," + repository + "," +
             repo_type + "," + manual + "," + versao_atual + "," + versao_nova)

        text.append(a)

    return text


def write_log(text):
    """
    Writing the log. /var/log/packagemon
    :param text:
    """

    try:
        log_text = open("/var/log/packagemon/packagemon.log", 'w')
        log_text.write(text)
        log_text.close()
    except:
        path = "/var/log/packagemon"
        os.makedirs(path, 0755)
        log_text = open('/var/log/packagemon/packagemon.log', 'w')
        log_text.close()
        write_log(text)
        return text


def envia_log(self):
    """
    Sending log to SIEM/BigData
    sock.sendto(<object>, ("<hostname>", <destination_port>))
    :param self:
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind(socket.gethostname(), 5055)
    sock.sendto(self, ("delgaka", 5000))


# atualiza()
data = setting_system_date()
hostname = setting_local_hostname()
output = setting_security_packages()
# ip = definir_ip()
setting_system_info()
log = ''

for i in output:
    log += data + "," + hostname + "," + i + "\n"
    # log += data + "," + hostname + "," + ip + ","  + i + "\n"

'''
Fields:
data,hostname,ip,pacote, arquitetura, repositorio,
repo_type (1 - Security, 0 - Non Security),
manual (1 - manually update, 0 - Non manually), versao_atual,versao_nova
'''
print(log)
write_log(log)
envia_log(log)
