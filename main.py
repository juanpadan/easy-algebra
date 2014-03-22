 #!/usr/bin/python
LETT="qwertyuiopasdfghjklzxcvbnm"
NUM="1234567890"

"""
this module provides a phraser that takes a string containing human 
readable expession and it simplifies it and turns it into a Polinomial
object that can be printed as a self compatible string

"""
import fractions
Frac = fractions.Fraction #shortcut


def multiply_vars(a,b,exp_a = 1,exp_b=1):
    """take to dictionaries containig variables (se Polinomial class)
    and multiply them, operands can be elevated to specified exponents
    returning new dictionary.
    Removes 0 exponents
    """
    out = {}
    for lett, exp in a.items():
        out.update({lett:exp*exp_a})
    
    for lett, exp in b.items():
        if lett not in out:
            out.update({lett:exp*exp_b})
        else:
            t = out[lett]
            out.update({lett:exp*exp_b+t})
    
    #remove letters with 0 exponent
    for lett,exp in out.items():
        if exp==0:
            del out[lett]            
    return out

def test_vars(a,b):
    """test dictionaries are equal"""
    #TODO verifica singolarita' di variabile
    if len(a)==len(b):
        out = True
        for i in range(len(a)):
            keys_a = sorted(a.keys())
            keys_b = sorted(b.keys())
            if keys_a[i]!=keys_b[i]:#if keys different
                out = False
                break
            elif a[keys_a[i]]!=b[keys_b[i]]:#if keys are equal test values
                out = False
                break
        return out
    else:#so len(a)!=len(b)
        return False


def read_monomial(exp):
    """takes a string (as those in tokenizer) and returns a monomial
    representation of the monomial string as a pair in the form:
    (Fraction(coefficent),{letter:exponent,...}"""
    exp = exp +"\n"
    num = "" #coefficent
    lett = {}
    i = 0
    
    while exp[i] in NUM:
        num+=exp[i]
        i+=1
    
    while exp[i] in LETT:
        var = exp[i]
        i+=1
        exponent = ""
        while exp[i] in NUM:
            exponent+= exp[i]
            i+=1
        if not exponent:
            exponent = "1"
        exponent = int(exponent)
        if var in lett.keys():
            exponent+=lett[var]
        lett.update({var:exponent})
    
    if lett and not num: #no coefficent was found but letters exist
        num = "1"
    elif not num and not num:
        num = "0"
    return (Frac(num),lett)

def simplify_polinomial(pol):
    l = list(pol)
    out = []
    while len(l)!=0:
        j = 0
        simile = False
        while j<len(out):
            simile = False
            if test_vars(out[j][1],l[0][1]):
                #^^^test monomials have the same literal
                v = out[j][0] #old coefficent
                out[j] = (v+l[0][0], l[0][1])
                simile = True
                l.pop(0)
                break
            j +=1
        if not simile:
            out.append(l[0])
            l.pop(0)
        
    no0 = []
    while len(out)>0:#eliminate 0 terms
        if out[0][0]!=0:
            no0.append(out[0])
        out.pop(0)
    return no0




class Polinomial:
    def __init__(self,val):
        if type(val)==type(str()):
            self.pol = solve(val)
        elif type(val)==type(list()):
            self.pol = list(val)
        else:
            raise(Exception("invalid argument type: "+str(type(val))))
            
    def __add__(self,other):
        return Polinomial(simplify_polinomial(self.pol+other.pol))
    
    def __sub__(self,other):
        out = list(self.pol)
        for frac,lett in other.pol:
            out.append((-frac,lett))
        return Polinomial(simplify_polinomial(out))
    
    def __mul__(self,other):
        out = []
        for f1,v1 in self.pol:
            for f2,v2 in other.pol:
                out.append((f1*f2,multiply_vars(v1,v2)))
        return Polinomial(out)
    
    def __div__(self,other):
        out = []
        for f1,v1 in self.pol:
            for f2,v2 in other.pol:
                out.append((f1/f2,multiply_vars(v1,v2,1,-1)))
        return Polinomial(out)
    
    
    def __str__(self):
        out = ""
        for frac, lett in self.pol:
            if frac>=0:
                tmp = "+"+str(frac)
            else: 
                tmp = str(frac)
            num = ""
            den = ""
            for var, exp in lett.items():
                if exp == 1:
                    num+=var
                elif exp == -1:
                    den+=var
                elif exp>1:
                    num+=var+str(exp)
                elif exp<-1:
                    den+=var+str(-1*exp)
            if den:
                den="/"+den
            out+=tmp+num+den
        return out
    
    def __repr__(self):
        return self.__str__()
            
def check_syntax(exp):
    """throws an expression on invalid syntax and prepares for tokenizer"""
    #FIXME very approximate and incomplete
    par = 0 
    out = ""
    implied_multiplication = False
    i = 0
    while i<len(exp):
        if exp[i] == "(":
            par += 1
            if i and exp[i-1] in LETT+NUM: #if i==0 don't check char at -1
                out+="*" #add implied multiplication
        elif exp[i] == ")":
            par -=1
            if len(exp)-(i+1) and exp[i+1] in LETT+NUM+"(":
                #don't check at len(exp)+1
                implied_multiplication = True
        if par == -1:
            raise SyntaxError("parenthesis not maching")
        
        if exp[i] in LETT+NUM+"()+*-/":
            out+=exp[i]        
            if implied_multiplication:
                out+="*"
                implied_multiplication = False
                
        elif exp[i] in " ":#ignore characters
            pass
        else:
            raise SyntaxError("invalid charecter: "+exp[i])
        i+=1
        
    if par != 0:
        raise SyntaxError("parenthesis not maching")
    return out
     
    
    
def group(index,string):
    """index and string such that string[index]=="("
    returns the cuple (new_index,string_in_parenthesis)
    where string_in_parenthesis[new_index-1] == ")"
    """   
    index+=1
    begin = index
    par = 1
    out = ""
    while par>0:
        
        if string[index]=="(":
            par +=1
        elif string[index]==")":
            par -=1
        index+=1
        
    return (index,string[begin:index-1])



def tokenize(exp):
    """from expression with correct syntax return a list of string 
    containing
    only Polinomials"""
    out = []
    tmp = ""
    i= 0
    while i<len(exp):
        
        if exp[i] in "+-*/":
            if tmp:#ignore when coming back from )
                out.append(Polinomial([read_monomial(tmp)]))
            out.append(exp[i])
            tmp = ""
            i+=1
        elif exp[i] == "(":
            i,sub = group(i,exp)
            out.append(solve(sub))
        else:
            tmp+=exp[i]
            i+=1
            
    if tmp:
        out.append(Polinomial([read_monomial(tmp)]))
    return out
    
def solve(exp):
    clean = check_syntax(exp)
    l = tokenize(clean)
    if l[0]=="-":
        out=Polinomial([])-l[1]
        i = 2
    else:
        out = l[0]
        i = 1
    while i<len(l):
        if l[i]=="+":
            out += l[i+1]
        elif l[i]=="-":
            out -= l[i+1]
        elif l[i]=="*":
            out *= l[i+1]
        elif l[i]=="/":
            out=/=l[i+1]
        else:
            raise Exception("unsupported operand: "+str(l[i]))
        i+=2
    return out
            

#DEBUG CODE
import code
import readline
import rlcompleter
#fine debug imports   
#avvia console
p = Polinomial #accesso piu' semplice al Polinomi

test = "3ab+c+d-(a+b/(a+b))-c+d"
print(check_syntax(test))
print(tokenize(check_syntax(test)))
print(solve(test))

vars = globals()
vars.update(locals())
readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)
shell.interact()    
    