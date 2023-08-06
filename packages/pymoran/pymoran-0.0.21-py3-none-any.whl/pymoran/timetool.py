import time


class TimeClass:
    def __init__(self) -> None:
        pass

    def localdate(self):
        '''
        获取格式化的当前日期
        return {str} 示例：2000-12-12
        '''
        return time.strftime('%Y-%m-%d', time.localtime())

    def localtime(self):
        '''
        获取格式化的当前时间
        return {str} 示例：2000-12-12 18:18:18
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def timestamp(self):
        '''
        获取当前时间的时间戳
        return {str}
        '''
        return int(time.time())

    # def timediff(time1, time2):
    #     '''
    #     计算time1与time2的时间差
    #     :param time1 time1
    #     :param time2 time2
    #     return {str}
    #     '''
    #     time1 = time.strptime('%Y-%m-%d %H:%M:%S', time1)
    #     time2 = time.strptime('%Y-%m-%d %H:%M:%S', time2)
    #     timeStamp1 = int(time.mktime(time1))
    #     timeStamp2 = int(time.mktime(time2))
    #     return timeStamp2-timeStamp1


if __name__=='__main__':
    pass
