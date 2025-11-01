import asyncio
import code

async def print_with_delay(message: str, delay: float) -> None:
    """print a message with a specified delay"""
    print(f"Starting {message}...")
    await asyncio.sleep(delay)
    print(f"Finished {message} after {delay:.2f} seconds")

async def main():
    # Create multiple tasks that run concurrently
    print("Starting main function...")

    # Create tasks with different delays
    task1 = asyncio.create_task(print_with_delay("Task 1", 2))
    task2 = asyncio.create_task(print_with_delay("Task 2", 1))
    task3 = asyncio.create_task(print_with_delay("Task 3", 3))
    code.interact(local=locals())

    # Wait for all tasks to complete
    await asyncio.gather(task1, task2, task3)

    print("All tasks completed")

# Run the asyncio program
if __name__ == "__main__":
    asyncio.run(main())