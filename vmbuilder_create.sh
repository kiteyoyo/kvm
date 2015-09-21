#!/bin/bash

HOSTNAME=kite_user
user=kite
password=yoyo10121125
MEMORY=512
CPUS=1
DISK_SIZE=10000
IP=140.115.26.59

vmbuilder kvm ubuntu \
-d /var/lib/libvirt/images/$HOSTNAME \
--cpus $CPUS \
--mem $MEMORY \
--user $user \
--hostname $HOSTNAME \
--pass $password \
--suite precise \
--iso /var/lib/libvirt/images/iso/ubuntu-12.04.5-alternate-amd64.iso \
--rootsize 10240 \
--lang en_US.UTF-8 \
--timezone Asia/Taipei \
--domain $HOSTNAME.com \
--libvirt qemu:///system \
--addpkg openssh-server \
--network default

#--bridge br0 \
#--ip $IP \
#--mask 255.255.255.0 \
#--gw 140.115.26.254 \
#--dns 140.115.26.5 \



#domifstat shooter1 vnet0

#sage: vmbuilder hypervisor distro [options]
#
#ptions:
# -h, --help            show this help message and exit
# --version             Show version information
#
# Build options:
#   --debug             Show debug information
#   -v, --verbose       Show progress information
#   -q, --quiet         Silent operation
#   -o, --overwrite     Remove destination directory before starting build
#   -c CONFIG, --config=CONFIG
#                       Configuration file
#   --templates=DIR     Prepend DIR to template search path.
#   -d DESTDIR, --destdir=DESTDIR
#                       Destination directory
#   --only-chroot       Only build the chroot. Don't install it on disk images
#                       or anything.
#   --chroot-dir=CHROOT_DIR
#                       Build the chroot in directory.
#   --existing-chroot=EXISTING_CHROOT
#                       Use existing chroot.
#   -t DIR, --tmp=DIR   Use TMP as temporary working space for image
#                       generation. Defaults to $TMPDIR if it is defined or
#                       /tmp otherwise. [default: /tmp]
#   --tmpfs=SIZE        Use a tmpfs as the working directory, specifying its
#                       size or "-" to use tmpfs default (suid,dev,size=1G).
#
# Disk:
#   --rootsize=SIZE     Size (in MB) of the root filesystem [default: 4096]
#   --optsize=SIZE      Size (in MB) of the /opt filesystem. If not set, no
#                       /opt filesystem will be added.
#   --swapsize=SIZE     Size (in MB) of the swap partition [default: 1024]
#   --raw=PATH          Specify a file (or block device) to use as first disk
#                       image (can be specified multiple times).
#   --part=PATH         Specify a partition table in PATH. Each line of
#                       partfile should specify (root first):      mountpoint
#                       size  one per line, separated by space, where size is
#                       in megabytes. You can have up to 4 virtual disks, a
#                       new disk starts on a line containing only '---'. ie:
#                       root 2000      /boot 512      swap 1000      ---
#                       /var 8000      /var/log 2000
#
# Settings for the initial user:
#   --user=USER         Username of initial user [default: ubuntu]
#   --name=NAME         Full name of initial user [default: Ubuntu]
#   --pass=PASS         Password of initial user [default: ubuntu]
#   --rootpass=ROOTPASS
#                       Initial root password (WARNING: this has strong
#                       security implications).
#   --uid=UID           Initial UID value.
#   --gid=GID           Initial GID value.
#   --lock-user         Lock the initial user [default: none]
#
# Other options:
#   --ssh-key=PATH      Add PATH to root's ~/.ssh/authorized_keys (WARNING:
#                       this has strong security implications).
#   --ssh-user-key=SSH_USER_KEY
#                       Add PATH to the user's ~/.ssh/authorized_keys.
#   --manifest=PATH     If passed, a manifest will be written to PATH
#
# Package options:
#   --addpkg=PKG        Install PKG into the guest (can be specified multiple
#                       times).
#   --removepkg=PKG     Remove PKG from the guest (can be specified multiple
#                       times)
#   --seedfile=SEEDFILE
#                       Seed the debconf database with the contents of this
#                       seed file before installing packages
#
# Network:
#   --domain=DOMAIN     Set DOMAIN as the domain name of the guest [default:
#                       ferreiraent.com].
#
# Installation options:
#   --suite=SUITE       Suite to install. Valid options: dapper gutsy hardy
#                       intrepid jaunty karmic lucid maverick natty oneiric
#                       precise quantal raring saucy trusty [default: lucid]
#   --flavour=FLAVOUR, --kernel-flavour=FLAVOUR
#                       Kernel flavour to use. Default and valid options
#                       depend on architecture and suite
#   --variant=VARIANT   Passed to debootstrap --variant flag; use minbase,
#                       buildd, or fakechroot.
#   --debootstrap-tarball=FILE
#                       Passed to debootstrap --unpack-tarball flag.
#   --iso=PATH          Use an iso image as the source for installation of
#                       file. Full path to the iso must be provided. If
#                       --mirror is also provided, it will be used in the
#                       final sources.list of the vm.  This requires suite and
#                       kernel parameter to match what is available on the
#                       iso, obviously.
#   --mirror=URL        Use Ubuntu mirror at URL instead of the default, which
#                       is http://archive.ubuntu.com/ubuntu for official
#                       arches and http://ports.ubuntu.com/ubuntu-ports
#                       otherwise
#   --proxy=URL         Use proxy at URL for cached packages
#   --install-mirror=URL
#                       Use Ubuntu mirror at URL for the installation only.
#                       Apt's sources.list will still use default or URL set
#                       by --mirror
#   --security-mirror=URL
#                       Use Ubuntu security mirror at URL instead of the
#                       default, which is http://security.ubuntu.com/ubuntu
#                       for official arches and http://ports.ubuntu.com
#                       /ubuntu-ports otherwise.
#   --install-security-mirror=URL
#                       Use the security mirror at URL for installation only.
#                       Apt's sources.list will still use default or URL set
#                       by --security-mirror
#   --components=COMPS  A comma seperated list of distro components to include
#                       (e.g. main,universe).
#   --ppa=PPA           Add ppa belonging to PPA to the vm's sources.list.
#   --lang=LANG         Set the locale to LANG [default: en_US.UTF-8]
#   --timezone=TZ       Set the timezone to TZ in the vm. [default: UTC]
#
# Post install actions:
#   --copy=FILE         Read 'source dest' lines from FILE, copying source
#                       files from host to dest in the guest's file system.
#   --execscript=SCRIPT, --exec=SCRIPT
#                       Run SCRIPT after distro installation finishes. Script
#                       will be called with the guest's chroot as first
#                       argument, so you can use 'chroot $1 <cmd>' to run code
#                       in the virtual machine.
#
# General OS options:
#   -a ARCH, --arch=ARCH
#                       Specify the target architecture.  Valid options: amd64
#                       i386 lpia (defaults to host arch)
#   --hostname=HOSTNAME
#                       Set NAME as the hostname of the guest. Default:
#                       ubuntu. Also uses this name as the VM name.
#
# Scripts:
#   --firstboot=PATH    Specify a script that will be copied into the guest
#                       and executed the first time the machine boots.  This
#                       script must not be interactive.
#   --firstlogin=PATH   Specify a script that will be copied into the guest
#                       and will be executed the first time the user logs in.
#                       This script can be interactive.
#
# libvirt integration:
#   --libvirt=URI       Add VM to given URI
#   --bridge=BRIDGE     Set up bridged network connected to BRIDGE.
#   --network=NETWORK   Set up a network connection to virtual network
#                       NETWORK.
#
# Network:
#   --ip=ADDRESS        IP address in dotted form [default: dhcp].
#   --mac=MAC           MAC address of the guest [default: random].
#   --mask=VALUE        IP mask in dotted form [default: based on ip setting].
#                       Ignored if ip is not specified.
#   --net=ADDRESS       IP net address in dotted form [default: based on ip
#                       setting]. Ignored if ip is not specified.
#   --bcast=VALUE       IP broadcast in dotted form [default: based on ip
#                       setting]. Ignored if ip is not specified.
#   --gw=ADDRESS        Gateway (router) address in dotted form [default:
#                       based on ip setting (first valid address in the
#                       network)]. Ignored if ip is not specified.
#   --dns=ADDRESS       DNS address in dotted form [default: based on ip
#                       setting (first valid address in the network)] Ignored
#                       if ip is not specified.
#
# VM settings:
#   -m MEM, --mem=MEM   Assign MEM megabytes of memory to the guest vm.
#                       [default: 128]
#   --cpus=CPUS         Assign NUM cpus to the guest vm. [default: 1]

# http://ubuntuforums.org/showthread.php?t=2260187
