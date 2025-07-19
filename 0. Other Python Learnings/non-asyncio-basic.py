import time

def say_hello():
    time.sleep(2)
    print("Hello, World!")

def say_good_bye():
    time.sleep(2)
    print("Good Bye, World!")

start_time = time.time()
say_hello()
say_good_bye()
total_time = time.time() - start_time
print(f"Total time taken: {total_time:.2f} seconds")