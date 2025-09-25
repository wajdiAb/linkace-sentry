import asyncio
from src.services.linkace_client import LinkAceClient

async def add_test_link():
    client = LinkAceClient(
        base_url="http://localhost:8080",
        api_key="1|aGNSmJmVYfGoaDASG8EszXD8W57z98oI8aePgnNlb0c6a29c"
    )
    
    # Add a link we know is dead
    link_data = {
        "url": "https://thiswebsitedefinitelydoesnotexist12345.com",
        "title": "Test Dead Link",
        "description": "This is a test link that should be detected as dead",
        "is_private": False,
        "check_disabled": False,
        "tags": [],
        "lists": []
    }
    
    try:
        # Create the link
        print("Adding test link...")
        response = await client.create_link(link_data)
        print("Test link added successfully!")
        print(response)
    except Exception as e:
        print(f"Error adding test link: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_test_link())