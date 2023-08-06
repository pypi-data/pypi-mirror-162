from airflow.providers.http.operators.http import SimpleHttpOperator
import example_demo.setting as setting


def call_alerm_api_operator(dag, TemplateParas, Contacts=[], OptName='', task_id="call_alerm", Memo=''):
    import time
    import json
    data = {}

    contacts = setting.TEL_CONTACTS or Contacts
    optname = setting.TEL_OPTNAME or OptName

    if not contacts or optname:
        print('no tel contact or optname !')
        return None

    # 目前只提供一个通用模板，模板格式如下：
    # ${TXT_32}系统${TXT_32}模块触发告警，告警信息${TXT_32}${TXT_32}
    # 该模板允许有4个参数(也支持只填写前3个参数)，最少3个参数，每个参数不应超过32个字节，即16个汉字
    # 参数填写在TemplateParas中，每个参数以|分割

    # 模板固定ID使用2，请不要修改
    data['TemplateNO'] = "2"
    # 参数，会填充到模板中，可以填写4个参数(也支持只填写前3个参数)，最少3个参数，每个参数间以'|'分割，每个参数不应超过32个字节，即16个汉字
    data['TemplateParas'] = TemplateParas
    # 电话接收人，必须是公司员工的域名，即邮箱'@'符号前面的名字，无法在公司通讯录查到的名字，无法拨打电话
    # data['Contact'] = "zhangyf"
    # 支持定时电话功能，需要给出日期+时间(格式%Y-%m-%d %H:%M:%S)，如果不填时间或者时间小于当前时间，电话会立刻打出
    # data['SendTime'] = time.strftime("%Y-%m-%d", time.localtime()) + " 18:00:00"    #这是定时电话的示例
    data['SendTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 用来记录打电话的备注，便于以后查询，可为空
    data['Memo'] = Memo
    # 用来记录电话发起人，便于以后查询，不可为空
    data['OptName'] = optname
    all_call_task = []
    for contact in contacts:
        data['Contact'] = contact
        call_task = SimpleHttpOperator(
            task_id=(task_id + contact),
            method='POST',
            endpoint='',
            http_conn_id='call_alerm_api',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            # extra_options={"timeout": 3},
            dag=dag,
        )
        all_call_task.append(call_task)
    return all_call_task
