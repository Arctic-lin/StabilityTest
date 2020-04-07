import os


def get_crash(path):
    """
    have Crash/ANR/AndroidReboot in a given path
    :param path: a given path
    :return: return a list [{keyword:filepath}, {keyword:filepath}]
    """
    keywords = ["Crash", "ANR", "AndroidReboot"]
    list = os.listdir(path)
    folders = []
    for line in list:
        filepath = os.path.join(path, line)
        if os.path.isdir(filepath):
            for keyword in keywords:
                if keyword in line:
                    folders.append({keyword: filepath})
                    break
    if not folders:
        print "have no Crash/ANR/AndroidReboot"
    else:
        for item in folders:
            for key, value in item.items():
                print key, "->", value
    return folders