from airflow.providers.ftp.hooks.ftp import FTPHook
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from example_demo.exceptions import OnedatautilConfigException


class FtpDownload(FTPHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour

        connect_id = self.sour.get("conn_id")

        kwargs['ftp_conn_id'] = connect_id

        super().__init__(*args, **kwargs)
        self.total_downloaded = 0
        self.remote_path = sour.get("remote_path")

        self.local_filepath = sour.get("local_filepath")
        try:
            self.total_file_size = self.get_size(self.remote_path)
        except:
            self.total_file_size = 0
        self.output_handle = ''

    def prepare_write(self):
        file_write = open(self.local_filepath, "wb")
        return file_write

    def write_to_file_with_progress(self, data):
        self.total_downloaded += len(data)
        percent_progress = (self.total_downloaded / self.total_file_size) * 100
        self.print_progress(percent_progress)

    def print_progress(self, percent_progress):
        print(f"from {self.remote_path} to {self.local_filepath} :  Percent Downloaded: {percent_progress}%")

    def download(self):
        download_res = False
        try:
            self.output_handle = self.prepare_write()

            self.retrieve_file(self.remote_path, None, callback=self.write_to_file_with_progress)
            download_res = True
        except:
            print(f'ftp_download : {self.remote_path} error')
        return  download_res

class SFTPDownload(SFTPHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour

        connect_id = self.sour.get("conn_id")

        kwargs['ssh_conn_id'] = connect_id

        super().__init__(*args, **kwargs)

    def download(self):
        con = self.get_conn()
        remote_path = self.sour.get("remote_path")
        local_filepath = self.sour.get("local_filepath")
        download_res = False
        if self.path_exists(remote_path):
            try:
                con.get(remote_path, local_filepath)
                download_res = True
            except:
                print(f'path:{remote_path}, sftp download error')
                # raise OnedatautilConfigException(f'path:{remote_path}, download error')
        else:
            print(f'no such path:{remote_path}')
            # raise OnedatautilConfigException(f'no such path:{remote_path}')
        return download_res


class MysqlDownload(MySqlHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour

        connect_id = self.sour.get("conn_id")

        kwargs['conn_name_attr'] = connect_id

        super().__init__(*args, **kwargs)

def source_hooks_downloader(sour):
    request_type = sour.get("request_type")
    download_res = False
    if request_type == 'sftp':
        sftp_hook = SFTPDownload(sour)
        download_res = sftp_hook.download()
    elif request_type == 'ftp':
        ftp_hook = FtpDownload(sour)
        download_res = ftp_hook.download()
    elif request_type == 'mysql':
        mysql_hook = MysqlDownload(sour)
        download_res = mysql_hook.download()


    # sour["download_res"] = download_res
    return download_res