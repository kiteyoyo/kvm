#! /bin/bash 
if [ $1 ]; then
	sudo adduser $1
	sudo adduser $1 libvirtd
	cp ~/kvm/
	sudo cp ./management.py /home/$1/management.py
	sudo mkdir /home/$1/kvm_log/
	sudo chown $1 /home/$1/kvm_log
	sudo chgrp $1 /home/$1/kvm_log
	
fi

