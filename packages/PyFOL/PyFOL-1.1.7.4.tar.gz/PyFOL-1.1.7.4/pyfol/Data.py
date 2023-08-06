class Data():
    def __init__(self):
        pass
    
    def swap(self,var1,var2):
        return var2,var1
    
    def maxlst(self,lst):
        max = lst[0]
        for i in lst[1:]:
            if i > max:
                max=i
        return max
    
    def minlst(self,lst):
        min = lst[0]
        for i in lst[1:]:
            if i < min:
                min=i
        return min
            
    def randms(self,seed):
        seed **= 2
        return int(str(seed)[1:5])
    
    