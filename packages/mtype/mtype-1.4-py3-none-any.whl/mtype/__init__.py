#Import Librarys
import os, sys

def match(v, t, output=False):
    if type(v) == t:
        match str(t):
            case "<class 'str'>":
                print(os.path.basename(sys.argv[0]) + ": INFO: '" + str(v) + "' is String: True")
            case "<class 'int'>":
                print(os.path.basename(sys.argv[0]) + ": INFO: '" + str(v) + "' is Integer: True")
            case "<class 'bool'>":
                print(os.path.basename(sys.argv[0]) + ": INFO: '" + str(v) + "' is Boolean: True")
            case _:
                print(os.path.basename(sys.argv[0]) + ": INFO: '" + str(v) + "' is "+str(t)+": True")
        return True
    elif (output):
        match str(t):
            case "<class 'str'>":
                print(os.path.basename(sys.argv[0]) + ": ERROR: '" + str(v) + "' is String: False")
            case "<class 'int'>":
                print(os.path.basename(sys.argv[0]) + ": ERROR: '" + str(v) + "' is Integer: False")
            case "<class 'bool'>":
                print(os.path.basename(sys.argv[0]) + ": ERROR: '" + str(v) + "' is Boolean: False")
            case _:
                print(os.path.basename(sys.argv[0]) + ": ERROR: '" + str(v) + "' is "+str(t)+": False")
        return False
    return False
    
def credits():
    print("INFO: 'mtype' was created by HMegaCrafter")
def credit():
    print("INFO: 'mtype' was created by HMegaCrafter")
def author():
    print("INFO: 'mtype' was created by HMegaCrafter")
def creator():
    print("INFO: 'mtype' was created by HMegaCrafter")