import json

import registry, os

appInfos = registry.findAppsVer()

for n in appInfos.keys():
    head = "./temp/Registry/"
    path = registry.judgePackage_Name(n)
    names = n.split(".")
    if not os.path.isdir(head + names[0]):
        os.mkdir(head + names[0])
    head += names[0] + "/"
    if not os.path.isdir(head + names[1]):
        os.mkdir(head+names[1])
    head += names[1] + "/"
    if not os.path.isfile(head + names[2] +".json"):
        with open(head+names[2]+".json","w") as p:
            json.dump("", p)
    registry.update_value(names[0], names[1], names[2], appInfos[n])
