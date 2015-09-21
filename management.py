#! /usr/bin/env python
import re, os,time, getpass, logging, readline, shutil
LOG_FILENAME = './kvm_log/completer.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG,)
class Virsh(object) :
    message='./kvm_log/virtViewerMessage.log'
    error='./kvm_log/virtViewerError.log'
    model_set=set(['start', 'reboot', 'shutdown', 'suspend', 'resume', 'destroy', 'undefine'])
    def __init__(self, user) :
        self.user=user
        self.table=dict()
        self.dirty=True

    def __update(self) :
        self.table.clear()
        result=os.popen('virsh list --all').read()
        if self.user :
            pat='([0-9]+|-)[ ]+('+self.user+'_[A-z0-9]+)[ ]+(running|shut off)[ ]*'
        else :
            pat='([0-9]+|-)[ ]+([A-z0-9]+)[ ]+(running|shut off)[ ]*'
        for a in re.findall(pat, result) :
            if self.user :
                self.table.update({a[1][len(self.user)+1:] : [a[2], 'N', 'N']})
            else :
                self.table.update({a[1] : [a[2], 'N', 'N']})

    def __upMac(self) :
        ip_mac=re.findall('(192\.168\.122\.\d+).+(..:..:..:..:..:..)', os.popen('arp -n').read())
        macipdict=dict()
        for item in ip_mac :
            macipdict.update({item[1] : item[0]})
        for item in self.table.items() :
            mac=re.search('..:..:..:..:..:..', os.popen('virsh domiflist '+self.user+'_'+item[0]).read()).group()
            if item[1][0]=='running' :
                ip=macipdict.get(mac)
                if not ip :
                    ip='N'
                self.table.update({item[0] : ['running', mac, ip]})
            else :
                self.table.update({item[0] : ['shut off', 'N', 'N']})

    def isExist(self, name) :
        if self.dirty==True :
            self.__update()
        if name in self.table.keys() :
            return True
        return False

    def virsh(self, model, name) :
        if model in Virsh.model_set :
            if self.isExist(name) :
                if model=='undefine' and self.table.get(name)[0]=='running' :
                    self.virsh('destroy', name)
                result=os.popen('virsh '+model+' '+self.user+'_'+name).read()
                print result
                if model=='undefine' :
                    self.__delete(name)
                elif model=='destroy' :
                    self.table.update( {name : ['shut off', 'N', 'N']} )
                else :
                    self.dirty=True
            else :
                print '\tPlease check VM name.'
        else :
            raise Exception('Not exist model(virsh)')

    def __delete(self, name) :
        result=os.popen('ls -l '+VmTool.qcow2_path).read()
        pat='.*'+self.user+'_'+name+'.*'
        match=re.search(pat, result)
        if match :
            path=VmTool.qcow2_path+self.user+'_'+name
            if match.group()[0]=='d' :
                shutil.rmtree(path)
            else :
                os.remove(path+'.qcow2')
            #os.system(inst)

    def getNameSet(self) :
        if self.dirty==True :
            self.__update()
        return self.table.keys()

    def getList(self) :
        if self.dirty==True :
            self.__update()
            self.__upMac()
        li=list()
        for key in sorted(self.table.keys()) :
            data=self.table.get(key)
            li.append([key, data[0], data[1], data[2]])
        return li

    def getRSList(self, model='all') :
        if self.dirty==True :
            self.__update()
        li=list()
        for item in self.table.items() :
            if model=='all' :
                li.append(item[0])
            elif item[1][0]==model :
                li.append(item[0])
        return sorted(li)

    def virtViewer(self, name) :
        if self.isExist(name)==True :
            if self.table.get(name)[0]!='running' :
                self.virsh('start', name)
            os.system('virt-viewer '+self.user+'_'+name+' > '+Virsh.message+' 2> '+Virsh.error+' &')
        else :
            print '\tPlease check your VM Name.'

