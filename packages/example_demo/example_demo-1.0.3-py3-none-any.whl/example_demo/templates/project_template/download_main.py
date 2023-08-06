# 下载流程  输入数据源，根据数据源信息，选取下载hook

from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.ftp.hooks.ftp import FTPHook
from airflow.providers.http.hooks.http import HttpHook
# from example_demo.request_downloader.airflow_downloader_hooks imprort FtpDownload




def sftp_dwonload_hook(sour):
    connect_id = sour.get("conn_id")
    sftp_hook = SFTPHook(ssh_conn_id=connect_id)
    print(sftp_hook.no_host_key_check)
    remote_path = sour.get("remote_path")
    local_filepath = sour.get("local_filepath")
    print(f'sftp_hook_get_file:{remote_path},to {local_filepath}')
    # con = sftp_hook.get_conn()
    # con.get(remote_path, local_filepath)
    sftp_hook.close_conn()






def ftp_download_hook(sour):
    connect_id = sour.get("conn_id")
    ftp_hook = FTPHook(ftp_conn_id=connect_id)
    remote_path = sour.get("remote_path")
    local_filepath = sour.get("local_filepath")

    ftp_hook.retrieve_file(remote_path, local_filepath)

    # hook = FtpDownload(sour)
    # hook.download()

class DownloadHookProcess:
    def __init__(self, all_resource):
        self.all_resource = all_resource
        # self.download_type = all_resource.get('download_type')


    def process(self):
        for sour in self.all_resource:
            download_type = sour.get("download_type")
            if download_type == 'sftp':
                sftp_dwonload_hook(sour)
            elif download_type == 'ftp':
                ftp_download_hook(sour)
            elif download_type == 'api_get':
                pass
