class String():
    def __init__(self,__operationstr):
        self.__operationstr = __operationstr
        
    def setstr(self,nowstr):
        self.__operationstr = nowstr
        
    def clearstr(self):
        self.__operationstr = ''
        
    def split(self,substr=' ',amount=-1,rm_empty_char=True,splitmode=None,sortword=False,setword=False):
        if self.__operationstr[-1] != substr:
            self.__operationstr += substr
        split_list = []
        last_search_pos = 0
        num = 0 if amount != -1 else -1
        substr_pos = self.__operationstr.find(substr,last_search_pos)
        while substr_pos != -1 and (num < amount if num != -1 else True):
            nowsplitword = self.__operationstr[last_search_pos:substr_pos]
            last_search_pos =  substr_pos+len(substr)
            substr_pos =  self.__operationstr.find(substr,last_search_pos)
            if num != -1:
                num += 1               
            if rm_empty_char and nowsplitword == '':   
                continue
            if splitmode == None: 
                split_list.append(nowsplitword)
            elif splitmode == 't':
                split_list.append(nowsplitword.title())
            elif splitmode == 'l':
                split_list.append(nowsplitword.lower())
            elif splitmode == 'u':
                split_list.append(nowsplitword.upper())
        if num != -1:
            surplus = self.__operationstr[last_search_pos:-1]
            split_list.append(surplus)
        if setword == True:
            split_list = list(set(split_list))
        if sortword == True:
            split_list.sort()
        self.__operationstr = self.__operationstr[:-1] + ''
        return split_list
    
    def replace(self,replaced_string,replace_string,amount=-1,returntotal=False):
        last_search_pos = 0
        pos_replaced_string = self.__operationstr.find(replaced_string,last_search_pos)
        num = 0 if amount != -1 else -1
        total = 0
        while pos_replaced_string != -1 and (num < amount if num != -1 else True):
            self.__operationstr = self.__operationstr[:pos_replaced_string] + replace_string + self.__operationstr[pos_replaced_string+len(replaced_string):]
            
            last_search_pos =  pos_replaced_string+len(replace_string)
            pos_replaced_string =  self.__operationstr.find(replaced_string,last_search_pos)
            if num != -1:
                num += 1    
            if returntotal:
                total += 1
        if returntotal:
            return self.__operationstr,total
        elif not returntotal:
            return self.__operationstr
        
    def find(self,findstr,start=0,end=-1,case_insensitive=False):
        findlst = []
        total = 0
        if case_insensitive:
            self.__operationstr = self.__operationstr.lower()
            findstr = findstr.lower()
        for i in range(start+1,len(self.__operationstr) if end==-1 else end):
            if self.__operationstr[i:i+len(findstr)] == findstr:
                findlst.append(i)
                total += 1
        return findlst,total
    
    def append(self,appendstr):
        self.__operationstr += appendstr
        
    def insert(self,pos,insertstr):
        self.__operationstr = self.__operationstr[:pos] + insertstr + self.__operationstr[pos:]
        
    def add(self,addstr):
        self.__operationstr = addstr + self.__operationstr
        
    def delete(self,pos,len=1):
        self.__operationstr = self.__operationstr[:pos] + self.__operationstr[pos+len:]
            
    def pop(self,len=1):
        if len > 1:
            pop = self.__operationstr[-1-len:-1]
            self.__operationstr = self.__operationstr[:-1-len]   
            return pop
        elif len==1:
            pop = self.__operationstr[-1]
            self.__operationstr = self.__operationstr[:-1]
            return pop
        
    def count(self,countstr):
        return self.find(countstr)[1]
    
    def reverse(self):
        newstr = ''
        i = len(self.__operationstr)-1
        while i != -1:
            newstr += self.__operationstr[i]
            i -= 1
        self.__operationstr = newstr
        
    def chartotal(self,start=0,end=-1):
        sum = 0
        for i in self.__operationstr[start:len(self.__operationstr) if end==-1 else end]:
            sum += ord(i)
        return sum
    
    def dateformat(self,formatchar='-',timechar=':'):
        if self.__operationstr == "".join(self.split()):
            return False
        else:
            datelst = self.split()
        if len(datelst) == 3:
            return "{}".format(formatchar).join(datelst)
        elif len(datelst) > 3 and  timechar != None:
            return "{}".format(formatchar).join(datelst[:3]) + " " + "{}".format(timechar).join(datelst[3:])
