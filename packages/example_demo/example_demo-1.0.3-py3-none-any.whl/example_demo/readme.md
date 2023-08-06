#jd_py_base
#目录
+ 目录   
>+ 安装使用及说明
>   + 模块安装
>   + 说明

 
>+ 模块文档
>  + commons
>    + common_fun
>      + get_next_check_time
>  + monitor
>    + monitor_singal_alert
>      + send_mail
>      + call_telephone
>      + pipe_monitor_file
>      + upload_singal_status
>  + request_downloaders
>    + downloaders
>      + sftp_farbic_connect
>      + ftp_connect
>      + get_request_content



#安装使用及说明
##模块安装
> pip install jd_py_base -i http://pypi:8081/ --trusted-host pypi
##说明
>1. 模块为各类通用方法整合，包括三个package（普通通用方法(commons），监控警报(monitor),请求方法（request_downloader））
>2. 版本 0.0.1，初步整合
#模块文档
##commmons
###common_fun
> 通用方法
- get_next_check_time
> 获取下一次交易时间
##monitor
###monitor_singal_alert
> 监控方法
- send_mail
> 邮件
>   
        发送邮件
        :param:str mail_host:
        :param:list email_list: 收件人列表
        :param:str sub: 主题
        :param:str content: 邮件内容
        :param:int _from: 发件人
        :param:bool debug:

- call_telephone
> 电话
>    
        电话报警 表 VoiceCall
        :param:str data_type: 系统 （大类型）
        :param:str date_str:
        :param:str receiver: 接收人
        :param:str sub_data_type: 模板参数模块
        :param:str remind_info: 模板参数 提示信息
        :param:str TemplateNO: 内部模板号
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

- pipe_monitor_file
> 发布状态
>     
        pipeline上报状态
        :param:str file_path:
        :param:str download_date:
        :param:str project_name:
        :param:str content:
        :param:str pipline_path:
        :param:str check_key_head:
        :param:bool debug:

- upload_singal_status
> 上传信号
>     
        pipeline上传信号状态
        :param:str project_name: 项目名称
        :param:str gen_state: 生成状态（0，初始化；1，成功；-1 非交易盘；-100 失败）
        :param:str update_time: 更新时间
        :param:str singal_info: 信号信息 （init 初始化；info 成功；error 错误失败）
        :param:int time_sleep:
        :param:bool debug:
        :return: bool :



##request_downloader
###downloaders
>请求方法
- sftp_farbic_connect
> sftp连接，返回连接对象
>     
        建立sftp连接
        :param:str sftp_host:
        :param:str sftp_user:
        :param:str sftp_password:
        :param:int try_num: 重试次数
        :param:int connect_timeout: 连接请求超时设置
        :param:bool debug:
        :return: sftp_con: sftp_con连接对象
    
- ftp_connect
> ftp连接，返回连接对象
>     
        建立ftp连接
        :param:str ftp_ip:
        :param:str ftp_port:
        :param:str ftp_user_id:
        :param:str ftp_password:
        :param:int try_num: 重试次数
        :param:int timeout: 连接请求超时设置
        :param:bool debug:
        :return: ftp_con: ftp_con连接对象

- get_request_content
> get请求
>     
        get请求
        :param:str url:
        :param:dict headers:
        :param:int timeout: 连接请求超时设置
        :param:int try_num: 重试次数
        :param:str auth_user_name:
        :param:str auth_password:
        :param:bool binary: 是否需要返回二进制
        :param:dict proxies:
        :param:bool debug:
        :return: res_content
