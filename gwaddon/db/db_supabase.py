from logging import getLogger, INFO
from supabase import create_client, Client
from supabase.client import ClientOptions

logger = getLogger(__name__)

url: str = "https://lfgtrzqxlvxfbzfrlczg.supabase.co"
api_key: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmZ3RyenF4bHZ4ZmJ6ZnJsY3pnIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NjM0MzcxNzAsImV4cCI6MTk3OTAxMzE3MH0.04oErHTJKzF3uOCR1vD1I5ESzVaky9imRHv2vKcLQy0"
)


def login(username: str, password: str):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"username": username, "password_hash": password},
        ),
    )

    response = supabase.table("gwaio_user").select("*").execute()
    if response.data:
        logger.debug(f"User {username} logged in successfully.")
        return response.data[0]
    raise Exception("Invalid username or password.")


def get_studio_data(token: str):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"token": token},
        ),
    )

    response = supabase.table("gwaio_studio").select("*").execute()
    if response.data:
        return response.data[0]["data"]
    raise Exception("Access was denied.")


def set_studio_data(key: str, token: str, data: dict[str, any]):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"token": token},
        ),
    )

    response = (
        supabase.table("gwaio_studio").update({"data": data}).eq("key", key).execute()
    )
    if response.data:
        return response.data[0]

    raise Exception("Failed to update data")


def add_user(token, data: dict[str, any]):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"token": token},
        ),
    )

    response = supabase.table("gwaio_user").insert(data).execute()
    if response.data:
        return response.data[0]

    raise Exception("Failed to add user")


def edit_user(token: str, user_id: int, data: dict[str, any]):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"token": token},
        ),
    )

    response = supabase.table("gwaio_user").update(data).eq("id", user_id).execute()
    if response.data:
        return response
    raise Exception("Failed to edit user")


def delete_user(token: str, user_id: int):
    supabase: Client = create_client(
        url,
        api_key,
        options=ClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema="public",
            headers={"token": token},
        ),
    )

    response = supabase.table("gwaio_user").delete().eq("id", user_id).execute()
    if response.data:
        return response

    raise Exception("Failed to delete user")


if __name__ in "__main__":
    user_data = login("e.aguado", "1234")
    edit_user("testfake", 104, {"active": True})
