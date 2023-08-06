# -*- coding: UTF-8 -*-
import traceback
import jdmssql
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from email.mime.multipart import MIMEMultipart
import time
import os
from example_demo.commons.common_fun import get_next_check_time
from example_demo.monitor.monitor_decorator import logit
from example_demo.monitor.pipeline_redis_remote import RemoteCmd, RedisClient
import example_demo.setting as setting

class email_logit(logit):

    def __init__(self, mail_host, email_list, sub, content, _from='msci@jindefund.com', *args, **kwargs):
        self.mail_host = mail_host
        super(email_logit, self).__init__(*args, **kwargs)
        self.email_list = email_list
        self.sub = sub
        self.content = content
        self._from = _from

    def notify(self):
        from_addr = "zhangyf@jindefund.com"  # 这里的hello可以任意设置，收到信后，将按照设置显示
        msg = MIMEText(self.content, _subtype='html', _charset='gb2312')  # 创建一个实例，这里设置为html格式邮件
        msg['Subject'] = self.sub  # 设置主题
        msg['From'] = self._from
        msg['To'] = ";".join(self.email_list)
        try:
            s = smtplib.SMTP()
            s.connect(self.mail_host)  # 连接smtp服务器
            s.sendmail(from_addr, self.email_list, msg.as_string())  # 发送邮件
            s.close()
            print('邮件发送成功')
        except smtplib.SMTPException as e:
            print('邮件发送失败')


def send_mail(sub, content, mail_host=None, email_to_list=None, email_from=None, payload_file=None, debug=False):
    """
        发送邮件
        :param:str sub: 主题
        :param:str content: 邮件内容
        :param:str mail_host:
        :param:list email_list: 收件人列表
        :param:str email_from: 发件人
        :param:str payload_file: 附件

        :param:bool debug:
    """
    # 加载配置
    sub = sub or setting.EMAIL_SUBJECT
    content = content or setting.EMAIL_CONTENT
    email_to_list = email_to_list or setting.EMAIL_TO_LIST
    mail_host = mail_host or setting.EMAIL_HOST
    email_from = email_from or setting.EMAIL_FROM
    debug = debug or setting.DEBUG_ENABLE
    email = MIMEMultipart()
    email['Subject'] = sub  # 设置主题
    email['From'] = email_from
    email['To'] = ";".join(email_to_list)
    msg = MIMEText(content, _subtype='html', _charset='gb2312')
    email.attach(msg)
    if payload_file:
        att1 = MIMEBase('application', 'octet-stream')
        att1.set_payload(open(payload_file, 'rb').read())
        payload_file_name = ''
        att1.add_header("Content-Disposition", "attachment", filename=Header(payload_file_name, "utf-8").encode())
        encoders.encode_base64(att1)
        email.attach(att1)
    if debug:
        print('send_email_host:%s, from:%s,to:%s'%(mail_host, email_from, ";".join(email_to_list)))
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)  # 连接smtp服务器
        s.sendmail(email_from, email_to_list, email.as_string())  # 发送邮件
        s.close()
        return True
    except Exception as e:
        if debug:
            traceback.print_exc()
            print("send email error : " + str(e))
        return False


def call_telephone(data_type, date_str, contacts=[], optname='', sub_data_type='A股市场', remind_info='download error', TemplateNO="2",
                   Status="0", CallResult="0", CallTimes="0", Memo="测试",
                   debug=False):
    """
        电话报警 表 VoiceCall

        :param:str data_type: 系统 （大类型）
        :param:str date_str:
        :param:list contacts: 接收人 必填
        :param:str optname: 发起人  必填
        :param:str sub_data_type: 模板参数模块
        :param:str remind_info: 模板参数 提示信息
        :param:str TemplateNO: 内部模板号  目前固定为 2
        :param:str Status: 状态（0-待处理，1-已处理 ）
        :param:str CallResult: 处理结果
        :param:str CallTimes: 重试次数，最多重试5次，间隔2分钟
        :param:str Memo: 备注
        :param:bool debug:
        **表 VoiceCall
        [SerialNum]              int IDENTITY(1, 1) not null,       --自增索引值
        [TemplateNO]            int not null,                      --内部模板号
        [TemplateParas]          varchar(2048) not null,            --模板参数列表，以'|'分隔
        [Contact]               varchar(16) not null,             --联系人，填写域名
        [Status]                 int not null,                      --状态，0-待处理，1-已处理
        [CallResult]                int not null,                      --处理结果
        [CallTimes]                 int not null,                      --重试次数，最多重试5次，间隔2分钟
        [Memo]                   varchar(2048),                     --备注
        [OptName]                varchar(16) not null,                 --通知发起人
        [OptTime]                 datetime default getdate()            --入库时间
        *[SendTime]               真实发送时间，可用作定时，后续可看需新增


    """
    call_result = False
    # %32x系统%32x模块出发告警，告警信息%32x%32x
    TemplateParas = f"{data_type}|{sub_data_type}|{date_str}|{remind_info}"
    contacts = contacts or setting.TEL_CONTACTS
    OptName = optname or setting.TEL_OPTNAME
    if not contacts or not OptName:
        print('call_telephone no receiver or sender!!')
        return call_result
    con = jdmssql.JDMSSQLHELPER(
        "CA393C4026A3EF1166558C24053F358E900E1F82CB84AA0BE8C94B92654BC5D99371FAC8CA195B77C739944344F06703EDCC4148943A72EFCBB1219DE6F49203")
    for Contact in contacts:

        # Contact = rece
        # print('类初始化时 ', con.isConnected(), con.isAlive())
        sql = """insert into VoiceCall (Date, TemplateNO, TemplateParas, Contact, Status, CallResult, CallTimes, Memo, OptName, OptTime)
               values (convert(char(10), getDate(), 111),'""" + TemplateNO + """','""" + TemplateParas + """','""" + Contact + """',""" + Status + """,
               """ + CallResult + """,""" + CallTimes + """,'""" + Memo + """','""" + OptName + """',getdate())"""
        try:
            con.ExecNonQuery(sql)
            call_result = True
        except:
            pass
    con.close()
    return call_result

