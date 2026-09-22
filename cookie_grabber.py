import os
import json
from playwright.sync_api import sync_playwright

# Define paths (Adjust the username and profile name if necessary)
# Default profile is usually "Default". If you use a specific profile, change it.
LOCAL_APPDATA = os.getenv("LOCALAPPDATA")
EDGE_PROFILE_PATH = os.path.join(LOCAL_APPDATA, r"Microsoft\Edge\User Data")
PFSENSE_URL = "https://192.168.1.254"  # Replace with your pfSense URL

def automated_cookie_grabber():
    with sync_playwright() as p:
        print("[+] Launching Edge using your local profile...")
        
        # Launch Edge using your existing User Data directory
        # 'Default' is the standard profile. Use 'Profile 1', etc., if you use multiple profiles.
        context = p.chromium.launch_persistent_context(
            user_data_dir=EDGE_PROFILE_PATH,
            channel="msedge",
            headless=False,  # Set to False if you want to watch it work visually
            args=["--profile-directory=Default", "--ignore-certificate-errors"]
        )
        
        # Open a new page and navigate to your pfSense instance
        page = context.new_page()
        page.goto(PFSENSE_URL, wait_until="networkidle")
        
        # Extract all cookies currently active for the domain
        cookies = context.cookies(PFSENSE_URL)
        
        # Look for the pfSense session ID
        php_sessid = None
        for cookie in cookies:
            if cookie['name'] == 'PHPSESSID':
                php_sessid = cookie['value']
                break
        
        if php_sessid:
            print(f"[+] Found active session ID: {php_sessid}")
            
            # Save the session details or the entire cookie list to a file for your automation tools
            with open("pfsense_session.json", "w") as f:
                json.dump(cookies, f, indent=4)
            print("[+] Cookies successfully exported to 'pfsense_session.json'")
        else:
            print("[-] Could not find an active PHPSESSID. Are you logged in on Edge?")
            
        context.close()

if __name__ == "__main__":
    automated_cookie_grabber()
