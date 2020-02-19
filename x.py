#!/usr/bin/env python3
import os, socket, hashlib, subprocess

socket.setdefaulttimeout(30)

print("---====PROJECT-X====---", "\n\n(1) Send a file\n(2) receive a file\n(3) exit")
while True:
    option = input("please enter the option you'd like to use: ")
    if option == "1" or option == "2": break
    elif option == "3":
        print("\nThank you for using PROJECT-X")
        exit()
    else: print("Invalid option! please try again....")

def f_size(file):
    size = file.seek(0,2)
    file.seek(0)
    return size

def check_host(ip):
    stat,output =subprocess.getstatusoutput(("ping -c 2 "+ip))
    return stat == 0



def receiver():
    print("preparing to receive a file...")
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(("",4545))
    sock.listen(1)
    input("\n\x1b[0;32mpress ENTER when (sender) is ready!\x1b[m")
    try:
        (sender,addy) = sock.accept()
    except:
        print("\x1b[0;32mdidn't get any connection or connection timeout!\x1b[m")
        exit()
    if sender:
        sender.send(b'hi')
        if bool(sender.recv(2) == b'hi'):
            print("\x1b[0;93mConnection established with:\x1b[1;32m", addy[0], "\x1b[m on port: ", addy[1])
            pass
        else:
            print("\x1b[0;32mdidn't get any connection or connection timeout!\x1b[m")
            exit()

    hash = sender.recv(64)
    print("got the hash: \""+hash.decode()+"\"")
    sender.send(b'ok')
    name = sender.recv(100).decode()
    print("file name:"+name,end='\t')
    sender.send(b'ok')
    size = int(sender.recv(50).decode())
    print(" size:",format(size/1024,".2f")+"KB")
    accept = input("press ENTER to accept or type 'NO' to refuse:")
    if accept:
        sender.send(b'no')
        exit()
    else:
        sender.send(b'send')
        pass
    if os.path.exists("received_files"): pass
    else: subprocess.call(['mkdir', 'received_files'])

    if os.path.exists("received_files/"+name):
        print("warning!!! file already exists !\n (1) overwrite file (default)\n (2) add  '(copy)' to the end of the file name.")
        op = input("choose an option: ")
        if op == '1' or op == '': pass
        else: name= "(copy)"+name
        file = open("received_files/" + name, "wb+")
    else:
        file = open("received_files/"+name,"wb+")


    while file.tell() < size:
        file.write(sender.recv(1024))
        prog = (file.tell()/size *100)
        print("Progress: [%d%%]\r"%prog,end='')

    file.seek(0)
    hash_2 = hashlib.sha256(file.read()).hexdigest().encode()
    if hash == hash_2:
        print("\n\x1b[1;32mfile received successfully!\x1b[m")
        print("located at: received_files/"+name)
        sender.send(b'done')
        file.close()
        sender.close()
        sock.close()
        exit()
    else:
        print("\x1b[1;31mERROR!\x1b[m Transfer failed or file corrupt. exiting.... ")
        exit()



def sender():
    print("\n---==please enter file path, or name if file in current directory to send==---")
    f_name = input("\npath/name: ")
    if os.path.exists(f_name):
        pass
    else:
        print("\x1b[1;31mError file doesn't exist....try again\x1b[m\n")
        sender()
        exit()

    try:
        file = open(f_name, "rb")
    except:
        print("\n\x1b[1;31mError couldn't open\x1b[m "+f_name)
        sender()
        exit()
    size = f_size(file)
    base_name = os.path.basename(f_name)
    if size > 500000000: print("\n\x1b[1;35mmwarning the selected file is above 500MB, it might take too long to send over slow connections!\x1b[m\n")
    print("\n\ncalculating sha256 hash now....")
    hash = hashlib.sha256(file.read()).hexdigest().encode()
    print("\x1b[0;32msha256 hash complete\x1b[m["+hash.decode()+"]" )
    print("File:\x1b[1;93m",f_name,"\x1b[m","Size:\x1b[1;93m",format((size/1024),".2f"),"\x1b[mKB")
    file.seek(0)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        ip = input("\nEnter IP/Domain of the receiver: ")
        if check_host(ip):
            print(ip,"\x1b[1;32m is alive and reachable!\x1b[m")
            input("press ENTER when you're ready to connect...\n")
            break
        else:
            print(ip,"\x1b[1;31m is Unreachable or blocking ping requests.\x1b[m")
            x = input("press ENTER to proceed with "+ip+" or type (No) to try again!")
            if x == '': break
            else: pass

    try:
        sock.connect((ip,4545))
    except:
        print("Didn't get any connection or connection timeout!\nPlease make sure the receiver is on.")
        exit()

    sock.send(b'hi')
    if bool(sock.recv(2) == b'hi'):
        print("\x1b[0;93mConnection established with:\x1b[1;32m", ip, "\x1b[m on port: ", '4545')
        pass
    else:
        print("\x1b[0;32mdidn't get any connection or connection timeout!\x1b[m")
        exit()


    sock.send(hash)
    if bool(sock.recv(2)== b'ok'): sock.send(base_name.encode())
    if bool(sock.recv(2) == b'ok'): sock.send(str(size).encode())
    
    try:
        accept = sock.recv(4)
        if accept == b'send': pass
    except:
        print("Receiver didn't accept the file. exiting......")
        exit()

    while file.tell() < size:
        sock.send(file.read(1024))
        prog = (file.tell() / size * 100)
        print("Progress: \x1b[1;36;44[%d%%]\r" % prog, end='')

    if sock.recv(4) ==b'done':
        print("\n\x1b[1;32mTransfer complete!\x1b[m\n")
        exit()
    else:
        print("\x1b[1;31mTransfer failed or file was corrupted during transfer...\x1b[m\n")
        exit()




if option == "1": sender()
if option == "2": receiver()