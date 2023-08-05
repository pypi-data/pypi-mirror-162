class Queue():
    def __init__(self,maxlen):
        self.__queuelst = []
        self.__front = 0
        self.__rear = -1
        self.__maxlen = maxlen
        self.__len = 0
        
    def isempty(self):
        return self.__len == 0
    
    def isfull(self):
        return self.__maxlen == self.__len
    
    def length(self):
        return self.__len
    
    def put(self,value):
        if self.isfull == True:
            return False
        self.__queuelst.append(value)
        self.__rear += 1
        self.__len += 1
        
    def leave(self):
        del self.__queuelst[self.__front]
        self.__len -= 1
        
    def show(self):
        import prettytable
        tb = prettytable.PrettyTable()
        tb.field_names = ['QueueIdx'+str(i) for i in range(0,self.__len)]
        tb.add_row(self.__queuelst)
        return tb
    
    