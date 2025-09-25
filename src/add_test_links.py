import asyncio
from src.services.linkace_client import LinkAceClient

async def add_test_link():
    client = LinkAceClient(
        base_url="http://localhost:8080",
        api_key="1|aGNSmJmVYfGoaDASG8EszXD8W57z98oI8aePgnNlb0c6a29c"
    )
    
    # Update existing links to enable checking
    update_data = {
        "check_disabled": False
    }
    
    try:
        # Update all links to enable checking
        response = await client.list_bookmarks()
        for link in response.get('data', []):
            print(f"\nEnabling checks for link {link['id']}: {link['url']}...")
            await client.update_link(link['id'], check_disabled=False)
            print("Link updated!")
            
        # Add new test dead link
        dead_link = {
            "url": "https://thiswebsitewillfail123.com",
            "title": "Test Dead Link",
            "description": "This link should trigger a notification",
            "is_private": False,
            "check_disabled": False,  # Important: allow checking
            "tags": [],
            "lists": [],
            "status": 1  # Set as working initially
        }
        
        print("\nAdding new dead test link...")
        response = await client.create_link(dead_link)
        print("Link added successfully!")
        print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_test_link())