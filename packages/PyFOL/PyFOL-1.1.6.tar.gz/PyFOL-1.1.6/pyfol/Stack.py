class Stack():
    def __init__(self):
        self.__top = 0
        self.__stacklst = []
        
    def isempty(self):
        return self.__top==0
    
    def height(self):
        return self.__top
    
    def push(self,value):
        self.__stacklst.append(value)
        self.__top += 1
        
    def pop(self):
        self.__stacklst.pop()
        
    def show(self):
        import prettytable
        tb = prettytable.PrettyTable()
        self.__stacklst.reverse()
        tb.add_column("Top",self.__stacklst)
        return tb