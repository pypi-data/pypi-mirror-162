class Digit():
    def __init__(self):
        pass
    
    def plus(self,num1,num2):
        return num1+num2
    
    def minus(self,num1,num2):
        return num1-num2
    
    def mult(self,num1,num2):
        return num1*num2
    
    def div(self,num1,num2,reverse=False):
        return num1/num2 if not reverse else num2/num1
    
    def mod(self,num1,num2):
        return num1%num2
    
    def abs(self,num):
        return num if num>=0 else -num
    
    def opp(self,num):
        return -num
    
    def gcd(self,num1,num2):
        gcdlst = []
        for i in range(1,self.min(num1,num2)+1):
            if num1 % i == 0 and num2 % i == 0:
                gcdlst.append(i)
        return self.maxlst(gcdlst)
    
    def lcm(self,num1,num2):
        for i in range(self.max(num1,num2),num1*num2+1):
            if i % num1 ==0 and i % num2 ==0:
                return i
            
    def avg(self,lst):
        sum = 0
        for i in lst:
            sum += i
        return sum/len(lst)
    
    def max(self,num1,num2):
        return num1 if num1>num2 else num2
    
    def min(self,num1,num2):
        return num1 if num1<num2 else num2
        
    def sum(self,lst):
        sumn = 0
        for i in lst:
            sumn += i
        return sumn
    
    def square(self,num):
        return self.pow(num,2)
    
    def cube(self,num):
        return self.pow(num,3)
    
    def e(self,num):
        length = 0
        num = str(num)
        if num[0] == '-':
            new = '-{}.'.format(num[1])
        elif num[0].isdigit():
            new = '{}.'.format(num[0])
        for i in range(1 if num[0].isdigit else 2,len(num)):
            new += num[i]
            length += 1
        new += 'e+{}'.format(length)
        return new
    
    def pow(self,base,index):
        return 1 if not index else base * self.pow(base,index-1)
        
    def fac(self,facn):
        return 1 if facn==1 else facn * self.fac(facn-1)