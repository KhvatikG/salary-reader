from dotenv import dotenv_values

try:
    from iiko_api import IikoApi
    
    config = dotenv_values(".env")
    
    # Check if all required configuration is present
    base_url = config.get("BASE_URL")
    login = config.get("IIKO_LOGIN")
    password = config.get("IIKO_PASS")
    
    if not all([base_url, login, password]):
        print("Warning: Missing iiko API configuration. Please create a .env file with BASE_URL, IIKO_LOGIN, and IIKO_PASS")
        iiko_api = None
    else:
        iiko_api = IikoApi(
            base_url=base_url,
            login=login,
            hash_password=password
        )
except Exception as e:
    print(f"Warning: Failed to initialize iiko_api: {e}")
    iiko_api = None

__all__ = ['iiko_api']
