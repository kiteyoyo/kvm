#! /usr/bin/env python
import re, os,time


class VirtInstall(object) :
    ios_path='/var/lib/libvirt/images/iso/'
    qcow2_path='/var/lib/libvirt/images/'
    out_path='./viewerMessage'
    max_cpu=4
    min_cpu=1
    max_memory=2048
    min_memory=512
    max_disk=200
    min_disk=10
    model_set=set(['start', 'reboot', 'shutdown', 'suspend', 'resume', 'destroy', 'undefine'])
    def __init__(self) :
        export='export LANGUAGE=en_US'
        os.system(export)
        self.name='default'
        self.os=self.__getOsList()[0]
        self.cpu=1
        self.memory=1024
        self.disk_size=10
        self.network='network=default'

    def __printParameter(self) :
        print 'Current parameter:'
        print '\tName:\t\t', self.name
        print '\tOS:\t\t', self.os[:-4]
        print '\tCPU:\t\t', self.cpu
        print '\tMemory Size:\t', self.memory
        print '\tDisk Size:\t', self.disk_size
        print '\tNetwork:\t',
        if self.network=='network=default' :
            print 'NAT'
        elif self.network=='bridge=br0' :
            print 'Bridge'
        
    def __getNameSet(self) :
        result=os.popen('virsh list --all').read()
        name_set=set()
        for a in re.findall('([0-9]+|-)[ ]+([A-z0-9]+)[ ]+(running|shut off)[ ]*', result) :
            name_set.add(a[1])
        return name_set

    def __setName(self) :
        name_set=self.__getNameSet()
        while True :
            print 'There are name list:'
            self.__standardPrint(name_set)
            name=raw_input('Please input a name not existing above: ')
            if re.search('[A-z0-9]+', name) :
                if name not in name_set :
                    self.name=name
                    break
                else :
                    print "Can't input above"
            else :
                print 'Please input a~z or A~Z or 0~9'

    def __getOsList(self) :
        os_list=list()
        result=os.popen('ls '+VirtInstall.ios_path).read()
        for a in result.split() :
            os_list.append(a)
        return os_list

    def __setOs(self) :
        os_list=self.__getOsList()
        size=len(os_list)
        for i in range(size) :
            print str(i+1)+'\t'+os_list[i]
        while True :
            number=int(raw_input("input os's number'"))
            if number>0 and number<=size :
                self.os=os_list[number-1]
                break
            if number==1 :
                print 'Please input 1'
            else :
                print 'Please input 1 ~ '+str(size)

    def __setMemory(self) :
        while True :
            memory=int(raw_input('Please input memory size(MB): '))
            if memory>=VirtInstall.min_memory and memory<=VirtInstall.max_memory :
                self.memory=memory
                break
            print 'Please input '+str(VirtInstall.min_memory)+' ~ '+str(VirtInstall.max_memory)+'.'

    def __setDisk(self) :
        while True :
            disk=int(raw_input('Please input disk size(GB): '))
            if disk>=VirtInstall.min_disk and disk<=VirtInstall.max_disk :
                self.disk_size=disk
                break
            print 'Please input '+str(VirtInstall.min_disk)+' ~ '+str(VirtInstall.max_disk)+'.'

    def __setNetwork(self) :
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
            number=int(raw_input('Please select one network moedl: '))
            if number==1 :
                self.network='network=default'
                break
            elif number==2 :
                self.network='bridge=br0'
                break
            print 'Please input 1 or 2.'
        print self.network

    def __setCpu(self) :
        while True :
            cpu=int(raw_input('Please input cpu number:'))
            if cpu>=VirtInstall.min_cpu and cpu<=VirtInstall.max_cpu :
                self.cpu=cpu
                break
            print 'Please input '+str(VirtInstall.min_cpu)+' ~ '+str(VirtInstall.max_cpu)+'.'

    def __getOsType(self) :
        if re.search('ubuntu', self.os) :
            return 'linux'
        return 'windows'

    def __getInstance(self) :
        inst='virt-install --connect qemu:///system '
        if self.name!='default' :
            inst+='--name '+self.name
        else :
            raise Exception('name is default')
        inst+=' --memory '+str(self.memory)
        inst+=' --vcpus '+str(self.cpu)
        inst+=' --cdrom '+VirtInstall.ios_path+self.os
        inst+=' --disk size='+str(self.disk_size)
        inst+=',path='+VirtInstall.qcow2_path+self.name+'.qcow2'
        #inst+=' --os-variant=ubuntutrusty'##### need structure table
        inst+=' --network '+self.network
        inst+=' --graphic vnc'
        inst+=' --hvm'
        inst+=' --accelerate'
        inst+=' --os-type '+self.__getOsType()
        return inst

    def __vmCreate(self) :
        self.__setName()
        while True :
            self.__printParameter()
            option=['OS', 'Memory Size', 'Disk Size', 'CPU Number', 'Network Model', 'Correct', 'Quit']
            self.__standardPrint(option)
            number=int(raw_input('Please choose number: '))
            if number==1 :
                self.__setOs()
            elif number==2 :
                self.__setMemory()
            elif number==3 :
                self.__setDisk()
            elif number==4 :
                self.__setCpu()
            elif number==5 :
                self.__setNetwork()
            elif number==6 :
                inst=self.__getInstance()+' >> createMessage 2>> '+VirtInstall.out_path+' &'
                os.system(inst)
                break
            elif number==7 :
                break
            else :
                print 'Please input 1 ~ 7.'

    def __getNameList(self) :
        result=os.popen('virsh list --all').read()
        name_dict=dict()
        for a in re.findall('([0-9]+|-)[ ]+([A-z0-9]+)[ ]+(running|shut off)[ ]*', result) :
            name_dict.update({a[1]:a[2]})
        name_list=list()
        for a in name_dict.items() :
            mac=re.search('..:..:..:..:..:..', os.popen('virsh domiflist '+a[0]).read()).group()
            if a[1]=='running' :
                ip_match=re.search('.*'+mac, os.popen('arp -e').read())
                if ip_match :
                    ip=ip_match.group().split()[0]
                else :
                    ip='N'
            else :
                ip='N'
            name_list.append([a[0], a[1], mac, ip])
        return name_list

    def __vmModel(self, model) :
        while True :
            name_list=self.__getNameList()
            size=len(name_list)
            name_list.append('Quit')
            self.__standardPrint(name_list)
            number=int(raw_input('Please input number: '))
            if number>0 and number<=size :
                name=name_list[number-1][0]
                if model=='view':
                    self.__vmVirsh('start', name)
                    os.system('virt-viewer '+name+' 2>> '+VirtInstall.out_path+' &')
                elif model in VirtInstall.model_set :
                    self.__vmVirsh(model, name)
                else :
                    raise Exception('model not exist in model_set')
            elif number==size+1 :
                break
            if size==1 :
                print 'Please input 1.'
            else :
                print 'Please input 1 ~ '+str(size+1)

    def __vmVirsh(self, model, name) :
        if model in VirtInstall.model_set :
            result=os.popen('virsh '+model+' '+name).read()
            print result
            if model=='undefine' :
                inst='rm '+VirtInstall.qcow2_path+name+'.qcow2'
                #print inst
        else :
            raise Exception('Not exist model(virsh)')

    def choose(self) :
        while True :
            option=['View VM', 'Start VM', 'Shutdown VM', 'Reboot VM', 'suspend VM', 'Destroy VM', 'Remove VM', 'Create VM', 'Quit']
            self.__standardPrint(option)
            number=int(raw_input('Please input number: '))
            if number==1 :
                self.__vmModel('view')
            elif number==2 :
                self.__vmModel('start')
            elif number==3 :
                self.__vmModel('shutdown')
            elif number==4 :
                self.__vmModel('reboot')
            elif number==5 :
                self.__vmModel('suspend')
            elif number==6 :
                self.__vmModel('destroy')
            elif number==7 :
                self.__vmModel('undefine')
            elif number==8 :
                self.__vmCreate()
            elif number==9 :
                break
            else :
                print 'Please input 1 ~ 9.'

    def __standardPrint(self, l) :
        head_interval='\t'
        number_interval=3
        item_interval='\t'
        size=len(l)
        s_max=len(str(size+1))+number_interval
        l_max=0
        if isinstance(l, set) :
            for a in l :
                print a+self.__printRepeat(' ', 3),
            print ''

        elif isinstance(l[0], list) :
            for a in l :
                l_max=max(l_max, len(a[0]))
            t_max=int((s_max+l_max)/8)+1
            for i in range(size) :
                if isinstance(l[i], list) :
                    print head_interval+str(i+1)+self.__printRepeat(' ', s_max-len(str(i+1)))+l[i][0]+self.__printRepeat('\t', t_max-int((len(l[i][0])+s_max)/8))+l[i][2]+'\t',
                    if l[i][3]=='N' :
                        print l[i][1]
                    else :
                        print l[i][1]+'   '+l[i][3]
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

    def ttty(self) :
        inst=self.__getInstance()#+' >> createMessage 2>> viewerMessage &'
        print inst
        os.system(inst)



if __name__=='__main__' :
    
    v=VirtInstall()
    v.choose()
