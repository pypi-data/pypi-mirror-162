"""
    配置主机组的联系人信息，更新到主机组内主机的inventory
"""
import json
import argparse
import ldap3
import logging

parser = argparse.ArgumentParser('Access ldap server and update zabbix host inventory poc')
parser.add_argument('-c', '--contacts-file', required=True, help='HostGroup contacts file')
parser.add_argument('-l', '--ldap-server', required=True, help='ldap server ip address')
parser.add_argument('-o', '--ldap-port', default=389, help='ldap server port')
parser.add_argument('-b', '--ldap-user', required=True, help='ldap bind user')
parser.add_argument('-w', '--ldap-password', required=True, help='ldap password')
parser.set_defaults(handler=lambda args: main(args))


def get_hostgrp_users(zapi):
    grp_ldap_users = dict()

    # 查询所有以admins结尾的用户组，
    # 用户组和主机组有约定的对应关系，
    # 如主机组名为 'XYZ',则主机组对应的用户组为 'XYZ admins'
    result = zapi.usergroup.get(
        {
            "selectUsers": ["userid", "name", "surname"],
            "output": ["usrgrpid", "name"],
            "search": {"name": "* admins"},
            'searchWildcardsEnabled': True,
            "status": 0
        }
    )
    for user_group in result:
        # 按约定，从用户组名字直接得到所对应的主机组名字
        grp_name = user_group.get("name").rsplit(" ", 1)[0]
        grp = {"GroupName": grp_name}

        # 由于host inventory中只能保存两个负责人信息（poc_1, poc_2），
        # 取这个用户组中的前两个用户
        grp_ldap_users[grp_name] = grp
        for i in range(min(len(user_group.get("users")), 2)):
            cn = f"{user_group.get('users')[i].get('name')} " \
                 f"{user_group.get('users')[i].get('surname')}"
            grp_ldap_users[grp_name][f"poc_{i + 1}_dn"] = f"cn={cn},ou=Person,dc=shchinafortune,dc=local"
    return grp_ldap_users


class LdapServer:
    """
    使用 ldap3 模块连接ldap server, 通过 dn 查询用户对应的属性
    """

    def __init__(self, host, port, bind_user, password):
        self.__server = ldap3.Server(host=host, port=port)
        self.__conn = ldap3.Connection(self.__server, bind_user, password, auto_bind=True)

    def get_user_info(self, dn):
        if not dn:
            return {}
        res = self.__conn.search(
            search_base=dn,
            search_filter='(objectClass=*)',
            search_scope=ldap3.BASE,
            attributes=ldap3.ALL_ATTRIBUTES  # 该参数无法取消, 取消后不返回任何属性
        )
        if res:
            return self.__conn.response[0].get('attributes')
        return {}


def main(args):
    """
    读取 Contacts.json 文件中 HostGroup 联系人信息, 按 GroupName 升序排列
    遍历 HostGroup 并将 zabbix 中对应的 Host 更新 Poc 信息。
    """

    # 登录ldap server
    ldap = LdapServer(host=args.ldap_server,
                      port=args.ldap_port,
                      bind_user=args.ldap_user,
                      password=args.ldap_password)

    contacts_file = args.contacts_file
    contacts = dict()

    # 读取文件中 HostGroup 联系人信息, 生成contacts, [{group1's info}, {group2's info}, ...]
    with open(contacts_file, 'r', encoding='utf8')as fp:
        temp = json.load(fp)
        for info in temp['HostGroup']:
            contacts[info['GroupName']] = info

    zapi = args.zapi
    hostgrp_users = get_hostgrp_users(zapi)
    hostgrp_users.update(contacts)

    zbx_groups = zapi.hostgroup.get({
        'filter': {
            'name': list(hostgrp_users.keys())
        },
        'output': ['groupid', 'name'],
        'selectHosts': ['hostid']
    })

    # 将zbx_groups 按照 group name 升序排列
    zbx_groups.sort(key=lambda g: g.get('name'))

    for zbx_group in zbx_groups:
        contact = hostgrp_users.get(zbx_group['name'], {})
        inventory = dict()
        for i in [1, 2]:
            dn = f'poc_{i}_dn'
            if dn in contact:
                poc_info = ldap.get_user_info(contact.get(dn))
                inventory[f'poc_{i}_name'] = ''.join(poc_info.get('sn', '') + poc_info.get('givenName', ''))
                inventory[f'poc_{i}_email'] = ','.join(poc_info.get('mail', ''))
                inventory[f'poc_{i}_phone_a'] = poc_info.get('telephoneNumber', [''])[0]
                inventory[f'poc_{i}_phone_b'] = poc_info.get('telephoneNumber', [''])[-1]
                inventory[f'poc_{i}_cell'] = ','.join(poc_info.get('mobile', ''))
                inventory[f'poc_{i}_screen'] = ','.join(poc_info.get('uid', ''))
                # inventory[f'poc_{i}_notes']: ''  # ldap暂无设置此属性
        zapi.host.massupdate({
            'hosts': zbx_group.get('hosts'),
            'inventory_mode': 1,  # 1 - Automatic
            'inventory': inventory
        })
        logging.info(f"update success! HostGroup-> [{zbx_group.get('name')!r}] ")
