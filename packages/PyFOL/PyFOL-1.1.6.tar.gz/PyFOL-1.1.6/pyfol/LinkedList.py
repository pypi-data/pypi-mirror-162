class LinkedList():
    class Node():
        def __init__(self,value=None,next=None,prev=None):
            self.value = value
            self.next = next
            self.prev = prev
            
    def __init__(self):
        self.__head = None
        self.__tail = None
        self.__len = 0
    
    def isempty(self):
        return self.__head == None
    
    def length(self):
        return self.__len
    
    def append(self,value):
        if self.__head == None:
            self.__head = self.Node(value)
            self.__tail = self.__head
        else:
            self.__tail.next = self.Node(value,prev=self.__tail)
            self.__tail = self.__tail.next
        self.__len += 1
        
    def insert(self,idx,value):
        pointer = self.__head
        for i in range(idx-1):
            pointer = pointer.next
        serach = self.Node(value,pointer.next,pointer.prev)
        pointer.next = serach
        serach.next.prev = serach
        self.__len += 1
        
    def add(self,value):
        node = self.Node(value)
        if self.__head == None:
            self.__head = node
            self.__tail = node
        else:
            self.__head.prev = node
            node.next = self.__head
            self.__head = node
        self.__len += 1
        
    def remove(self,idx):
        pointer = self.__head
        for i in range(idx):
            pointer = pointer.next
        if pointer == self.__head:
            self.__head = self.__head.next
            if pointer.next:
                pointer.next.prev = None
            return
        if pointer.next == None:
            pointer.prev.next = pointer.next
            return
        pointer.prev.next = pointer.next
        pointer.next.prev = pointer.prev
        self.__len -= 1
        
    def delete(self,value,delall=False):
        pointer = self.__head
        for i in range(self.length()-1):
            if pointer.value == value:
                self.remove(i)
                return
            pointer = pointer.next
        
    def serach(self,value):
        pointer = self.__head
        for i in range(self.length()-1):
            if pointer.value == value:
                return i
            else:
                pointer = pointer.next
        return False
    
    def isexist(self,value):
        pointer = self.__head
        for i in range(self.length()-1):
            if pointer.value == value:
                return True
            else:
                pointer = pointer.next
        return False
    
    def setvalue(self,idx,value):
        pointer = self.__head
        for i in range(idx):
            pointer = pointer.next
        pointer.value = value
        return False
    
    
    def show(self):
        import prettytable
        tb = prettytable.PrettyTable()
        tb.field_names = ["Value","Next","Prev"]
        pointer = self.__head
        while pointer:
            if pointer.next == None:
                if pointer.prev == None:
                    tb.add_row([pointer.value,None,None])
                else:
                    tb.add_row([pointer.value,None,pointer.prev.value])
            else:
                if pointer.prev == None:
                    tb.add_row([pointer.value,pointer.next.value,None])
                else:
                    tb.add_row([pointer.value,pointer.next.value,pointer.prev.value])
            pointer = pointer.next
        return tb
        

    
        
    