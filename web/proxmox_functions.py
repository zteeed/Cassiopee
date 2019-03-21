from secrets import ip, user, password, verify_ssl
from proxmoxer import ProxmoxAPI


def sort_vms(vms):
    v = map(lambda vm: vm['id'], vms)
    v = map(lambda vm: vm.split("/")[1], v)
    v = map(int, v)
    types = map(lambda vm: vm['type'], vms)
    nodes = map(lambda vm: vm['node'], vms)
    l = sorted(zip(v, nodes, types, vms), key=lambda x: (x[2], x[1], x[0]))
    _, _, _, vms = zip(*l)
    return vms


def proxmox_data():
    proxmox = ProxmoxAPI(ip, user=user, password=password, verify_ssl=verify_ssl)
    vms = proxmox.cluster.resources.get(type='vm')
    vms = sort_vms(vms)
    return vms