class BufferCompleter(object) :
    def __init__(self, single_options, vm_options, virsh) :
        self.sop=single_options
        self.vop=vm_options
        self.virsh=virsh

    def complete(self, text, state) :
        response=None
        #print 'text:', text, 'state:', state
        if state==0 :
            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            logging.debug('origline=%s', repr(origline))
            logging.debug('begin=%s', begin)
            logging.debug('end=%s', end)
            logging.debug('being_completed=%s', being_completed)
            logging.debug('words=%s', words)

            '''
            print 'origline', origline
            print 'begin', begin
            print 'end', end
            print 'being_completed', being_completed
            print 'words', words
            '''
            if not words :
                self.current_candidates=sorted(list(sop).extend(vop))
                print self.current_candidates
            else :
                try :
                    if begin==0 :
                        candidates=list(self.sop)
                        candidates.extend(self.vop)
                    elif words[0] in self.vop :
                        #print 'search virsh list --all'
                        if words[0] in ['view'] :
                            candidates=self.virsh.getRSList()
                        if words[0] in ['open', 'delete'] :
                            candidates=self.virsh.getRSList('shut off')
                        else :
                            candidates=self.virsh.getRSList('running')
                        # search vm list
                    elif not words[0] in self.sop :
                        print '\tPlease check your command.'
                    if being_completed :
                        self.current_candidates=[w for w in candidates
                                    if w.startswith(being_completed)]
                        #print self.current_candidates
                    else :
                        self.current_candidates=candidates
                    logging.debug('candidates=%s', self.current_candidates)
                except (KeyError, IndexError), err :
                    #print 'error', err
                    logging.error('completion error: %s', err)
                    self.current_candidates=[]
        try :
            response=self.current_candidates[state]
        except :
            reasponse=None
            logging.debug('complete(%s, %s) => %s', repr(text), state, response)
        return response

class Stand(object) :
    def standardPrint(self, l) :
        head_interval='\t'
        number_interval=3
        item_interval='\t'
        size=len(l)
        s_max=len(str(size+1))+number_interval
        l_max=0
        if not l :
            print '\tNothing'
        elif isinstance(l, set) :
            for a in l :
                print a+self.__printRepeat(' ', 3),
            print ''

        elif isinstance(l[0], list) :
            for a in l :
                l_max=max(l_max, len(a[0]))
            t_max=int((s_max+l_max)/8)+1
            for i in range(size) :
                if isinstance(l[i], list) :
                    print head_interval+str(i+1)+self.__printRepeat(' ', s_max-len(str(i+1)))+l[i][0]+self.__printRepeat('\t', t_max-int((len(l[i][0])+s_max)/8)),
                    if l[i][3]=='N' :
                        print l[i][1]
                    else :
                        print l[i][1]+'   '+l[i][2]+'   '+l[i][3]
                else :
                    print head_interval+str(i+1)+self.__printRepeat(' ', s_max-len(str(i+1)))+l[i]
            print ''
        else :
            n=2
            for a in l :
                l_max=max(l_max, len(a))
            t_max=int((s_max+l_max)/8)+1
            for i in range(size) :
                if i%n==0 :
                    print head_interval+str(i+1)+self.__printRepeat(' ', s_max-len(str(i+1)))+l[i]+self.__printRepeat('\t', t_max-int((len(l[i])+s_max)/8)),
                elif i%n==n-1 :
                    print str(i+1)+self.__printRepeat(' ', s_max-len(str(i+1)))+l[i]
                else :
                    print str(i+1)+self.__printRepeat(' ', s_max+-len(str(i+1)))+l[i]+self.__printRepeat('\t', t_max-int((len(l[i])+s_max)/8)),
            print ''

    def __printRepeat(self, a, n) :
        out=''
        for i in range(n) :
            out+=a
        return out

