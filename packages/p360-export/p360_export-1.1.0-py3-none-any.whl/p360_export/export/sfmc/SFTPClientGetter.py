from paramiko import SFTPClient, SSHClient, AutoAddPolicy

from p360_export.export.sfmc.SFMCData import SFMCData


class SFTPClientGetter:
    def get(self, sfmc_data: SFMCData) -> SFTPClient:
        host = f"{sfmc_data.tenant_url}.ftp.marketingcloudops.com"
        username = sfmc_data.ftp_username
        password = sfmc_data.ftp_password

        ssh = SSHClient()

        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        return ssh.open_sftp()
