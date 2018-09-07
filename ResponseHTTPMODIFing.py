#encoding=utf-8
import os, io, sys, re, time, base64, json
import webbrowser, urllib.request
import socket
import time
import http.server
from socketserver import ThreadingMixIn
from urllib.parse import unquote
import logging
import cgi

HOST,PORT='',8083
def testJsonResponse():
    Result ={'result':False} 
    RootID  ={'RootID':'testRootId'}
    ContextID ={'ContextID':'TESTcontextID'}
            #print("第二次ID",contextID)  
    TxType  ={'TxType':'txType'}
    PaymentAccountTime  ={'PaymentAccountTime':'20180905104930216'}
    Status ={'Status':20}
    ResponseCode    ={'ResponseCode':'2000'}
    ResponseMessage ={'ResponseMessage':'OK'}
    response=Result.copy()
        #print("第二次ID",Result)
    response.update(RootID)
        #print("第二次ID",RootID)
        #print("第二次ContextID",ContextID)
        #print("第二次response",response)
    response.update(ContextID)
    response.update(TxType)
        #print("第二次ID",TxType)
    response.update(PaymentAccountTime)
        #print("第二次ID",PaymentAccountTime)
    response.update(Status)
    response.update(ResponseCode)
    response.update(ResponseMessage)
    response=json.dumps(response)
    return response
def httpResponse(stdout):
    print(time.time())
    print("传入参数类型",type(stdout))
    print("传入参数值",stdout)
    messge="message="
    #post获得参数为str，json.loads需要的传参是bytes类型，因此进行编码转换#
    weatherInfo=stdout[len(messge):]
    jsonData = json.loads(bytes(weatherInfo,encoding="utf-8"))
    #输出JSON数据
    Fee = jsonData["fee"]
    contextID =jsonData["contextID"]
    rootID =jsonData["rootID"]
    txType =jsonData["txType"]
    #退款返回
    if 'RefundSource' in jsonData:
        if(Fee%2==1):
            Result ={'result':True} 
            RootID  ={'RootID':rootID}
            ContextID ={'ContextID':contextID}  
            TxType  ={'TxType':txType}
            Status ={'Status':20}
            ResponseCode    ={'ResponseCode':'2000'}
            ResponseMessage ={'ResponseMessage':'OK'}
        else:
            Result ={'result':True} 
            RootID  ={'RootID':rootID}
            ContextID ={'ContextID':contextID}  
            TxType  ={'TxType':txType}
            Status ={'Status':20}
            ResponseCode    ={'ResponseCode':'2000'}
            ResponseMessage ={'ResponseMessage':'OK'}
        response=Result.copy()
        response.update(RootID)
        response.update(ContextID)
        response.update(TxType)
        response.update(Status)
        response.update(ResponseCode)
        response.update(ResponseMessage)
        response=json.dummps(response)
    else:#非退款
        if(Fee%2==1):
            Result ={'resul':True} 
            RootID  ={'RootID':rootID}
            ContextID ={'ContextID':contextID}
            #print("第一次ID",contextID)  
            TxType  ={'TxType':txType}
            PaymentAccountTime  ={'PaymentAccountTime':'20180905104930216'}
            Status ={'Status':20}
            ResponseCode    ={'ResponseCode':'2000'}
            ResponseMessage ={'ResponseMessage':'OK'}
        else:
            Result ={'result':True} 
            RootID  ={'RootID':rootID}
            ContextID ={'ContextID':contextID}
            #print("第二次ID",contextID)  
            TxType  ={'TxType':txType}
            PaymentAccountTime  ={'PaymentAccountTime':'20180905104930216'}
            Status ={'Status':10}
            ResponseCode    ={'ResponseCode':'2000'}
            ResponseMessage ={'ResponseMessage':'OK'}
        response=Result.copy()
        #print("第二次ID",Result)
        response.update(RootID)
        #print("第二次ID",RootID)
        #print("第二次ContextID",ContextID)
        #print("第二次response",response)
        response.update(ContextID)
        response.update(TxType)
        #print("第二次ID",TxType)
        response.update(PaymentAccountTime)
        #print("第二次ID",PaymentAccountTime)
        response.update(Status)
        response.update(ResponseCode)
        response.update(ResponseMessage)
        response=json.dumps(response)
    print(time.time()) 
    return response
class myHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        #logging.warning(self.headers.get('Content-Length'))
        logging.warning(self.headers.get_content_maintype())
        logging.warning(self.headers.items())
        #读取限制长度，以免读取超时
        dataStr=self.rfile.read(int(self.headers.get('Content-Length')))
        dataStr = dataStr.decode(encoding="utf-8")
        #print("请求数据为：\n", dataStr)
        file_name = unquote(dataStr)
        file_name =file_name[:(len(file_name)-12)]
        print('获得数据为',file_name)
        datere=httpResponse(file_name)
        print('输出响应内容为',datere)
        #testrespings=testJsonResponse()
        try:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(datere,encoding="utf8"))
        except Exception as e:
            print("socket.error : Connection broke. Aborting" + str(e))
            self.wfile._sock.close()
            self.wfile._sock=None
            return False
        print("success prod")
        return True

    def get_data_string(self):
        now = time.time()
        clock_now = time.localtime(now)
        cur_time = list(clock_now)
        date_string = "%d-%d-%d-%d-%d-%d" % (cur_time[0],
                cur_time[1],cur_time[2],cur_time[3],cur_time[4],cur_time[5])
        return date_string
    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return
            mname = 'do_' + self.command
            print("真实请求方式",mname)
            if not hasattr(self, mname):
                self.send_error(501, "Unsupported method (%r)" % self.command)
                return
            method = getattr(self, mname)
            print("before call ",mname)
            method()
            #增加 debug info 及 wfile 判断是否已经 close
            print("after call ",mname)
            if not self.wfile.closed:
                self.wfile.flush() #actually send the response if not already done.
            print("after wfile.flush()")
        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return


class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""
    pass
    

if __name__ == "__main__":
    try:
        server = ThreadedHTTPServer((HOST,PORT), myHandler)
        print('Started httpserver on port ',PORT)
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