class VmTool(Stand) :
    releaseList=[['Ubuntu 12.04 LTS (Precise Pangolin)', 'ubuntuprecise', 'precise'], ['Ubuntu 14.04 LTS (Trusty Tahr)', 'ubuntutrusty', None], ['Microsoft Windows 7', 'win7', None]]
    ios_path='/var/lib/libvirt/images/iso/'
    qcow2_path='/var/lib/libvirt/images/'
    max_cpu=4
    min_cpu=1
    max_memory=2048
    min_memory=512
    max_disk=200
    min_disk=10
    def __init__(self, virsh) :
        self.vir=virsh
        self.name='default'
        self.os=self.getOsList()[0]
        self.release=0
        self.cpu=1
        self.memory=1024
        self.disk_size=10
        self.network='network=default'

    def setName(self) :
        name_set=self.vir.getNameSet()
        while True :
            print 'There are name list:'
            self.standardPrint(name_set)
            name=raw_input('Please input a name not existing above: ')
            if re.search('[A-z0-9]+', name) :
                if name not in name_set :
                    self.name=name
                    break
                else :
                    print "Can't input above"
            else :
                print 'Please input a~z or A~Z or 0~9'

    def getOsList(self) :
        os_list=list()
        result=os.popen('ls '+VirtInstall.ios_path).read()
        for a in result.split() :
            os_list.append(a)
        return os_list

    def setOs(self) :
        os_list=self.getOsList()
        size=len(os_list)
        for i in range(size) :
            print str(i+1)+'\t'+os_list[i]
        while True :
            number=int(raw_input("input os's number: "))
            if number>0 and number<=size :
                self.os=os_list[number-1]
                break
            if number==1 :
                print 'Please input 1'
            else :
                print 'Please input 1 ~ '+str(size)

    def setOsRelease(self, cla='VirtInstall') :
        #http://manpages.ubuntu.com/manpages/trusty/man1/virt-install.1.html
        #virt-install --os-variant list
        source=[]
        if cla=='Vmbuilder' :
            for release in self.releaseList :
                if release[2] :
                    source.append(release)
        else :
            source=self.releaseList
        size=len(source)
        for i in range(size) :
            print str(i+1)+'\t'+source[i][0]
        while True :
            number=int(raw_input('Please choose OS Release: '))
            if number>0 and number<=size :
                self.release=number-1
                break
            if size==1 :
                print 'Please input 1.'
            else :
                print 'Please input 1 ~ '+str(size)+'.'

    def setMemory(self) :
        while True :
            memory=int(raw_input('Please input memory size(MB): '))
            if memory>=VirtInstall.min_memory and memory<=VirtInstall.max_memory :
                self.memory=memory
                break
            print 'Please input '+str(VirtInstall.min_memory)+' ~ '+str(VirtInstall.max_memory)+'.'

    def setDisk(self) :
        while True :
            disk=int(raw_input('Please input disk size(GB): '))
            if disk>=VirtInstall.min_disk and disk<=VirtInstall.max_disk :
                self.disk_size=disk
                break
            print 'Please input '+str(VirtInstall.min_disk)+' ~ '+str(VirtInstall.max_disk)+'.'

    def setNetwork(self) :
        while True :
            print '''
        There are two model:
        1\tNAT:
        \tYou can get the network by DHCP.
        \tBut you can't directly connect the vm.
        \tYou can connect this server and connect your vm(IP:192.168.122.X).
        2\tBridge:
        \tDirectly use the network.
        \tBut you need a static ip(140.115.26/25.X).
            '''
            number=int(raw_input('Please select one network model: '))
            if number==1 :
                self.network='network=default'
                break
            elif number==2 :
                self.network='bridge=br0'
                break
            print 'Please input 1 or 2.'

    def setCpu(self) :
        while True :
            cpu=int(raw_input('Please input cpu number:'))
            if cpu>=VirtInstall.min_cpu and cpu<=VirtInstall.max_cpu :
                self.cpu=cpu
                break
            print 'Please input '+str(VirtInstall.min_cpu)+' ~ '+str(VirtInstall.max_cpu)+'.'

