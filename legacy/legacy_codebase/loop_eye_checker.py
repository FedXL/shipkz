import asyncio
from utils.eye_queue import main_loop_eye_checker

def main_eye():
    asyncio.run(main_loop_eye_checker())

if __name__ == '__main__':
    main_eye()
