from dotenv import dotenv_values

try:
    from iiko_api import IikoApi
    
    config = dotenv_values(".env")
    
    iiko_api = IikoApi(
        base_url=config.get("BASE_URL"),
        login=config.get("IIKO_LOGIN"),
        hash_password=config.get("IIKO_PASS")
    )
except Exception as e:
    print(f"Warning: Failed to initialize iiko_api: {e}")
    iiko_api = None

__all__ = ['iiko_api']