class VirtInstall(VmTool) :
    message='./kvm_log/virtInstallMessage.log'
    error='./kvm_log/virtInstallError.log'
    def __init(self, virsh) :
        super(VirtInstall, self).__init__(virsh)
        self.variantNumber=0

    def __printParameter(self) :
        print 'Current parameter:'
        print '\tName:\t\t', self.name
        print '\tOS:\t\t', self.os[:-4]
        print '\tRelease:\t', VirtInstall.releaseList[self.release][0]
        print '\tCPU:\t\t', self.cpu
        print '\tMemory Size:\t', self.memory
        print '\tDisk Size:\t', self.disk_size
        print '\tNetwork:\t',
        if self.network=='network=default' :
            print 'NAT'
        elif self.network=='bridge=br0' :
            print 'Bridge'

        
    def __getOsType(self) :
        if re.search('ubuntu', self.os) :
            return 'linux'
        return 'windows'

    def __getInstance(self) :
        inst='virt-install --connect qemu:///system '
        if self.name!='default' :
            inst+='--name '+getpass.getuser()+'_'+self.name
        else :
            raise Exception('name is default')
        inst+=' --ram '+str(self.memory)
        inst+=' --vcpus '+str(self.cpu)
        inst+=' --cdrom '+VirtInstall.ios_path+self.os
        inst+=' --disk size='+str(self.disk_size)+',bus=virtio,format=qcow2'
        inst+=',path='+VirtInstall.qcow2_path+getpass.getuser()+'_'+self.name+'.qcow2'
        inst+=' --disk path=/var/lib/libvirt/images/virtio/virtio-win.iso,device=cdrom'
        inst+=' --os-variant='+VirtInstall.releaseList[self.release][1]
        inst+=' --force'
        inst+=' --video qxl --channel spicevmc'
        inst+=' --network '+self.network+',model=virtio'
        inst+=' --graphic vnc'
        inst+=' --hvm'
        inst+=' --accelerate'
        inst+=' --os-type '+self.__getOsType()
        return inst

    def create(self) :
        self.setName()
        while True :
            self.__printParameter()
            option=['OS', 'Release', 'CPU Number' ,'Memory Size', 'Disk Size', 'Network Model', 'Correct', 'Quit']
            self.standardPrint(option)
            number=int(raw_input('Please choose number: '))
            if number==1 :
                self.setOs()
            elif number==2 :
                self.setOsRelease('VirtInstall')
            elif number==3 :
                self.setCpu()
            elif number==4 :
                self.setMemory()
            elif number==5 :
                self.setDisk()
            elif number==6 :
                self.setNetwork()
            elif number==7 :
                inst=self.__getInstance()+' > '+VirtInstall.message+' 2> '+VirtInstall.error+' &'
                os.system(inst)
                print inst
                break
            elif number==8 :
                break
            else :
                print 'Please input 1 ~ 7.'

