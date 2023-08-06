import socket
import logging
log = logging.getLogger(__name__)
import paramiko
from paramiko.file import BufferedFile

def host_is_local(hostname, port=None):
    """returns True if the hostname points to the localhost, otherwise False."""
    if hostname in ("localhost", "0.0.0.0", "127.0.0.1"):
        return True
    hostname = socket.getfqdn(hostname)
    print(hostname)
    if hostname in ("localhost", "0.0.0.0", "127.0.0.1"):
        return True
    localhost = socket.gethostname()
    localaddrs = socket.getaddrinfo(localhost, None)
    targetaddrs = socket.getaddrinfo(hostname, None)
    for (family, socktype, proto, canonname, sockaddr) in localaddrs:
        for (rfamily, rsocktype, rproto, rcanonname, rsockaddr) in targetaddrs:
            if rsockaddr[0] == sockaddr[0]:
                return True
    return False

#print(host_is_local('172.24.4.55'))
#print(host_is_local('m7-pce-dev01'))
#print(host_is_local('192.168.122.1'))
#print(host_is_local('172.17.0.1'))
#print(host_is_local('172.22.0.1'))
#print(host_is_local('172.19.0.1'))
#print(host_is_local('172.18.0.1'))
#print(host_is_local('0.0.0.0'))
#print(host_is_local('127.0.0.1'))
#print(host_is_local('172.24.4.56'))

def buf2str(buf: BufferedFile) -> str:
    return buf.read().decode("utf-8")

ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect('172.24.4.40')
_, stdout, stderr = ssh_client.exec_command('whoami && pwd')
print(buf2str(stdout))
err = buf2str(stderr)
cmd = 'export JAVA_HOME=/usr/java/jdk1.8 && cd /mnt/disk0/home/denglong/env/openmldb/openmldb-0.5.0-linux/spark-3.0.0-bin-openmldbspark/jars && java -cp openmldb-batch-0.6.0-* com._4paradigm.openmldb.batch.utils.VersionCli'
cmd = 'cd /mnt/disk0/home/denglong/env/openmldb/openmldb-0.5.0-linux/spark-3.0.0-bin-openmldbspark/jars && java -cp openmldb-batch-0.6.0-* com._4paradigm.openmldb.batch.utils.VersionCli'
_, stdout, err = ssh_client.exec_command(
    #f'java -cp {batch_jar_path} com._4paradigm.openmldb.batch.utils.VersionCli')
    cmd)
print(cmd)
print(buf2str(err))
print(buf2str(stdout))
