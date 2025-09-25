import asyncio
from src.services.linkace_client import LinkAceClient
import json
import httpx

async def main():
    client = LinkAceClient(
        base_url="http://localhost:8080",
        api_key="1|aGNSmJmVYfGoaDASG8EszXD8W57z98oI8aePgnNlb0c6a29c"
    )
    
    try:
        # List bookmarks
        response = await client.list_bookmarks(per_page=10)
        print("\nListing bookmarks:")
        print(json.dumps(response, indent=2))
        
        if response.get('data'):
            # Get the first link's ID
            first_link = response['data'][0]
            link_id = first_link['id']
            
            print(f"\nUpdating link {link_id} with 'dead' tag...")
            try:
                update_response = await client.update_link(
                    link_id=link_id,
                    tags=['dead'],
                    status=0  # 0 = dead, 1 = working
                )
                print("\nUpdate response:")
                print(json.dumps(update_response, indent=2))
            except httpx.HTTPError as e:
                print(f"\nHTTP Error: {str(e)}")
                print(f"Response status: {e.response.status_code if hasattr(e, 'response') else 'No status'}")
                print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No content'}")
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())