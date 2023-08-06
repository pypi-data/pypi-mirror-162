# -*- coding: utf-8 -*-
import getpass
import os
import shutil
from example_demo.commons import common_fun as tools


def deal_file_info(file, replace_querys=[]):
    # file = file.replace("{DATE}", tools.get_current_date())
    # file = file.replace("{USER}", getpass.getuser())
    for query in replace_querys:
        file = file.replace(query[0], query[1])
    return file


class GenerateProject:
    def __init__(self):
        self.download_type = ''
        self.airflow_p = False
        self.project_name = ''
        self.owner = ''

    # 选取对应的唯一cfg
    def check_target_cfg_file(self, src):
        if self.airflow_p:
            if (f'project_airflow_{self.download_type}.cfg' in src and self.download_type) or (
                    not self.download_type and src.endswith('project_airflow.cfg')):
                return True
        else:
            if (f'project_{self.download_type}.cfg' in src and self.download_type) or (
                    not self.download_type and src.endswith('project.cfg')):
                return True
        return False

    def copy_callback(self, src, dst, *, follow_symlinks=True):
        if src.endswith("cfg") and not self.check_target_cfg_file(src):
            return

        if self.airflow_p and src.endswith("main.py"):
            return
        elif not self.airflow_p and (src.endswith("main_dag.py") or src.endswith("env_dag_cfg.py")):
            return

        #   指定DT ,项目cfg 文件 名称依然改为 project.cfg
        if src.endswith("cfg") and not src.endswith("project.cfg"):
            if self.download_type:
                dst = dst.replace(f"_{self.download_type}.cfg", ".cfg")
            if self.airflow_p:
                dst = dst.replace(f"project_airflow", "project")

        if src.endswith(".py") and not src.endswith("main_dag.py"):
            with open(src, "r", encoding="utf-8") as src_file, open(
                    dst, "w", encoding="utf8"
            ) as dst_file:
                content = src_file.read()
                dst_file.write(content)
        elif src.endswith("main_dag.py"):
            with open(src, "r", encoding="utf-8") as src_file, open(
                    dst, "w", encoding="utf8"
            ) as dst_file:
                content = src_file.read()
                content = deal_file_info(content, [('{project_name}', self.project_name), ('{airflow_owner}', self.owner)])

                dst_file.write(content)
        elif src.endswith(".cfg"):
            with open(src, "r", encoding="utf-8") as src_file, open(
                    dst, "w", encoding="utf8"
            ) as dst_file:
                content = src_file.read()
                content = deal_file_info(content, [('{download_type}', self.download_type)])

                dst_file.write(content)

        else:
            shutil.copy2(src, dst, follow_symlinks=follow_symlinks)

    def generate(self, project_name, need_date=False, download_type="", airflow_p=False, airflow_owner=''):
        if need_date:
            now_time_str = tools.get_now_timedate()
            project_name = project_name + '_' + now_time_str
        self.download_type = download_type
        self.airflow_p = True if airflow_p else False
        self.project_name = project_name
        self.owner = airflow_owner
        if os.path.exists(project_name):
            print("%s 项目已经存在" % project_name)
        else:
            template_path = os.path.abspath(
                os.path.join(__file__, "../../../templates/project_template")
            )
            shutil.copytree(
                template_path, project_name, copy_function=self.copy_callback
            )

            print("\n%s 项目生成成功" % project_name)
