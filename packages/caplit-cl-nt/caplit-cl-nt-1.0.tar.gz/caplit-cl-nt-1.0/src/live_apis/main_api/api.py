# api.py vx2

import json
import os
import time
from subprocess import Popen

import requests

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.52"
}

def openApp(App):
    try:
        Popen("python " + App)
    except Exception as e:
        error = repr(e)
        log(error)


def command(command):
    try:
        Popen(command)
        doneLog(command)

    except Exception as e:
        error = repr(e)
        log(error)


def log(text):
    with open("../log.txt", "a") as l:
        ti = time.asctime(time.localtime(time.time()))
        ti = "\n" + ti + "\n"
        info = ti + text + "\n"
        l.write(info)


def doneLog(item):
    item = "run " + item + " done"
    log(item)

def writeTemp(file, content):
    if ".json" in file:
        proJSON("./temp/" + file, "w", content=content)
    elif ".txt" in file:
        proFile("./temp/" + file, "w", content=content)

def readTemp(file):
    if ".json" in file:
        data = proJSON("./temp/" + file, "r")
    elif ".txt" in file:
        data = proFile("./temp/" + file, "r")
    return data


def findApps():
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
                            appName = appdata["name"]
                            path = "../Application/" + i + "/application.py"
                            appsInfo[appName] = path
    return appsInfo


def proFile(filedir, mode, encoding, content=None):
    if mode == "w" or mode == "wb" or mode == "a":
        with open(filedir, mode, encoding=encoding) as w:
            w.write(content)
    elif mode == "r":
        with open(filedir, mode, encoding=encoding) as r:
            cont = r.read()
            return cont


def proJSON(filedir, mode, content=None):
    if mode == "w" or mode == "wb" or mode == "a":
        with open(filedir, mode) as wj:
            json.dump(content, wj)
    elif mode == "r":
        with open(filedir, mode) as rj:
            cont = json.load(rj)
            return cont


def judgeEXT(fileDir):
    ext = os.path.splitext(fileDir)[-1]
    return ext


def musicPlay(com, musicFile=None):
    import pygame
    if com == "play":
        pygame.mixer.music.load(musicFile)
        pygame.mixer.music.play(1, 0)
    elif com == "stop":
        pygame.mixer.music.stop()
    elif com == "pause":
        pygame.mixer.music.pause()
    elif com == "unpause":
        pygame.mixer.music.unpause()
    elif com == "stop":
        pygame.mixer.music.stop()


def download(url, filedir, headers):
    import requests
    bt = requests.get(url, headers=headers)
    print("开始下载")
    proFile(filedir=filedir, mode="wb", content=bt)
    print("下载完成")


def pkgInfo(pkgName, Item):
    with open("../Application/" + pkgName + "/appinfo.json", "r") as infoes:
        data = json.load(infoes)
        reInfo = data["Item"]
    return reInfo


def rcPath(packName, file):
    rc = "../Application/" + packName + "/resources/" + file
    return rc


def exZipfile(fileDir, exDir):
    import zipfile
    zip_file = zipfile.ZipFile(fileDir)
    zip_list = zip_file.namelist()  # 得到压缩包里所有文件
    for f in zip_list:
        if os.path.exists(exDir):
            zip_file.extract(f, exDir)  # 循环解压文件到指定目录
        else:
            os.mkdir(exDir)
            zip_file.extract(f, exDir)
    zip_file.close()


def search_file(path, dir_in_search, keyword=None):
    if keyword is not None:
        result = os.listdir(path)
        Result = []
        for i in result:
            if keyword in i:
                if dir_in_search:
                    if path[-1] == "/" or path[-1] == "\\":
                        if os.path.isdir(path + i):
                            search_file(path, dir_in_search=True, keyword=keyword)
                        else:
                            Result.append(i)
                    else:
                        if os.path.isdir(path + os.sep + i):
                            search_file(path, dir_in_search=True, keyword=keyword)
                        else:
                            Result.append(i)
                else:
                    Result.append(i)
        try:
            if Result[0] == "":
                outcome = "none"
                return outcome
            else:
                return Result
        except:
            outcome = "none"
            return outcome
    else:
        files = os.listdir(path)
        return files


def installPkgToBox(path):
    try:
        with open(path, "rb") as ope:
            file = ope.read()
            with open("./temp/pkgtemp.zip", "wb") as save:
                save.write(file)
        exZipfile("./temp/pkgtemp.zip", "../Application/")
        done = True
    except:
        done = False
    return done

def resize_image(file, size):
    # file应为文件路径而不是已打开的PIL图像
    # size应为一个元组
    from PIL import Image
    image = Image.open(file)
    image = image.resize(size)
    return image

def message(title,author,content):
    with open("./temp/message.json","r",encoding="utf-8") as r:
        me = json.load(r)
        me["TITLE"] = title
        me["AUTHOR"] = author
        me["CONTENT"] = content
    with open("./temp/message.json","w",encoding="utf-8") as w:
        json.dump(me,w)

def get_pietech_message():
    try:
        p = requests.get("https://pytoolbox-1301360149.cos.ap-nanjing.myqcloud.com/message.json",headers=headers)
        with open("temp/pt_message.json","wb") as m:
            m.write(p.content)
        with open("temp/pt_message.json","r",encoding="utf-8") as n:
            ni = json.load(n)
            try:
                if ni["show"] == "True":
                    return True
                else:
                    return False
            except:
                log("无法读取消息.请在官网进行反馈.ERROR0")
                return False
    except:
        return False

def version():
    with open("./temp/Config/Version.json","r") as c:
        c = json.load(c)
    return c

def config(pak,son,name):
    with open("./temp/Config/{}/{}/{}.json".format(pak,son,name),"r",encoding="utf-8") as r:
        content = json.load(r)
    return content

def write_config(pak,son,name,content):
    with open("./temp/Config/{}/{}/{}.json".format(pak,son,name),"w",encoding="utf-8") as w:
        json.dump(content,w)

if __name__ == "__main__":
    print("这不是一个直接运行的文件QAQ")
    print("详见https://gitee.com/ptstudio/py-tool-box/wikis/开发者文档/api.py函数集说明")
    os.system(
        "pause"
    )