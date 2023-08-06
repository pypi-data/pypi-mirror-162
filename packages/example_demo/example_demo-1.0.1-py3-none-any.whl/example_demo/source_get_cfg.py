import example_demo.setting as setting
from example_demo.setting import setting_info
from example_demo.exceptions import OnedatautilConfigException
import re
import os

def format_params(text: str, all_info: dict):
    if not text:
        return text
    key_params = re.findall('\{(.*?)\}', text)
    if key_params:
        for para in key_params:
            if all_info.get(para):
                text = text.replace('{%s}' % para, str(all_info.get(para)))
    return text


def get_sftp_ftp_source_info(setting_info, request_type):
    sftp_source = []
    file_download_all = setting_info.get("file_download_all")
    source_get_connect_id = setting_info.get("source_get_connect_id")
    file_load_dir_from = setting_info.get("file_load_dir_from")
    file_target_download_path = setting_info.get("file_target_download_path")
    file_load_test_path = setting_info.get("file_load_test_path")

    file_load_dir_from = format_params(file_load_dir_from, setting_info)
    file_target_download_path = format_params(file_target_download_path, setting_info)
    file_load_test_path = format_params(file_load_test_path, setting_info)

    if not file_load_dir_from or not file_target_download_path or not file_download_all:
        raise OnedatautilConfigException('file download path  or file_target_download_path or file_load_dir_from no '
                                         'cfg!!')

    debug = setting_info.get("debug_enable")

    for file_index, file in enumerate(file_download_all):
        file_info = {}
        file = format_params(file, setting_info)
        local_filepath = os.path.join(file_target_download_path, file)
        if debug and file_load_test_path:
            local_filepath = os.path.join(file_load_test_path, file)
        file_info["request_type"] = request_type
        file_info["file_download"] = file
        file_info["remote_path"] = os.path.join(file_load_dir_from, file)
        file_info["local_filepath"] = local_filepath
        file_info["conn_id"] = source_get_connect_id
        sftp_source.append(file_info)
    return sftp_source





def get_source_cfg(**kwargs):
    if kwargs:
        setting_info.update(kwargs)
    all_source = []
    request_type = setting.SOURCE_GET_REQUEST_TYPE
    if request_type in ('sftp', 'ftp'):
        all_source = get_sftp_ftp_source_info(setting_info, request_type)



    return all_source
