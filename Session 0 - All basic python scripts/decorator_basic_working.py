def my_decorator(func):
    def wrapper():
        print("Before Function call")
        func() # Calling the original function
        print("After the function call")
    return wrapper

@my_decorator # Applying the decorator
def say_hello():
    print("Hello, World!")

say_hello()