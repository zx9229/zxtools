import os
import paramiko
import stat


class sftptool(object):
    @staticmethod
    def sftpClient(host, port, user, pswd, *args, **kwargs):
        client = paramiko.Transport((host, int(port)))
        client.connect(username=user, password=pswd)
        sftpObj = paramiko.SFTPClient.from_transport(client)
        return sftpObj

    @staticmethod
    def sftpClientPPK(host, port, user, privateKey, *args, **kwargs):
        rsaKey = paramiko.RSAKey.from_private_key_file(privateKey)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, int(port), user, pkey=rsaKey)
        sftpObj = paramiko.SFTPClient.from_transport(ssh.get_transport())
        return sftpObj

    @staticmethod
    def sftpClientClose(sftpCli: paramiko.SFTPClient):
        sftpCli.close()

    @staticmethod
    def sftpGet(sftpCli: paramiko.SFTPClient, remotePath, localPath):
        """  paramiko.SFTPClient  """
        if localPath[-1:] in ('/', '\\'):
            localPath = os.path.join(localPath, os.path.basename(remotePath))
        elif localPath[-1:] == os.curdir:
            localPath = os.path.join(os.path.dirname(localPath), os.path.basename(remotePath))  # yapf: disable
        localPath = localPath.replace('\\', '/')
        remotePath = remotePath.replace('\\', '/')
        dirName = os.path.dirname(localPath)
        if dirName:
            os.makedirs(dirName, exist_ok=True)
        sftpCli.stat(remotePath)  # 检查远程文件/文件夹是否存在.
        sftpCli.get(remotePath, localPath)  # (remotePath)和(localPath)必须都是文件.
        return localPath

    @staticmethod
    def sftpPut(sftpCli: paramiko.SFTPClient, localPath, remotePath):
        ''' sftp断点续传 https://www.jianshu.com/p/19319228ece0 '''
        if remotePath[-1:] in ('/', '\\'):
            remotePath = os.path.join(remotePath, os.path.basename(localPath))
        elif remotePath[-1:] == os.curdir:
            remotePath = os.path.join(os.path.dirname(remotePath), os.path.basename(localPath))  # yapf: disable
        remotePath = remotePath.replace('\\', '/')
        rDirName = os.path.dirname(remotePath)
        if rDirName:
            sftptool.makedirs_remote(sftpCli, rDirName, exist_ok=True)
        os.stat(localPath)  # 检查本地文件是否存在.
        sftpCli.put(localPath, remotePath)
        return remotePath

    @staticmethod
    def makedirs_remote(sftpCli: paramiko.SFTPClient, name, mode=0o777, exist_ok=False):  # yapf: disable
        ''' 以 os.makedirs 为蓝本进行了修改 '''
        def isf_isd_remote(sftpClientObject, path: str):
            # 判断一个远程路径的是文件还是目录
            try:
                obj_SFTPAttributes = sftpClientObject.stat(path)
                isF = obj_SFTPAttributes.st_mode & stat.S_IFREG == stat.S_IFREG
                isD = obj_SFTPAttributes.st_mode & stat.S_IFDIR == stat.S_IFDIR
                if isF and isD:
                    raise RuntimeError('this path is both a file and a directory')  # yapf: disable
                return isF, isD
            except FileNotFoundError:
                return False, False

        def exists_remote(sftpClientObject, path):
            # 若,一个远程路径,不是文件,不是目录,暂时认为该路径不存在.
            isF, isD = isf_isd_remote(sftpClientObject, path)
            return isF or isD

        head, tail = os.path.split(name)
        if not tail:
            head, tail = os.path.split(head)
        if head and tail and not exists_remote(sftpCli, head):
            try:
                sftptool.makedirs_remote(sftpCli, head, mode, exist_ok)
            except FileExistsError:
                # Defeats race condition when another thread created the path
                pass
            cdir = os.curdir
            if isinstance(tail, bytes):
                cdir = bytes(os.curdir, 'ASCII')
            if tail == cdir:  # xxx/newdir/. exists if xxx/newdir exists
                return
        try:
            sftpCli.mkdir(name, mode)
        except OSError:
            # Cannot rely on checking for EEXIST, since the operating system
            # could give priority to other errors like EACCES or EROFS
            if not exist_ok or not isf_isd_remote(sftpCli, name)[1]:
                raise

    @staticmethod
    def listdir(sftpCli: paramiko.SFTPClient, path="."):
        return sftpCli.listdir(path)

    @staticmethod
    def exists(sftpCli: paramiko.SFTPClient, path: str):
        ''' 类似 os.path.exists 函数 '''
        try:
            sftpCli.stat(path)
            return True
        except FileNotFoundError:
            return False


if __name__ == "__main__":
    print('NotImplementedError')
