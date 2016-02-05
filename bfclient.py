import socket
import time
import datetime
import threading
import sys
import copy


#routing table
ndict={'cost':[],'address':[],'link':[]}

#for poison reverse
ncheat={'cost':[],'address':[],'link':[]}


dvstore={'cost':[],'destaddr':[],'srcaddr':[],'link':[]}

#to store neighbor's initial cost
neifirst={'cost':[],'address':[],'link':[]}

#to store neighbor's cost when linkdown
originalcost={'cost':[],'address':[],'link':[]}

linkdown=[]

#my neighbor list
mynei={'timer':[],'address':[]}
disvec=[]
INF=1000000

shutdownflag=0
linkupflag=0


localip=socket.gethostbyname(socket.gethostname())
localport=int(sys.argv[1])
timeout=int(sys.argv[2])
myaddr=(localip,localport)

neighbors=sys.argv[3:]


slisten = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
slisten.bind((localip,localport))
s_send = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#add new nodes to routing table
def changeRT(destaddr,cost,link):
    ndict['address'].append(destaddr)
    ndict['cost'].append(cost)
    ndict['link'].append(link)

    #print ndict
    #updateDV(ndict)

#add new neighbors
def add_neighbor(addr,cost,neilink):

    mynei['address'].append(addr)
    mynei['timer'].append(time.ctime())

    neifirst['address'].append(addr)
    neifirst['cost'].append(cost)
    neifirst['link'].append(neilink)
    #neilink=ip+':'+str(port)
    changeRT(addr,cost,neilink)
    #print 'neighbor:',mynei


    tr=threading.Thread(target=recvFunc)
    tr.setDaemon(True)
    tr.start()
    #print disvecstr

#send routing table to neighbors
def sendDV(dict):
    #print mynei
    disvecstr=''

    i=0
    while i<len(dict['address']):
        temp='Destination='+dict['address'][i][0]+':'+str(dict['address'][i][1])+', Cost='+str(dict['cost'][i])+', Link=('+dict['link'][i]+')\n'
        #disvec.append((ndict['address'][i],ndict['cost'][i]))
        disvecstr+=temp
        i+=1
    for i in mynei['address']:

            s_send.sendto(localip+':'+str(localport)+';'+disvecstr,i)

