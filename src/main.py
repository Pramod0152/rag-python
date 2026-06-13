import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.grpc_server import serve

if __name__ == "__main__":
    asyncio.run(serve())