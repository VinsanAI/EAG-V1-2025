import asyncio

async def risky_operation(task_id: int, delay: float) -> None:
    """A function that might raise an error"""
    try:
        print(f"\nTask {task_id}: Starting risky operation")

        # Simulate an error for task 2
        if task_id == 2:
            print(f"Task {task_id}: failed")
            raise ValueError(f"Task {task_id} failed!")

        print(f"Task {task_id}: Operation completed successfully\n")

    finally:
        print(f"Task {task_id} cleanup completed successfully")

async def main():
    try:
        print("starting main function...")

        # Create three tasks with different delays
        tasks = [
            asyncio.create_task(risky_operation(1,2)),
            asyncio.create_task(risky_operation(2,1)), # This one will fail
            asyncio.create_task(risky_operation(3,3))
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    finally:
        print("Main function cleanup - always executes!")

if __name__ == "__main__":
    asyncio.run(main())