# BF algorithm
def processDV(src,srcaddr,destr,costr,linkr):
    dvstore['srcaddr'].append(srcaddr)
    dvstore['destaddr'].append(destr)
    dvstore['cost'].append(costr)
    dvstore['link'].append(linkr)

    if destr==myaddr:

        if srcaddr in ndict['address']:

            idx=ndict['address'].index(srcaddr)
            mycost=ndict['cost'][idx]
            mylink=ndict['link'][idx]

            #MY LINK TO SRC IN MY TABLE
            mylinkaddr=mylink.split(':')
            mylinkaddr=(mylinkaddr[0],int(mylinkaddr[1]))

            #THE LINK I RECEIVED TO SRC
            linkraddr=linkr.split(':')
            linkraddr=(linkraddr[0],int(linkraddr[1]))


            if linkr==localip+':'+str(localport):

                #HAVE DIRECT WAY
                if costr!=INF:
                    if mycost==INF:
                        #print 'mycostinf'

                        if srcaddr in mynei['address']:
                            for a in neifirst['address']:
                                if a==srcaddr:
                                    firstidx=neifirst['address'].index(a)
                                    ndict['cost'][idx]=neifirst['cost'][firstidx]
                                    ndict['link'][idx]=src
                                    sendDV(ndict)
                        else:
                            ndict['cost'][idx]=INF

                            ndict['link'][idx]=src
                            sendDV(ndict)
                    else:
                        if mycost>costr:

                            ndict['cost'][idx]=costr
                            ndict['link'][idx]=src
                            sendDV(ndict)

                            for a in neifirst['address']:
                                if a==srcaddr:
                                    firstidx=neifirst['address'].index(a)
                                    if mycost>neifirst['cost'][firstidx]:
                                        ndict['cost'][idx]=neifirst['cost'][firstidx]
                                        ndict['link'][idx]=src
                                        sendDV(ndict)

                        else:
                            pass

                else:
                    #pass
                    if srcaddr in mynei['address']:
                        for a in neifirst['address']:
                            if a==srcaddr:
                                firstidx=neifirst['address'].index(a)
                                ndict['cost'][idx]=neifirst['cost'][firstidx]
                                ndict['link'][idx]=src
                                sendDV(ndict)

            else:

                #SRC SAID THERE IS ANOTHER WAY, BYPASS SOME OTHER NODES
                if linkraddr in ndict['address']:
                    lidx=ndict['address'].index(linkraddr)
                    mycosttolinkr=ndict['cost'][lidx]
                    mylinktolinkr=ndict['link'][lidx]
                    if mycosttolinkr==INF:
                        #print 'linkinf'
                        # I CANNOT GET TO SRC AS THE WAY IT TOLD ME
                        # SO I FIND BACK THE DIRECT WAY BETWEEN US
                        #print neifirst
                        for a in neifirst['address']:
                            if a==srcaddr:
                                firstidx=neifirst['address'].index(a)
                                ndict['cost'][idx]=neifirst['cost'][firstidx]
                                ndict['link'][idx]=src
                                sendDV(ndict)





        else:
            add_neighbor(srcaddr,costr,src)
            sendDV(ndict)

    else:

        if destr in ndict['address']:
            didx=ndict['address'].index(destr)
            mycosttodest=ndict['cost'][didx]
            mylinktodest=ndict['link'][didx]
            if srcaddr in ndict['address']:
                sidx=ndict['address'].index(srcaddr)
                mycosttosrc=ndict['cost'][sidx]
                mylinktosrc=ndict['link'][sidx]



                if mylinktodest==src:
                    if destr in mynei['address']:

                    #poison reverse
                        ncheat=copy.deepcopy(ndict)
                        ncheat['cost'][didx]=INF
                        ncheat['link'][didx]=src
                        #sendDV(ncheat)
                        disvecstr=''

                        i=0
                        while i<len(ncheat['address']):
                            temp='Destination='+ncheat['address'][i][0]+':'+str(ncheat['address'][i][1])+', Cost='+str(ncheat['cost'][i])+', Link=('+ncheat['link'][i]+')\n'
                            #disvec.append((ndict['address'][i],ndict['cost'][i]))
                            disvecstr+=temp
                            i+=1


                        s_send.sendto(localip+':'+str(localport)+';'+disvecstr,srcaddr)



                    if costr==INF:
                        if destr in mynei['address']:
                            for a in neifirst['address']:
                                if a==destr:
                                    firstidx=neifirst['address'].index(a)
                                    ndict['cost'][didx]=neifirst['cost'][firstidx]
                                    ndict['link'][didx]=neifirst['link'][firstidx]
                                    sendDV(ndict)
                        else:

                            ndict['cost'][didx]=INF
                            ndict['link'][didx]=src
                            sendDV(ndict)
                    else:

                        #print mycosttosrc,costr,mycosttodest,destr

                        if mycosttosrc+costr<mycosttodest:

                            ndict['cost'][didx]=costr+mycosttosrc
                            #ndict['link'][didx]=src
                            ndict['link'][didx]=mylinktosrc
                            sendDV(ndict)

                else:
                    if mycosttodest<costr:

                        pass
                    else:

                        if mycosttosrc+costr<mycosttodest:
                            if linkr==localip+':'+str(localport):
                                #print 'ppp'
                                pass
                            elif mylinktosrc==destr[0]+':'+str(destr[1]):# and linkr==destr[0]+':'+str(destr[1]):
                                if mycosttodest==INF:
                                    if srcaddr in mynei['address']:
                                        for a in neifirst['address']:
                                            if a==srcaddr:
                                                firstidx=neifirst['address'].index(a)
                                                ndict['cost'][didx]=neifirst['cost'][firstidx]+costr
                                                ndict['link'][didx]=src
                                                sendDV(ndict)

                                #pass

                    #
                            else:
                                if costr+mycosttosrc>INF:
                                    ndict['cost'][didx]=INF
                                    ndict['link'][didx]=src

                                    sendDV(ndict)
                                else:
                                    ndict['cost'][didx]=costr+mycosttosrc
                                    #ndict['link'][didx]=src
                                    ndict['link'][didx]=mylinktosrc
                                    sendDV(ndict)
                        else:
                            pass
            else:
                pass

            

        if destr not in ndict['address']:
            sidx=ndict['address'].index(srcaddr)
            mycosttosrc=ndict['cost'][sidx]
            mylinktosrc=ndict['link'][sidx]
            if mycosttosrc!=INF:
                mycosttodest=mycosttosrc+costr
                #mylinktodest=src
                mylinktodest=mylinktosrc
            else:
                pass
                #mycosttodest=INF
                #mylinktodest=src

            changeRT(destr,mycosttodest,mylinktodest)
            sendDV(ndict)


