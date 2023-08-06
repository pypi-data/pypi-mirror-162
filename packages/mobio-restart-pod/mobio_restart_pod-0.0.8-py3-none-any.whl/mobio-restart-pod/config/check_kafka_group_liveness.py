#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
               ..
              ( '`<
               )(
        ( ----'  '.
        (         ;
         (_______,' 
    ~^~^~^~^~^~^~^~^~^~^~
    Author: ThongNV
    Company: M O B I O
    Date Created: 5/25/22
"""
import os
import sys
from datetime import datetime
from os.path import exists

APPLICATION_DATA_DIR = os.environ.get("APPLICATION_DATA_DIR")


def get_topic_kafka(group_id):
    try:
        # Read file group data
        file_group_data = APPLICATION_DATA_DIR + "/kafka-consumer-group-data.json"
        if exists(file_group_data):
            # Kiểm tra thời gian tạo file, nếu out date quá thì k áp dụng để restart
            m_time = os.path.getmtime(file_group_data)
            # dt_m = datetime.fromtimestamp(m_time)
            duration = datetime.now().timestamp() - m_time  # Số giây kể từ thời điểm update file
            # Nếu dữ liệu file data update quá 10 phút thì k kiểm tra nữa
            if duration > 600:
                return 0

            f = open(file_group_data)
            groups_data = f.read()
            if not groups_data:
                return 0
            if groups_data:
                groups_data = eval(groups_data)
        else:
            return 0

        # Read file config
        file_path = "/tmp/kafka-consumer-config.txt"
        if exists(file_path):
            f = open(file_path)
            consumer_config = f.read()
            if consumer_config:
                configs = consumer_config.split(":")
                if configs:
                    pod_name = os.environ.get("HOSTNAME")
                    pod_config = configs[0]
                    if pod_config == pod_name:
                        consumer_id = configs[1]
                        if group_id in groups_data:
                            members_id = groups_data.get(group_id)
                            if isinstance(members_id, list):
                                if consumer_id not in members_id:
                                    return 1

        return 0
    except Exception:

        return 0


if __name__ == '__main__':
    group_id = sys.argv[1] if len(sys.argv) > 1 else None
    check_status = get_topic_kafka(group_id)
    if check_status == 1:
        print("NotWorker")
    else:
        print("Alive")
