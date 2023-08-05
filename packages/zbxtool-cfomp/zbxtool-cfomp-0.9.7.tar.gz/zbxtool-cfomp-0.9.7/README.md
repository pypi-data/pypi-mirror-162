# zbxtool

 提供一些修改 zabbix 的操作。

## 使用说明

```shell
# python setup.py install

# zbxtool -h
usage: zbxtool [-h] -s ZBX_SERVER -u ZBX_USER -p ZBX_PASSWD [-t TIMEOUT]
               [-l {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}]
               [command] ...

optional arguments:
  -h, --help            show this help message and exit
  -s ZBX_SERVER, --zbx-server ZBX_SERVER
                        URL of zabbix server
  -u ZBX_USER, --zbx-user ZBX_USER
                        Zabbix server login username
  -p ZBX_PASSWD, --zbx-passwd ZBX_PASSWD
                        Zabbix server login password
  -t TIMEOUT, --timeout TIMEOUT
                        Zabbix API timeout
  -l {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}, --level {CRITICAL,FATAL,ERROR,WARN,INFO,DEBUG}
                        Logging level

subcommands:

  [command]
    discovery
    es_index_zbxhost
    fs_calc
    gen_analaysis_report
    hostgrp_aggr_item
    hosttpl
    inventory_supplementary
    ldap_usergrp
    multi_interfaces
    oob
    service_tree
    sync_wework_media
    update_hostgrp_poc
    update_hostname
    vmware_host_inventory
```

### 子命令说明

- **discovery**: 打印 Zabbix 自动发现的 host, 并输出到 excel.

- **vmware_host_inventory**: 通过 Api 读取 vCenter 信息，更新 Zabbix 中 Hypervisors 组中 Host 的 inventory 信息。

- **update_hostgrp_poc**: 读取 ldap 人员信息, 更新 Zabbix 中各组主机的 inventory。

- **update_hostname**: 消除 Zabbix 中 Discovered Hosts 组中 hostname 末尾的下划线+数字的情况。

- **service_tree**: 在 Zabbix 中 依据主机组生成 it-service 树

- **es_index_zbxhost**: 将 Zabbix 中各主机的 inventory 信息采集至 ElasticSearch 的 Index 中

- **multi_interfaces**: 输出 Zabbix 各主机的 inventory 的 Host networks 字段中的 ip 信息

- **oob**: 更新主机的 inventory OOB IP address 字段

- **ldap_usergrp**: 创建 zabbix 每个主机组的用户组, 并同步到 ldap 的 ou=zabbix 的 user groups 中

- **inventory_supplementary**: vmware 主机更新 inventory type 字段为 vm, 主机有 rsync 进程监控项更新 inventory tag 字段.

- **sync_wework_media**: 从企业微信中获取用户 ID，更新到 zabbix 用户的企业微信告警媒介的 sendto
-
- **hosttpl**: 批量添加、删除、显示 zabbix 主机模板
-
- **fs_calc**: 在各 zabbix 主机上创建总磁盘空间和已用磁盘空间两个监控项。

- **hostgrp_aggr_item**: 在 Zabbix server 主机创建用于统计各主机组资源使用情况的监控项。

- **gen_analaysis_report**: 生成 zabbix 主机组资源使用率报表

### 示例

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password update_hostname

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password vmware_host_inventory

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password vmware_host_inventory -l 10.189.61.62 10.189.61.63 -l 10.189.61.64

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password service_tree delete --service-name test

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password service_tree create --service-name test --group-name Orabbix

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password es_index_zbxhost --es_url 10.189.67.26 [--es_user] [--es_passwd]

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password update_hostgrp_poc -c Contacts.json --ldap-server 10.189.67.14 --ldap-user cn=Manager,dc=shchinafortune,dc=local --ldap-password password

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password discovery --drule 750-开发\* -o result.xlsx

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password multi_interfaces -o result.xlsx

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password oob

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password ldap_usergrp --ldap-server 10.189.67.14 --ldap-user cn=Manager,dc=shchinafortune,dc=local --ldap-password xxxx --create-ldap-group --create-zbx-usrgrp

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password inventory_supplementary

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password sync_wework_media --corpid corpid --secret secret -d '华鑫运管平台-测试' -t /tmp/token-cache -g "Zabbix administrators"

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p real_passwd gen_analaysis_report --start 20220701 --end 20220731
