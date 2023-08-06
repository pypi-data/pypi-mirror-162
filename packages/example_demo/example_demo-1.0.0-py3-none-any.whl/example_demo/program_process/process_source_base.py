import os
import time
import copy
import example_demo.setting as setting
import example_demo.commons.common_fun as common


class SourceBase():
    def __init__(self, setting_info=None, **kwargs):

        self.setting_info = setting_info
        # if kwargs:
        #     self.setting_info.update(kwargs)

    def check_outdata(self, url_source):
        # all_has = False

        # vendordb1_connect_url = r'mssql+pymssql://sa:Wind2011@sh-vendordb1\vendordb/SecurityMaster'
        # sql_client = SqlDbClient(vendordb1_connect_url)
        # query_sql = ''
        # df = sql_client.read_sql(query_sql)
        # return all_has ,url_source
        pass

    def file_report_process(self, url_source, process_start=False):
        email_file_report = self.setting_info.get("email_file_report")
        email_content = ''
        project_name = self.setting_info.get("project_name")
        email_subject = f'{project_name} file_report'

        success_num = 0
        error_num = 0
        need_load_sour = []
        all_has = False
        for ind, sour in enumerate(url_source):
            source = copy.deepcopy(self.setting_info)
            source.update(sour)
            file_target_download_fpath = source.get("file_target_download_fpath") or source.get \
                ("source_file_target_download_fpath")
            real_file_target_download_fpath = source.get("file_real_target_download_fpath") or source.get \
                ("source_real_file_target_download_fpath")

            pipeline_check_key = source.get("pipeline_check_key")
            source_load_file_minsize = source.get("file_load_minsize") or source.get("source_load_file_minsize")
            message = ''

            download_in_db = source.get("download_in_db")
            if download_in_db:
                message = f'项目名称：{project_name}:更新数据库成功'
                success_num += 1
                print(message)
                continue

            if common.check_path(file_target_download_fpath, source_load_file_minsize):
                file_size = os.path.getsize(file_target_download_fpath)
                file_last_update_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                      time.localtime(os.stat(file_target_download_fpath).st_mtime))
                message = f'项目名称：{project_name}:{pipeline_check_key} -------------目标文件 check_success：{real_file_target_download_fpath},已存在，file_size：{file_size}, file_last_update_time:{file_last_update_time}'

                print(message)
                success_num += 1
            else:
                need_load_sour.append(source)
                if not process_start:
                    message = f'项目名称：{project_name}:{pipeline_check_key} -------------目标文件 check_error!：{real_file_target_download_fpath},不存在'
                    print(message)

                error_num += 1
            if message:
                email_content += message + '\r\n'
        all_file_num = success_num + error_num

        if process_start and len(need_load_sour) > 0:
            print(f'项目名称：{project_name},待下载目标文件总数：{len(need_load_sour)}')
        elif process_start and len(need_load_sour) == 0:
            print(f'项目名称：{project_name},was over.')

        else:
            print(f'项目名称：{project_name},目标文件总数：{all_file_num},has_success_num:{success_num},error_num:{error_num}')
            conclusion_txt = f'项目名称：{project_name},目标文件总数：{all_file_num},has_success_num:{success_num},error_num:{error_num}'
            email_content = conclusion_txt + '\r\n'
        # if email_content and not process_start and email_file_report:
        #     send_mail(email_subject, email_content)
        if not need_load_sour:
            all_has = True
        return all_has, need_load_sour