def pipe_monitor_file(project_type, check_key, info, file_size=0,  gs=True, pipeline_redis_server_ip="sh-gds-pipeline"
                                                                                                     ".jinde.local",
                      pipeline_redis_server_port=12121, pipeline_domain_name='JINDE\zhangyf',
                      pipeline_proxy_ip='192.168.5.114', debug=False):
    """
        pipeline上报文件状态

        :param:str project_type: 项目类型
        :param:str check_key: 项目名称
        :param:str info: 附加信息
        :param:int(float) file_size:文件大小
        :param:bool gs: gen_state 生成状态
        :param:str pipeline_redis_server_ip: 服务器地址
        :param:int pipeline_redis_server_port: 服务器端口
        :param:str pipeline_domain_name: pipeline 运行用户
        :param:str pipeline_proxy_ip: pipeline 代理

        :param:bool debug:

        next_to_do :返回值的收拢，result & reponse

    """
    if setting.PIPELINE_REDIS_SERVER_IP:
        pipeline_redis_server_ip = setting.PIPELINE_REDIS_SERVER_IP
    if setting.PIPELINE_REDIS_SERVER_PORT:
        pipeline_redis_server_port = setting.PIPELINE_REDIS_SERVER_PORT
    # 关于代理，在win 机器上若已挂代理，是可以直接查找本机ip和用户名；linux机器上目前无法添加代理
    # 满足不同场景下的使用，提供 自设置ip和代理或者使用默认代理
    # host_name = socket.gethostname()
    # ip = socket.gethostbyname(host_name)
    # domain_name = win32api.GetUserNameEx(win32api.NameSamCompatible)
    if setting.PIPELINE_DOMAIN_NAME:
        pipeline_domain_name = setting.PIPELINE_DOMAIN_NAME
    if setting.PIPELINE_PROXY_IP:
        pipeline_proxy_ip = setting.PIPELINE_PROXY_IP
    if not pipeline_domain_name:
        print('no pipeline cfg')
        return
    redis_client = RedisClient(pipeline_redis_server_ip, pipeline_redis_server_port)
    response_cmd_list = redis_client.get_response_cmd_list(pipeline_proxy_ip, pipeline_domain_name, uuid=True)

    server_list = redis_client.get_server_recv_cmd_list()

    cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cur_time_format = cur_time.replace(' ', 'T')
    next_check_time = get_next_check_time()
    # file_size = str(os.path.getsize(file_path))
    report_info = {"project_type": project_type, "project_name": check_key, "state": gs, "file_size": file_size,
                   "update_time": cur_time_format, "info": info, "next_report_time": next_check_time}
    if debug:
        print(report_info)
    # if not os.path.exists(file_path):
    #     print('%s file_path not exists' % file_path)
    #     return
    cmd = RemoteCmd.gen_remote_cmd("user_report_file", report_info, pipeline_proxy_ip, pipeline_domain_name, response_cmd_list)
    result = redis_client.send_sync_request_info(response_cmd_list, server_list, cmd, timeout=2)

    if not result:
        print("connect server error.")
        # report_result["result"] = "report failed."
        return False
    response = RemoteCmd.get_cmd_content(result)
    if debug:
        print(response)
    return True


def upload_singal_status(project_name, gen_state, update_time, singal_info, time_sleep=300, debug=False):
    """
        pipeline上传信号状态

        :param:str project_name: 项目名称
        :param:str gen_state: 生成状态（0，初始化；1，成功；-1 非交易盘；-100 失败）
        :param:str update_time: 更新时间
        :param:str singal_info: 信号信息 （init 初始化；info 成功；error 错误失败）
        :param:int time_sleep:
        :param:bool debug:
        :return: bool :

    """

    update_time_format = update_time.replace(' ', 'T')
    signal_cmd_str = f'D:\pipelinevenv\Scripts\plproxy signalset -n {project_name} -gs {gen_state} -f 0 -t {update_time_format} -i "{singal_info}" '

    if debug:
        print(signal_cmd_str)
        return False
    count = 0
    try:
        while count <= 6:
            status = os.system(signal_cmd_str)
            if status == 0:
                count = 10
            else:
                count += 1
                time.sleep(time_sleep)
    except Exception as e:
        error_signal_cmd_str = f'D:\pipelinevenv\Scripts\plproxy signalset -n {project_name} -gs -100 -f 0 -t {update_time_format} -i "error" '
        os.system(error_signal_cmd_str)
    return True if count == 10 else False
