#.isempty function returns True or false , Must input a list and store return value in a variable in main code
def isempty(stk:list) -> bool:
    if not isinstance(stk, list):
        raise TypeError
    else:
        if stk == []:
            return True
        else:
            return False

#.push function returns the stack,top , Must input a list,an value to push in the stack  and store return value in a variable in main code
def push(stk:list, item:int) -> int:
    if not isinstance(stk, list):
        raise TypeError
    else:
        stk.append(item)
        top = len(stk) - 1
        print("SUCCESS")
        return stk,top

#.pop function prints the error(or) returns the stack,the removed item, The top .Must input a list and store return value in a variable in main code
def pop(stk:list): 
    if not isinstance(stk, list):
        raise TypeError
    else:
        if isempty(stk):
             print("UnderflowError")
        else:
            item = stk.pop()
            if len(stk) == 0:
                top = None
            else:
                top = len(stk) - 1
            return stk,top,item
            
#.peek function returns the error(or)top's value . Must input a list and store return value in a variable in main code
def peek(stk:list):
    if not isinstance(stk, list):
        raise TypeError
    else:
        if isempty(stk):
            return "UnderflowError"
        else:
            top = len(stk) - 1
            return stk[top]

#.display function returns the error(or)stack in order . Must input a list and direct exection in main code
def display(stk:list):
    if not isinstance(stk, list):
        raise TypeError
    else:
        if isempty(stk):
            print("stack is empty")
        else:
            top = len(stk) - 1
            print(stk[top], "<---top")
            for a in range(top - 1, -1, -1):
                print(stk[a])