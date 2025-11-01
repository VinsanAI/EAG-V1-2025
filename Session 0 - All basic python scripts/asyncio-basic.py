import time
import asyncio

async def say_hello():
    await asyncio.sleep(2)
    print("Hello, World!")

async def say_good_bye():
    await asyncio.sleep(2)
    print("Good Bye, World!")

async def main():
    start_time = time.time()

    # Run both functions concurrently
    await asyncio.gather(say_hello(), say_good_bye())

    total_time = time.time() - start_time
    print(f"Total time taken: {total_time:.2f} seconds")

# Run the main function
asyncio.run(main())