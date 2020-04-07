# _*_ coding: UTF-8 _*_
import requests
import re
import socket
import os
import threading
import time
import json
import hashlib
import collections
from requests.exceptions import ConnectionError
from lib.Uiautomator.adbClient import AdbClient

DEVICE_PORT = int(os.environ.get('UIAUTOMATOR_DEVICE_PORT', '9008'))
LOCAL_PORT = int(os.environ.get('UIAUTOMATOR_LOCAL_PORT', '9008'))
HTTP_TIMEOUT = 60

class NotFoundHandler(object):

    '''
    Handler for UI Object Not Found exception.
    It's a replacement of UiAutomator watcher on device side.
    '''

    def __init__(self):
        self.__handlers = collections.defaultdict(lambda: {'on': False, 'handlers': []})

    def __get__(self, instance, owner):
        return self.__handlers[instance.serialno]
    
class JsonRpcError(Exception):
    @staticmethod
    def format_errcode(errcode):
        m = {
            -32700: 'Parse error',
            -32600: 'Invalid Request',
            -32601: 'Method not found',
            -32602: 'Invalid params',
            -32603: 'Internal error',
        }
        if errcode in m:
            return m[errcode]
        if errcode >= -32099 and errcode <= -32000:
            return 'Server error'
        return 'Unknown error'

    def __init__(self, error={}):
        self.code = error.get('code')
        self.message = error.get('message')
        self.data = error.get('data')
        self.exception_name = (self.data or {}).get('exceptionTypeName', 'Unknown')

    def __str__(self):
        return '%d %s: %s' % (
            self.code,
            self.format_errcode(self.code),
            '%s <%s>' % (self.exception_name, self.message))
    
    def __repr__(self):
        return repr(str(self))
    
class RunTestsThread(threading.Thread):
    """
    Runs the instrumentation for the specified package in a new thread.
    """
    def __init__(self, adbClient=None, testClass=None, testRunner=None):
        threading.Thread.__init__(self)
        self.adbClient = adbClient
        self.testClass = testClass
        self.testRunner = testRunner
        self.pkg = re.sub('\.test$', '', self.testClass)
        self.pro = None

    def run(self):
        self.forceStop()
        self.pro = self.adbClient.adb_shell(["am", "instrument", "-w", "%s/%s"%(self.testClass, self.testRunner)], timeout=5, kil=False)

    def forceStop(self):
        self.adbClient.adb_shell(['am', 'force-stop', self.pkg], timeout=5)
        self.adbClient.adb_shell(['am', 'force-stop', self.testClass], timeout=5)
        time.sleep(1)
    
    def stop(self):
        self.forceStop()
        if self.pro and self.pro.is_running():
            try:
                for ch in self.pro.children():
                    ch.kill()
                self.pro.kill()
            except Exception:
                pass
        

class TimeoutRequestsSession(requests.Session):
    def request(self, method, url, **kwargs):
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = HTTP_TIMEOUT
        resp = super(TimeoutRequestsSession, self).request(method, url, **kwargs)
        return resp

