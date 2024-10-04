import asyncio
from module_7.utils.create_web_order_parcer import unregisterparcer, registerparcer

if __name__ == '__main__':
    asyncio.run(unregisterparcer())
    asyncio.run(registerparcer())
