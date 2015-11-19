#!/usr/bin/python
# -*- coding: utf-8 -*-

# Project Name: PackageMon
# File Name:    packagemon

__author__ = 'delgaka'

import re
import subprocess
import os
import socket

def atualiza():
    """
    Updating the system packages repo (apt-get update -qq).
    """

    subprocess.call(["apt-get", "update", "-qq"])


def definir_data():
    """
    Get the system date (date -u)
    """

    data = subprocess.Popen(["date", "-u"], stdout = subprocess.PIPE)
    data,dataerr = data.communicate()
    data = data.replace("\n", "")
    return data


def definir_hostname():
    """
    Getting hostname.
    """

    hostname = subprocess.Popen(["hostname"], stdout = subprocess.PIPE)
    hostname, hostnameerr = hostname.communicate()
    hostname = hostname.replace("\n", "")
    return hostname


def definir_ip():
    """
    Getting ip address (hostname -I)
    """

    ip = subprocess.Popen(["hostname", "-I"], stdout = subprocess.PIPE)
    ip, iperr = ip.communicate()
    #ip = ip.replace("\n", "")
    ip = re.search(".*\..*\..*\..*(?=\s+)", ip).group(0)
    ip = ip.replace(" ","")
    return ip


def definir_info_system():
    """
    Running the lsb_release -a for system OS distribution
    """

    try:
        shell1 = subprocess.Popen(["lsb_release", "-a"],
                stdout = subprocess.PIPE)
        shell2 = subprocess.Popen(["cut", "-f", "2"],
            stdin = shell1.stdout, stdout = subprocess.PIPE)
        output,err = shell2.communicate()
        shell2.stdout.close()
        #output,err = shell1.communicate()
        shell1.stdout.close()
        output = output.split("\n")
    except Exception, e:
        print("Somethin goes wrong on the definir_pacotes_security()", e)

    if '' in output:
        output.remove('')

    """
    Output:
    0 - Distributor ID
    1 - Description
    2 - Release
    3 - Codename
    """

    dist_id = output[0]
    print(dist_id)
    description = output[1]
    print(description)
    release = output[2]
    print(release)
    codename = output[3]
    print(codename)

    print(output)


def definir_pacotes_security():
    """
    Running the apt-show-versions to list upgreadables pacakges.
    Formating the result in comma separated.
    (package,architeture,repo,cuurent_version,new_version)
    """

    try:
        shell1 = subprocess.Popen(["apt-show-versions", "-u"],
                stdout = subprocess.PIPE)
        #shell2 = subprocess.Popen(["grep", "\-security"],
        #    stdin = shell1.stdout, stdout = subprocess.PIPE)
        #output,err = shell2.communicate()
        #shell2.stdout.close()
        output,err = shell1.communicate()
        shell1.stdout.close()
        output = output.split("\n")
    except Exception, e:
        print("Package apt-show-versions not installed")
        subprocess.call(["apt-get", "install", "-qq", "apt-show-versions"])
        definir_pacotes_security()

    texto = []

    #removing the blank item (garbage).
    if '' in output:
        output.remove('')

    #formating the result
    for i in output:
        pacote = re.search("^([^:]+)", i).group(0)
        arquitetura = re.search("(?<=:)\w+", i).group(0)
        repositorio_temp = re.search("(?<=\/)\S+", i).group(0)

        try:
            #print(repositorio_temp)
            temp = repositorio_temp.split("-")
            repositorio = repositorio_temp
            if temp[0] == "Security" :
                repo_type = str(1)
            else:
                    repo_type = str(0)
        except Exception, e:
            repositorio = repositorio_temp
            repo_type = 0

        atual = re.search("(?<=\s)\S+", i).group(0)
        if atual == "*manually*":
            versao_atual = re.search("(?<=from )\S+",i).group(0)
            manual = str(1)
        else:
            versao_atual = atual
            manual = str(0)

        versao_nova = re.search("(?<= to ).*", i).group(0)

        '''
        Fields:
        pacote, arquitetura, repositorio, repo_type, versao_atual,versao_nova
        '''
        a = (pacote + "," + arquitetura + "," + repositorio + ","
            + repo_type + "," + manual + "," + versao_atual + "," + versao_nova)

        texto.append(a)

    return texto

def escreve_log(texto):
    """
    Writing the log. /var/log/packagemon
    """

    try:
        log = open('/var/log/packagemon/packagemon.log', 'w')
        log.write(texto)
        log.close()
    except:
        path = "/var/log/packagemon"
        os.makedirs(path, 0755)
        log = open('/var/log/packagemon/packagemon.log', 'w')
        log.close()
        escreve_log(texto)
        return texto

def envia_log(log):
    """
    Sending log to SIEM/BigData
    sock.sendto(<object>, ("<hostname>", <destination_port>))
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.bind(socket.gethostname(), 5055)
    sock.sendto(log, ("delgaka", 5000))


#atualiza()
data = definir_data()
hostname = definir_hostname()
output = definir_pacotes_security()
#ip = definir_ip()
definir_info_system()
log = ''

for i in output:
    log += data + "," + hostname + ","  + i + "\n"
    #log += data + "," + hostname + "," + ip + ","  + i + "\n"

'''
Fields:
data,hostname,ip,pacote, arquitetura, repositorio,
repo_type (1 - Security, 0 - Non Security),
manual (1 - manually update, 0 - Non manually), versao_atual,versao_nova
'''
print(log)
escreve_log(log)
envia_log(log)