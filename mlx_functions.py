import os
import dotenv
import requests
import hashlib
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.firefox.options import Options

dotenv.load_dotenv()
mlx_email_address = os.getenv("MLX_EMAIL")
mlx_password = os.getenv("MLX_PASSWORD")
folder_id = os.getenv("FOLDER_ID")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def signin() -> str:
    url = "https://api.multilogin.com/user/signin"
    payload = {
        "email": f"{mlx_email_address}",
        "password": hashlib.md5(mlx_password.encode()).hexdigest()
    }
    r = requests.post(url=url, headers=HEADERS, json=payload)
    if r.status_code != 200:
        print("Wrong credentials")
    else:
        json_response = r.json()
        token = json_response['data']['token']
        return token
    
def create_profile(token: str, proxy: list, index: int, extension_paths: list, browser_type="mimic") -> str:
    HEADERS.update({
    "Authorization": f"Bearer {token}"
    })

    payload = {
    "browser_type": browser_type,
    "folder_id": folder_id,
    "name": f"Profile number {index + 1}",
    "os_type": "windows",
    "proxy": {
        "host": proxy["host"],
        "type": proxy["type"],
        "port": proxy["port"],
        "username": proxy["username"],
        "password": proxy["password"]
    },
    "parameters": {
        "fingerprint": {
            "cmd_params": {
                "params": [
                    {
                        "flag": "load-extension",
                        "value": f"{','.join(extension_paths)}"
                    }
                ]
            }
        },
        "flags": {
            "audio_masking": "mask",
            "fonts_masking": "mask",
            "geolocation_masking": "mask",
            "geolocation_popup": "prompt",
            "graphics_masking": "mask",
            "graphics_noise": "mask",
            "localization_masking": "mask",
            "media_devices_masking": "mask",
            "navigator_masking": "mask",
            "ports_masking": "mask",
            "proxy_masking": "custom",
            "screen_masking": "mask",
            "timezone_masking": "mask",
            "webrtc_masking": "mask"
        },
        "storage": {
            "is_local": False,
            "save_service_worker": False
        }
    }
    }

    url = "https://api.multilogin.com/profile/create"
    response = requests.post(url=url,headers=HEADERS, json=payload)

    if (response.status_code != 201):
        message = response.json()['status']['message']
        profile_id = False
        return profile_id, message
    else:
        profile_id = response.json()['data']['ids'][0]
        message = response.json()['status']['message']
        return profile_id, message

def start_profile(token: str, profile_id: str) -> str:
    HEADERS.update({
        "Authorization": f"Bearer {token}"
    })

    url = f"https://launcher.mlx.yt:45001/api/v2/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium&headless_mode=false"
    response = requests.get(url=url, headers=HEADERS)
    if response.status_code != 200:
        message = response.json()['status']['message']
        profile_port = False
        profile_started = False
        print(f"Error at starting profile: {message}")
        return profile_port, profile_started
    else:
        profile_port = response.json()['data']['port']
        profile_started = True
        return profile_port, profile_started

def stop_profile(profile_id: str, token: str) -> str:
    HEADERS.update({
        "Authorization": f"Bearer {token}"
    })
    url = f"https://launcher.mlx.yt:45001/api/v1/profile/stop/p/{profile_id}"
    r = requests.get(url=url, headers=HEADERS)
    if r.status_code != 200:
        print("Can't stop profile")
    else:
        print("Profile stopped")

def instantiate_driver(profile_port: str, browser_type="mimic") -> webdriver:
    if browser_type == 'mimic':
        driver = webdriver.Remote(command_executor=f"http://127.0.0.1:{profile_port}", options=ChromiumOptions())
    elif browser_type == 'stealthfox':
        driver = webdriver.Remote(command_executor=f"http://127.0.01:{profile_port}", options=Options())
    return driver