class Vmbuilder(VmTool) :
    suite_set=set(['breezy', 'dapper', 'edgy', 'etch', 'feisty', 'gutsy', 'hardy', 'hoary', 'intrepid', 'jaunty', 'jessie', 'karmic', 'lenny', 'lucid', 'maverick', 'natty', 'oneiric', 'potato', 'precise', 'quantal', 'raring', 'sarge', 'sid', 'squeeze', 'warty', 'wheezy', 'woody'])
    suite_dict={'ubuntu-12.04.5-alternate-amd64.iso':'precise', 'ubuntu-12.04.5-server-amd64.iso':'precise'}
    message='./kvm_log/vmbuilderMessage.log'
    error='./kvm_log/vmbuilderError.log'
    def __init__(self, virsh, user) :
        super(Vmbuilder, self).__init__(virsh)
        self.user=user
        self.name='ubuntu'
        self.password='ubuntu'
        self.ip=''
        self.pkg=['openssh-server']

    def __printParameter(self) :
        print 'Current parameter:'
        print '\tName:\t\t', self.name
        print '\tUser Name:\t', self.user
        print '\tPassword:\t', self.password
        #print '\tOS:\t\t', self.os[:-4]
        print '\tRelease:\t', Vmbuilder.releaseList[self.release][0]
        print '\tCPU:\t\t', self.cpu
        print '\tMemory Size:\t', self.memory
        print '\tDisk Size:\t', self.disk_size
        print '\tNetwork:\t',
        if self.network=='network=default' :
            print 'NAT'
        elif self.network=='bridge=br0' :
            print 'Bridge'
            print '\tIP:\t\t', self.ip
        print '\tPackage:\t',
        for p in self.pkg :
            print p+', ',
        print ''

    def __setIp(self) :
        while True :
            ip=raw_input('Please input IP: ')
            if re.search(r'^140\.115\.2(5|6)\.([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-3])$', ip) :
                self.ip=ip
                break
            print 'Please check your IP.'

    def __getSuite(self) :
        suite=Vmbuilder.suite_dict.get(self.os)
        if suite :
            return suite
        else :
            print 'There is not supported script.'
        
    def __getInstance(self) :
        inst='vmbuilder kvm ubuntu '
        if self.name!='default' :
            inst+='--name '+self.user+'_'+self.name+' --overwrite'
        else :
            raise Exception('name is default')
        inst+=' -d '+VirtInstall.qcow2_path+self.user+'_'+self.name
        inst+=' --cpus '+str(self.cpu)
        inst+=' --mem '+str(self.memory)
        inst+=' --user '+self.user
        inst+=' --hostname '+self.name
        inst+=' --pass '+self.password
        #inst+=' --suite '+self.__getSuite()
        #inst+=' --iso '+VirtInstall.ios_path+self.os
        inst+=' --rootsize '+str(self.disk_size*1024)
        #inst+=' --os-variant='
        inst+=' --suite '+Vmbuilder.releaseList[self.release][2]
        #inst+=' --lang en_US.UTF-8'
        inst+=' --timezone Asia/Taipei'
        inst+=' --libvirt qemu:///system'
        for pkg in self.pkg :
            inst+=' --addpkg '+pkg
        if self.network=='network=default' :
            inst+=' --network default'
        elif self.network=='bridge=br0' :
            inst+=' --bridge br0'
            inst+=' --ip '+self.ip
            inst+=' --mask 255.255.255.0'
            inst+=' --net '+self.ip[:11]+'0'
            inst+=' --bcast '+self.ip[:11]+'255'
            inst+=' --gw '+self.ip[:11]+'254'
            if self.ip.split('.')[2]=='25' :
                inst+=' --dns 140.115.25.11'
            else :
                inst+=' --dns 140.115.26.5'
        return inst

    def setUser(self) :
        self.user=raw_input('User Name: ')

    def setPass(self) :
        self.password=getpass.getpass()

    def create(self) :
        self.setName()
        while True :
            self.__printParameter()
            option=['User Name', 'Password', 'Release', 'CPU Number' ,'Memory Size', 'Disk Size', 'Network Model', 'Correct', 'Quit']
            self.standardPrint(option)
            number=int(raw_input('Please choose number: '))
            if number==1 :
                self.setUser()
            elif number==2 :
                self.setPass()
            elif number==3 :
                self.setOsRelease('Vmbuilder')
                suite=self.__getSuite()
                if not suite :
                    self.os=self.getOsList[0]
            elif number==4 :
                self.setCpu()
            elif number==5 :
                self.setMemory()
            elif number==6 :
                self.setDisk()
            elif number==7 :
                self.setNetwork()
                if self.network=='bridge=br0' :
                    self.__setIp()
            elif number==8 :
                inst=self.__getInstance()+' > '+Vmbuilder.message+' 2> '+Vmbuilder.error+' &'
                os.popen(inst)
                break
            elif number==9 :
                break
            else :
                print 'Please input 1 ~ 9.'

