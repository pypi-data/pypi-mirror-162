import json
import os
import platform
import shutil


def path(pak):
    return "./temp/Registry/{}".format(pak)


def new_configpack(pak):
    os.mkdir(path(pak))


def new_son(pak,son):
    if not os.path.isdir("./temp/Registry/{}".format(pak)):
        new_configpack(pak)
    os.mkdir("./temp/Registry/{}/{}".format(pak,son))


def new_config(pak,son,file):
    pth = "./temp/Registry/{}/{}".format(pak,son)
    if not os.path.isdir("./temp/Registry/{}".format(pak)):
        new_configpack(pak)
    if not os.path.isdir(pth):
        new_son(pak,son)
    shutil.move(file,pth)


def remove_config(pak,son,name):
    pth = "./temp/Registry/{}/{}/{}.json".format(path(pak),son,name)
    if os.path.isfile(pth):
        os.remove(pth)


def remove_son(pak,son):
    pth = "./temp/Registry/{}/{}".format(pak,son)
    if os.path.isdir(pth):
        shutil.rmtree(pth)


def remove_pak(pak):
    path = "./temp/Registry/{}".format(pak)
    if os.path.isdir(path):
        shutil.rmtree(path)

def update(pak,son,name,file):
    pth = "{}/{}/{}.json".format(path(pak),son,name)
    try:
        if os.path.isfile(pth):
            shutil.move(file,"./temp/Registry/{}/{}".format(pak,son))
            return "DONE"
        else:
            return "CAN'T FIND"
    except:
        return "ERROR"

def update_value(pak,son,name,value):
    pth = "./temp/Registry/{}/{}/{}.json".format(pak,son,name)
    with open(pth,"w") as w:
        json.dump(value,w)

def update_cpyver():
    with open("./temp/Registry/python/cpython.json")as v:
        json.dump(platform.python_version(),v)

def list():
    lst = os.listdir("./temp/Registry")
    if len(lst) > 0:
        for i in lst:# Registry
            print(i)
            now = "./temp/Registry/"+i
            if os.path.isdir(now):
                fck = os.listdir(now) # Package
                if len(fck) > 0:
                    for n in fck:
                        print("   "+n)
                        now1 = "./temp/Registry/"+i+"/"+n # son
                        if os.path.isdir(now1):
                            mmp = os.listdir(now1) # name
                            for m in mmp:
                                print("        "+m)


def findAppsVer():
    appsInfo = {}
    apps = os.listdir("../Application/")
    for i in apps:
        if "com." in i or "cn." in i:
            file = os.listdir("../Application/" + i)
            if len(file) > 0:
                for n in file:
                    if n == "appinfo.json":
                        with open("../Application/" + i + "/" + "appinfo.json", "r", encoding='utf-8') as r:
                            appdata = json.load(r)
                            appVer = appdata["version"]
                            appsInfo[i] = appVer
    return appsInfo

def judgePackage_Name(name:str):
    name = name.split(".")
    path = "./temp/Registry/{}/{}/{}.json".format(name[0],name[1],name[2])
    return path