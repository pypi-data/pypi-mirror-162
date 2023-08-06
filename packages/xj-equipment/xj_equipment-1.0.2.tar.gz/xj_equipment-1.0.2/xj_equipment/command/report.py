# encoding: utf-8
"""
@project: djangoModel->report
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 自动预警脚本
@created_time: 2022/7/4 18:32
"""
import datetime

import pymysql


class Report:
    conn_config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "123456",
        'database': "django",
        'charset': "utf8"
    }

    def __init__(self, config=None):
        if config is None:
            self.conn = pymysql.connect(**self.conn_config)
        else:
            self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()

    def get_log_list(self):
        # 拉取设备运行记录
        end = datetime.datetime.now()  # 当前时间
        start = end - datetime.timedelta(days=1)  # 前一个小时
        select_sql = "select * from equipment_record where created_time>='{}' and created_time <= '{}'".format(start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"))
        self.cursor.execute(select_sql)
        res = self.cursor.fetchall()
        select_result = []
        for item in res:
            temp_header_list = ['id', 'equip_id', 'flag_id', 'unit_id', 'value', 'status', 'summary']
            temp_dict = {}
            for k, v in enumerate(temp_header_list):
                temp_dict[v] = item[k]
            select_result.append(temp_dict)
        return select_result

    def warning_rule(self, record):
        # 预警规则判断
        run_sql = "select warning_toplimit from equipment_equipment where id={}".format(record['equip_id'])
        self.cursor.execute(run_sql)
        warning_top_limit = self.cursor.fetchone()
        if not warning_top_limit is None and warning_top_limit[0]:
            self.up_warning(record)
        else:
            print('设备未设置预警规则，或者运行正常')

    def up_warning(self, warning_record):
        # 自动上报
        select_sql = "select * from equipment_warn where equip_id={} and equip_record_id={} and is_handle=0;".format(
            warning_record['equip_id'],
            warning_record['id'],
        )
        self.cursor.execute(select_sql)
        res = self.cursor.fetchone()
        if res is None:
            insert_sql = "insert into equipment_warn (`equip_id`,`equip_record_id`,`summary`,`work_level`,`is_handle`) values({},{},'{}','normal',0);"
            insert_sql = insert_sql.format(
                warning_record['equip_id'],
                warning_record['id'],
                '自动预警上报'
            )
            self.cursor.execute(insert_sql)
            self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    config = {
        'host': "127.0.0.1",
        'user': "root",
        'password': "123456",
        'database': "django",
        'charset': "utf8"
    }
    app = Report(config)
    select_result = app.get_log_list()
    for i in select_result:
        app.warning_rule(i)
