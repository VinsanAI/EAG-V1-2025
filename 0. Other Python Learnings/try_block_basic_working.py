try:
    x = 10/0 # This will cause the ZeroDivisionError
except ZeroDivisionError:
    print("Cannot be divided by Zero!")
finally:
    print("This always runs.")