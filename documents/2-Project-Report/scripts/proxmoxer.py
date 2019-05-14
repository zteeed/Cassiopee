from proxmoxer import ProxmoxAPI
proxmox = ProxmoxAPI('proxmox_host', user='proxmox_admin', backend='ssh_paramiko')
for node in proxmox.nodes.get():
    for vm in proxmox.nodes(node['node']).openvz.get():
        print "{0}. {1} => {2}" .format(vm['vmid'], vm['name'], vm['status'])
