import asyncio
from src.service import LinkAceSentry

async def main():
    service = LinkAceSentry()
    try:
        # Start the service
        await service.start()
        print("Service started, checking links...")
        
        # Run one check cycle
        await service.run_once()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())