#the thread to receive routing table
def recvFunc():
    while 1:
    #global iniflag
        rdata=slisten.recvfrom(2048)
        rdata=rdata[0]
        temp=rdata.split(';')
        src=temp[0]
        #print 'src',src

        srcaddr=src.split(':')
        srcaddr=(srcaddr[0],int(srcaddr[1]))

        if srcaddr in mynei['address']:
            nidx=mynei['address'].index(srcaddr)
            mynei['timer'][nidx]=time.ctime()

        data=''.join(temp[1:])
        #print data
        if data=='LINKDOWN':
            #print 'linkdown'
            downidx=ndict['address'].index(srcaddr)
            originalcost['address'].append(srcaddr)
            ocost=ndict['cost'][downidx]
            originalcost['cost'].append(ocost)
            olink=ndict['link'][downidx]
            originalcost['link'].append(olink)

            ndict['cost'][downidx]=INF
            sendDV(ndict)
            #print mynei
            if srcaddr in mynei['address']:
                neiidx=mynei['address'].index(srcaddr)
                del mynei['address'][neiidx]
                del mynei['timer'][neiidx]

            linknum=0
            while linknum<len(ndict['link']):

                #print linknum
                if ndict['link'][linknum]==src:
                    print 'down ',src
                    ndict['cost'][linknum]=INF
                    show_RT()
                    sendDV(ndict)
                    #print disvecstr
                    #print '\n'
                linknum+=1




            #sendDV()

        if data=='LINKUP':
            #print 'up'
            oidx=originalcost['address'].index(srcaddr)
            ocost=originalcost['cost'][oidx]
            olink=originalcost['link'][oidx]
            upidx=ndict['address'].index(srcaddr)
            ndict['cost'][upidx]=ocost
            ndict['link'][upidx]=olink
            sendDV(ndict)

            mynei['address'].append(srcaddr)
            mynei['timer'].append(time.ctime())
            del originalcost['address'][oidx]
            del originalcost['cost'][oidx]
            del originalcost['link'][oidx]



        else:
            #splite received table into address,cost and link(next hop)
            databyline=data.split('\n')
            databyline=databyline[:len(databyline)-1]
            for i in databyline:
            #i=''.join(i)
                dv=i.split(',')
                destr=dv[0]
                destr=destr[12:]
                destr=destr.split(':')
                destr=(destr[0],int(destr[1]))
            #print destr

                costr=dv[1]
                costr=costr[6:]
                if costr!=INF:
                    costr=int(costr)
            #print costr

                linkr=dv[2]
                linkr=linkr[7:-1]
            #print linkr


                processDV(src,srcaddr,destr,costr,linkr)


        if shutdownflag==1:
            break
        #print databyline


        # else:
        #     mynei['address'].append(srcaddr)
        #     mynei['timer'].append(time.ctime())

        #print data
        #print '\n'

#the thread to check if a neighbor hasn't been heard for 3*timeout
def shutdownwhen3Timeout():

    while 1:
        for i in mynei['timer']:
            #print i
            te=time.ctime()
            if (datetime.datetime.strptime(te, "%a %b %d %H:%M:%S %Y")-datetime.datetime.strptime(i, "%a %b %d %H:%M:%S %Y")).seconds > 3*timeout:
                neiidx=mynei['timer'].index(i)
                neiaddr=mynei['address'][neiidx]

                rtidx=ndict['address'].index(neiaddr)
                ndict['cost'][rtidx]=INF
                sendDV(ndict)

                linknum=0
                while linknum<len(ndict['link']):

                    #print linknum
                    if ndict['link'][linknum]==neiaddr[0]+':'+str(neiaddr[1]):
                        #print 'TIMEOUTdown ',neiaddr[0]+':'+str(neiaddr[1])
                        ndict['cost'][linknum]=INF
                        sendDV(ndict)
                        #print disvecstr
                        #print '\n'
                    linknum+=1

                del mynei['timer'][neiidx]
                del mynei['address'][neiidx]

                #sendDV()

            else:
                pass

        if shutdownflag==1:
            break


#thread that keep sending routing table for every timeout interval
def sendwhenTimeout():

    ts=time.ctime()
    while 1:
        te=time.ctime();
        if (datetime.datetime.strptime(te, "%a %b %d %H:%M:%S %Y")-datetime.datetime.strptime(ts, "%a %b %d %H:%M:%S %Y")).seconds < timeout:
            pass
        else:
            sendDV(ndict)
            ts=time.ctime()
        if shutdownflag==1:
            break



