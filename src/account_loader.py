from pathlib import Path
import yaml
import os

"""
example of yaml file for user:

login: "login"
password: "password"
user_agent: ""
available_univerces:
- "x100"
- "x1000"
"x100":
    "universe_key": "uni26"
    "cookies":
        "PHPSESSID": "7gulb10uv2tts4v60dp00ap1"
        "uni26": "42F%2F%25%2F%2F%25%2F%2F%25%2F0%2F%25%2F%2F%25%2F0%2F%25%2F0%2F%25%2F0%2F%25%2F0%2F%25%2F1594494981"
        "xgame_referer": "%5B%23%5D%5B%23%5D%5B%23%5D"
"x1000":
    "universe_key": "uni33"
    "cookies":
        "PHPSESSID": "pleik4mooddh2qitrd1o5p60"
        "uni33": "%2F%2F%25%2F%2F%25%2F%2F%25%2F0%2F%25%2F%2F%25%2F0%2F%25%2F1%2F%25%2F0%2F%25%2F0%2F%25%2F1602238951"
        "xgame_referer": "%5B%23%5D%5B%23%5D%5B%23%5D"

"""

ACCOUNT_DATA_DIR = Path("accounts/")
def load_account_metadata(username, universe):
    filename = ACCOUNT_DATA_DIR / Path(f"{username}.yml")
    print(os.getcwd())
    assert filename.exists(), f"{filename} not found!"

    with filename.open("r") as f:
        whole_dict = yaml.safe_load(f)
    
    assert universe in whole_dict["available_univerces"]
    res_dict = dict()
    res_dict["login"] = whole_dict["login"]
    res_dict["password"] = whole_dict["password"]
    res_dict["user_agent"] = whole_dict["user_agent"]
    
    res_dict["cookies"] = whole_dict[universe]["cookies"]
    res_dict["universe_key"] = whole_dict[universe]["universe_key"]

    return res_dict
