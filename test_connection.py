import asyncio
from src.services.linkace_client import LinkAceClient
from src.config import settings

async def main():
    api = LinkAceClient(
        base_url=settings.linkace_base_url,
        api_key=settings.linkace_api_token
    )
    try:
        links = await api.list_bookmarks()
        print("Successfully connected to LinkAce API!")
        print(f"Found {len(links)} links:")
        for link in links:
            print(f"- {link['url']} ({link.get('title', 'No title')})")
    except Exception as e:
        print(f"Error connecting to LinkAce API: {e}")

if __name__ == "__main__":
    asyncio.run(main())