class UiAutomatorServer(AdbClient):
    _init_local_port = 9008
    hdlrs = NotFoundHandler()
    
    def __init__(self, serialno=None, local_port=None, device_port=9008, adb_server_host="localhost", adb_server_port=None):
        super(UiAutomatorServer, self).__init__(serialno)
        self.device_port = int(device_port) if device_port else DEVICE_PORT
        self.local_port = self.redirect_port(local_port, adb_server_host)
        self.baseUrl = 'http://%s:%d' % (adb_server_host, self.local_port)
        self._server_jsonrpc_url = self.baseUrl + "/jsonrpc/0"
        self.session = TimeoutRequestsSession()
        self.uiautomator_process = None
        self.start()
    
    def redirect_port(self, local_port=9008, adb_server_host=None):
        try:  
            for line in self.forward_list():
                if self.serialno in line and line.endswith("%d"%self.device_port):
                    return int(line.split()[1][4:])
        except Exception:
            pass
        return self.next_local_port(adb_server_host)
    
    def next_local_port(self, adbHost=None):
        def is_port_listening(port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((str(adbHost) if adbHost else '127.0.0.1', port))
            s.close()
            return result == 0
        if self._init_local_port >= 32764:
            self._init_local_port = 9008
        while is_port_listening(self._init_local_port):
            self._init_local_port += 1
        return self._init_local_port
    
    @property
    def screenshot_uri(self):
        return '%s/screenshot/0' % (self.baseUrl)
    
    def screenshot(self, filename=None):
        try:
            r = requests.get(self.screenshot_uri, timeout=10)
            if filename:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                return filename
            else:
                return r.content
        except Exception:
            self.takeSnapshot(filename)
        
    @property
    def jsonrpc(self):
        """
        Make jsonrpc call easier
        For example:
            self.jsonrpc.pressKey("home")
        """
        class JSONRpcWrapper():
            def __init__(self, server):
                self.server = server
                self.method = None
            
            def __getattr__(self, method):
                self.method = method
                return self

            def __call__(self, *args, **kwargs):
                http_timeout = kwargs.pop('http_timeout', HTTP_TIMEOUT)
                params = args if args else kwargs
                return self.server.jsonrpc_call(self.method, params, http_timeout)

        return JSONRpcWrapper(self)

    def jsonrpc_call(self, method, params=[], http_timeout=60, restart=True):
        """ jsonrpc2 call
        Refs:
            - http://www.jsonrpc.org/specification
        """
        ERROR_CODE_BASE = -32000
        def __rpc_call(method, params=[], http_timeout=60):
            request_start = time.time()
            data = {
                "jsonrpc": "2.0",
                "id": self._jsonrpc_id(method),
                "method": method,
                "params": params,
            }
            data = json.dumps(data).encode('utf-8')
            res = self.session.post(self._server_jsonrpc_url,
                headers={"Content-Type": "application/json"},
                timeout=http_timeout,
                data=data)
            if res.status_code == 502:
                raise Exception(res, "gateway error, time used %.1fs" % (time.time() - request_start))
            if res.status_code != 200:
                raise Exception(self._server_jsonrpc_url, data, res.status_code, res.text, "HTTP Return code is not 200", res.text)
            jsondata = res.json()
            error = jsondata.get('error')
            if not error:
                return jsondata.get('result')

        # error happends
            raise JsonRpcError(error)
        try:
            return __rpc_call(method, params, http_timeout)
        except ConnectionError:
            if restart:
                self.stop()
                self.start(timeout=30)
                return self.jsonrpc_call(method, params, http_timeout, restart=False)            
        except JsonRpcError as e:
            if e.code == ERROR_CODE_BASE - 2 and self.hdlrs['on']:  # Not Found
                try:
                    # any handler returns True will break the left handlers
                    any(handler(self.hdlrs.get('device', None)) for handler in self.hdlrs['handlers'])
                finally:
                    self.hdlrs['on'] = True
                return __rpc_call(method, params, http_timeout)            
            elif e.code == ERROR_CODE_BASE - 1:
                if restart:
                    self.stop()
                    self.start(timeout=30)
                    return self.jsonrpc_call(method, params, http_timeout, restart=False)
            self.stop()
            raise e
    
    def _jsonrpc_id(self, method):
        m = hashlib.md5()
        m.update(("%s at %f" % (method, time.time())).encode("utf-8"))
        return m.hexdigest()
    
    @property
    def alive(self):
        try:
            r = self.session.get("%s/ping" % (self.baseUrl), timeout=2)
            return r.status_code == 200
        except Exception:
            return False
    
    def install_runner(self):
        if self.adb_shell(["pm", "list", "instrumentation", "com.github.uiautomator"]):
            return
        cur_path = os.path.dirname(__file__)
        apks = [os.path.join(cur_path, "apks", "app-uiautomator.apk"), os.path.join(cur_path, "apks", "app-uiautomator-test.apk")]
        self.install(apks)
    
    def start(self, timeout=20):
        if self.get_device_state != "device":
            print("reconnect offline")
            self.adb_command("reconnect offline")
            time.sleep(4)
            if self.get_device_state != "device":
                print("kill-server")
                self.adb_command("kill-server")
                time.sleep(4)
        self.install_runner()
        self.uiautomator_process = RunTestsThread(self, "com.github.uiautomator.test", "android.support.test.runner.AndroidJUnitRunner")
        self.uiautomator_process.start()
        self.forward(self.local_port, self.device_port)

        while timeout > 0:
            if self.alive:
                break
            self.delay(0.1)
            timeout -= 0.1
        else:
            raise IOError("RPC server not started!")
        
    def __del__(self):
        try:
            self.uiautomator_process.stop()
        except Exception:
            pass
    
    def stop(self):
        '''Stop the rpc server.'''
        if not self.alive:
            return
        
        try:
            res = requests.post("%s/stop" % (self.baseUrl))
        except Exception:
            res = None         
        finally:
            if res is not None:
                res.close()
            if self.uiautomator_process:
                self.uiautomator_process.stop()
                self.uiautomator_process = None

if __name__ == "__main__":
    ser = UiAutomatorServer()
        
