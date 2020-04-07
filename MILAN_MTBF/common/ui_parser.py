import os
import time

lib_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from automator.uiautomator import Device


class UIParser():
    @staticmethod
    def nest(self, func):
        def wrapper(*args, **kwargs):
            func(args)

        return wrapper

    @staticmethod
    def run(obj, params, exceptfunc=None):
        device = obj if isinstance(obj, Device) else obj.device

        def param_parser(param):
            if isinstance(param, dict):
                for k, v in param.items():
                    if v == None:
                        param.pop(k)
            else:
                for v in param:
                    if v == None:
                        param.remove(v)

        def error(param):
            if param.has_key("assert") and param['assert'] == False:
                return False
            else:
                print "%s error!" % param
                exceptfunc() if (exceptfunc) else None
                return True

        def listfoo(param):
            resault = True
            if isinstance(param["content"], list):
                for content in param["content"]:
                    param_tmp = param
                    param_tmp["content"] = content
                    resault = resault and listfoo(param)
            elif param["id"] == "meta":
                resault = resault and getattr(obj, param["content"])(
                    *param["action"]["param"] if param.has_key("action") and param["action"].has_key("param") else [])
            else:
                print param
                if param_parser(param["id"]) == {}:
                    return True
                select = device(**{param["id"]: param["content"]})
                action = select.wait.exists(timeout=5000) if not param.has_key("wait") else select.wait.exists(
                    timeout=int(param["wait"]))
                if action and not (param.has_key("action") and param["action"] == None):
                    getattr(select, "click")(None) if not param.has_key("action") else getattr(select,
                                                                                               param["action"]["type"])(
                        *param["action"]["param"] if param["action"].has_key("param") else [])
                    time.sleep(
                        param["action"]["delay"] if param.has_key("aciton") and param["action"].has_key("delay") else 0)
                resault = resault and action
            return resault

        def dictfoo(param):
            resault = True
            if not param.has_key("id"):
                return False
            if isinstance(param["id"], list):
                for content in param["id"]:
                    param_tmp = param
                    param_tmp["id"] = content
                    if param["id"].has_key("action"):
                        param_tmp["action"] = param["action"]
                    resault = resault and listfoo(param)
            elif param["id"].has_key("meta"):
                resault = resault and getattr(obj, param["id"]["meta"])(
                    *param["action"]["param"] if param.has_key("action") and param["action"].has_key("param") else [])
            else:
                if param_parser(param["id"]) == {}:
                    return True
                select = device(**param["id"])
                # action=select.wait.exists(timeout = 5000) if ((not param.has_key("wait")) or ((param.has_key("wait") and param["wait"]))) else select.wait.exists(timeout = int(param["wait"]))
                action = select.wait.exists(timeout=5000) if not param.has_key("wait") else select.wait.exists(
                    timeout=int(param["wait"]))
                if action and not (param.has_key("action") and param["action"] == None):
                    getattr(select, "click")(None) if not param.has_key("action") else getattr(select,
                                                                                               param["action"]["type"])(
                        *param["action"]["param"] if param["action"].has_key("param") else [])
                    time.sleep(
                        param["action"]["delay"] if param.has_key("aciton") and param["action"].has_key("delay") else 0)
                resault = resault and action
            return resault

        for param in params:
            if isinstance(param, list):
                UIParser.run(obj, param)
            else:
                if param.has_key("id") and isinstance(param["id"], dict):
                    if not dictfoo(param):
                        if (error(param)):
                            return False
                elif param.has_key("id") and param.has_key("content") and not isinstance(param["id"], dict):
                    if not listfoo(param):
                        if (error(param)):
                            return False
        return True
