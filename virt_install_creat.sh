#! /bin/bash

name='shooter'

ubuntu_desk='ubuntu-14.04.2-desktop-amd64.iso'
ubuntu_server='ubuntu-14.04.2-server-amd64.iso'
windows='Win7Ent_64_CHT_wSP1.ISO'
server_iso=$ubuntu_desk

memory_size=2048
vm_disk_size=200

nat='network=default'
bridge='bridge=br0'
network_type=$nat

vnc='vnc'


virt-install --connect qemu:///system \
 --name $name \
 --memory $memory_size \
 --vcpus 2 \
 --file /var/lib/libvirt/images/$name.qcow2 \
 --file-size $vm_disk_size \
 --cdrom /var/lib/libvirt/images/iso/$server_iso \
 --$graphic \
 --network $network_type \
 --os-type linux \
 --hvm \
 --accelerate


#virt-install --os-variant list

#--network birdige=br0



#virt-install \
#--connect qemu:///system \
#--name=虛擬機器的名稱 \
#--ram=分配的記憶體大小 [MB] \
#--os-type=作業系統類型 [ex: linux] \
#--os-variant=作業系統的版本名稱 [ex: ubuntujaunty] \
#--hvm [全虛擬化，hvm 與 paravirt 擇其一，請參考附錄] \
#--paravirt [半虛擬化，hvm 與 paravirt 擇其一，請參考附錄] \
#--accelerate [KVM 加速器] \
#--cdrom=系統安裝光碟的路徑 [ex: *.iso] \
#--file=虛擬硬碟的路徑 [ex: *.qcow2] \
#--file-size=虛擬硬碟的大小 [GB] \
#--bridge=br0 [注意：如果您沒有使用橋接網路，請設定成 --network=default] \
#--vnc \
#--noautoconsole \
#--debug