class Management(Stand) :

    def __help(self) :
        print '\t<Command>'
        print '\tcreateManual : create a VM manually'
        print '\tcreateAuto   : create a VM automatically'
        print '\thelp : show help data'
        print '\tlist : list all VM'
        print '\tquit : quit this interface'
        print ''
        print '\t<Command> <VM Name>'
        print '\tview     : view the VM'
        print '\topen     : open the VM'
        print '\treboot   : reboot the VM'
        print '\tshutdown : shut dowm the VM'
        print '\tturnoff  : turn off the power of the VM'
        print '\tdelete   : delete the VM'

    def choose(self) :
        print '\tinput help to see more command'
        if os.geteuid()==0 :
            user=raw_input('Please input your account: ')
        else :
            user=getpass.getuser()
        vir=Virsh(user)
        readline.set_completer(BufferCompleter(['help', 'list', 'quit', 'createAuto', 'createManual'], ['view', 'open', 'reboot', 'shutdown', 'turnoff', 'delete'], vir).complete)
        readline.parse_and_bind('tab: complete')
        while True :
            inp=raw_input(' >>> ')
            com=inp.split()
            if com :
                if com[0]=='quit' :
                    break
                elif com[0]=='help' :
                    self.__help()
                elif com[0]=='list' :
                    name_list=vir.getList()
                    self.standardPrint(name_list)
                elif com[0]=='createManual' :
                    v=VirtInstall(vir)
                    v.create()
                elif com[0]=='createAuto' :
                    if os.geteuid()==0 :
                        v=Vmbuilder(vir, user)
                        v.create()
                    else :
                        print '\tPlease run as root'
                elif len(com)==2 :
                    if com[0]=='view' :
                        vir.virtViewer(com[1])
                    elif com[0]=='open' :
                        vir.virsh('start', com[1])
                    elif com[0]=='reboot' :
                        vir.virsh('reboot', com[1])
                    elif com[0]=='shutdown' :
                        vir.virsh('shutdown', com[1])
                    elif com[0]=='turnoff' :
                        vir.virsh('destroy', com[1])
                    elif com[0]=='delete' :
                        vir.virsh('undefine', com[1])
                else :
                    print '\t <Command> < VM Name>'



if __name__=='__main__' :
    m=Management()
    m.choose()

# breezy     Ubuntu 5.10 (Breezy Badger)
# dapper     Ubuntu 6.06.2 LTS (Dapper Drake)
# edgy       Ubuntu 6.10 (Edgy Eft)
# etch       debian etch
# feisty     Ubuntu 7.04 (Feisty Fawn)
# gutsy      Ubuntu 7.10 (Gutsy Gibbon)
# hardy      Ubuntu 8.04.4 LTS (Hardy Heron)
# hoary      Ubuntu 5.04 (Hoary Hedgehog)
# intrepid   Ubuntu 8.10 (Intrepid Ibex)
# jaunty     Ubuntu 9.04 (Jaunty Jackalope)
# jessie     debian jessie
# karmic     Ubuntu 9.10 (Karmic Koala)
# lenny      Debian lenny
# lucid      Ubuntu 10.04.4 LTS (Lucid Lynx)
# maverick   Ubuntu 10.10 (Maverick Meerkat)
# natty      Ubuntu 11.04 (Natty Narwhal)
# oneiric    Download Ubuntu 11.10 (Oneiric Ocelot)
# potato     Debian GNU/Linux 2.2 ('potato')
# precise    Ubuntu 12.04.5 LTS (Precise Pangolin)
# quantal    Ubuntu 12.10 (Quantal Quetzal)
# raring     Ubuntu 13.04 (Raring Ringtail)
# sarge      Debian -- Debian "sarge"
# sid        Debian sid
# squeeze    Debian 6.0 (*Squeeze*)
# warty      Ubuntu 4.10 (Warty Warthog)
# wheezy     Debian -- Debian "wheezy"
# woody      Debian GNU/Linux 3.0 "woody"
# https://packages.debian.org/wheezy/all/debootstrap/filelist
