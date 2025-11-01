from pdb import set_trace

x = 10
set_trace() #debugger starts here

y = 20
set_trace()

my_dict = {"a": 1, "b": 2, "c": 3}
set_trace()

def add(a, b):
    result = a + b
    return result

z = add(x, y)
print("result:", z)

# Comments on commands executed 
#  c  or  continue  	Resume execution until the next breakpoint
#  h  or  help  	Show available commands
#  s  or  step  	Execute the next line and step into functions
#  p variable  	Print the value of a variable ( p x  or just  x )
#  pp variable  	Pretty-print variable ( pp my_dict )
#  q  or  quit  	Quit the debugger and stop the execution
#  b 10  	Set a breakpoint at line 10
#  cl   	Clear all breakpoints

