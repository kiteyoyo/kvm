#!/bin/bash 
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install openssh-server -y
sudo apt-get install fail2ban -y
sudo apt-get install qemu-kvm libvirt-bin ubuntu-vm-builder bridge-utils virtinst virt-viewer spice-vdagent -y
sudo chgrp libvirtd /var/lib/libvirt/images/
sudo chmod 771 /var/lib/libvirt/images/