#show routing table
def show_RT():
    disvecstr=''

    i=0
    while i<len(ndict['address']):
        temp='Destination='+ndict['address'][i][0]+':'+str(ndict['address'][i][1])+', Cost='+str(ndict['cost'][i])+', Link=('+ndict['link'][i]+')\n'

        disvecstr+=temp
        i+=1
    print disvecstr+'\n'

#linkdown
def link_down(downip,downport):
    addr=(downip,downport)
    #print mynei
    if addr in mynei['address']:
        neiidx=mynei['address'].index(addr)
        del mynei['address'][neiidx]
        del mynei['timer'][neiidx]

        #print mynei

        #i=0
        #while i<3:
        s_send.sendto(localip+':'+str(localport)+';'+'LINKDOWN',addr)
            #i+=1

        downidx=ndict['address'].index(addr)
        originalcost['address'].append(addr)
        ocost=ndict['cost'][downidx]
        originalcost['cost'].append(ocost)
        olink=ndict['link'][downidx]
        originalcost['link'].append(olink)

        ndict['cost'][downidx]=INF
        sendDV(ndict)

        linknum=0
        while linknum<len(ndict['link']):

            print linknum
            if ndict['link'][linknum]==addr[0]+':'+str(addr[1]):
                #print 'down TARGET ',addr[0]+':'+str(addr[1])
                ndict['cost'][linknum]=INF
                sendDV(ndict)
                #print disvecstr
                #print '\n'
            linknum+=1
        #sendDV()

        #print originalcost,mynei
    else:
        print "The target is not your neighbor, link cannot be shut down"


#linkup
def link_up(upip,upport):
    addr=(upip,upport)
    if addr in ndict['address']:
        oidx=originalcost['address'].index(addr)
        ocost=originalcost['cost'][oidx]
        olink=originalcost['link'][oidx]

        upidx=ndict['address'].index(addr)
        ndict['cost'][upidx]=ocost
        ndict['link'][upidx]=olink

        s_send.sendto(localip+':'+str(localport)+';'+'LINKUP',addr)

        mynei['address'].append(addr)
        mynei['timer'].append(time.ctime())
        del originalcost['address'][oidx]
        del originalcost['cost'][oidx]
        del originalcost['link'][oidx]
        sendDV(ndict)


        #sendDV()
        #print originalcost
        #print mynei
    else:
        print "The link doesn't exist, so cannot be restored"


#close
def close():
    global shutdownflag
    shutdownflag=1
    pass


#add initial input to neighbor list
neighbornum=len(neighbors)
if neighbornum%3==0:
    neighbornum=neighbornum/3
    i=0
    while i<neighbornum:
        nip=neighbors[3*i]
        nport=int(neighbors[3*i+1])
        ncost=int(neighbors[3*i+2])

        #print neighbornum,nip,nport,ncost

        #add neighbor information to dictionary. one key is address(ip,port), the other key is cost
        neilink=nip+':'+str(nport)
        add_neighbor((nip,nport),ncost,neilink)
        i+=1
else:
    print 'wrong information of neighbors,ip address, port and cost of each neighbor are required\nPlease type CLOSE'



#main thread, deal with usr input
while 1:
    try:
        t1=time.ctime();
        while 1:
            t2=time.ctime();
            if (datetime.datetime.strptime(t2, "%a %b %d %H:%M:%S %Y")-datetime.datetime.strptime(t1, "%a %b %d %H:%M:%S %Y")).seconds >2:
               break

        sendDV(ndict)

        # tr=threading.Thread(target=recvFunc)
        # tr.setDaemon(True)
        # tr.start()

        tst=threading.Thread(target=sendwhenTimeout)
        tst.setDaemon(True)
        tst.start()

        tsd=threading.Thread(target=shutdownwhen3Timeout)
        tsd.setDaemon(True)
        tsd.start()

        while 1:
            input=raw_input('\n>>\n')
            input=input.split(' ')
            if input[0]=='SHOWRT':
                show_RT()
            elif input[0]=='LINKDOWN':
                link_down(input[1],int(input[2]))
            elif input[0]=='LINKUP':
                link_up(input[1],int(input[2]))
            elif input[0]=='CLOSE':
                close()
            else:
                print 'Cannot recognize the command'

            if shutdownflag==1:
                break

        if shutdownflag==1:
            break



    except IndexError:
        print 'Wrong input format.'



slisten.close()
s_send.close()





