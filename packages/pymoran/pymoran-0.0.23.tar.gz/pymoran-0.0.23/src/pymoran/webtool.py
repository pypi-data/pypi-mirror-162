from pymoran import strtool

class MsgClass:
    def __init__(self):
        self.msgdata = {
            'code': -1,
            'msg': '',
            'data': {},
            'other': {}
        }
        self.jsonclass = strtool.JsonClass()

    # def change_datatype(self, byte):
    #     if isinstance(byte, bytes):
    #         return str(byte, encoding='utf-8')
    #     return json.JSONEncoder.default(byte)

    def successMsg(self, msg: str = '', data: dict or list = {}):
        '''
        成功消息
        :param msg 提示内容，默认空
        :param data 回传的内容，默认空字典
        :return {str} Json字符串
        '''
        self.msgdata['code'] = 0
        self.msgdata['msg'] = msg
        self.msgdata['data'] = data
        return self.jsonclass.jsonToDumps(self.msgdata)

    def errorMsg(self, msg: str = ''):
        '''
        错误消息
        :param msg 提示内容，默认空
        :return {str} Json字符串
        '''
        self.msgdata['code'] = -1
        self.msgdata['msg'] = msg
        return self.jsonclass.jsonToDumps(self.msgdata)

    def abnormalMsg(self, msg: str = ''):
        '''
        异常消息
        :param msg 提示内容，默认空
        :return {str} Json字符串
        '''
        self.msgdata['code'] = -2
        self.msgdata['msg'] = msg
        return self.jsonclass.jsonToDumps(self.msgdata)

    def loginMsg(self, data: dict or list = {}):
        '''
        登录成功消息
        :param msg 提示内容，默认空
        :return {str} Json字符串
        '''
        self.msgdata['code'] = 1000
        self.msgdata['msg'] = 'success'
        self.msgdata['data'] = data
        return self.jsonclass.jsonToDumps(self.msgdata)

    def logoutMsg(self):
        '''
        未登录消息
        :return {str} Json字符串
        '''
        self.msgdata['code'] = 1001
        self.msgdata['msg'] = '登录状态已失效，请重新登录！'
        return self.jsonclass.jsonToDumps(self.msgdata)

    def customMsg(self, code: int = 0, msg: str = '', data: dict or list = {}, other: dict or list = {}):
        '''
        自定义消息
        :param code 消息代码，默认0
        :param msg 提示内容，默认空
        :param data 回传的内容，默认空字典
        :param other 其他内容，默认空字典
        :return {str} Json字符串
        '''
        self.msgdata['code'] = code
        self.msgdata['msg'] = msg
        self.msgdata['data'] = data
        self.msgdata['other'] = other
        # if d:
        #     # d参数为True则不进行json转换
        #     return msgdata
        return self.jsonclass.jsonToDumps(self.msgdata)
