from src.core.account_loader import load_account_metadata
import requests
import json
from copy import deepcopy

def process_g_key_raw(raw_text):
    pos_a = raw_text.find("{")
    assert pos_a != -1, "error - bad response text"
    res = json.loads(raw_text[pos_a:])
    # ---
    res["user"]["special"]["id"] = int(res["user"]["special"]["id"])
    res["user"]["place"] = int(res["user"]["place"])
    res["user"]["points"] = int(res["user"]["points"])
    res["user"].pop("avatar")
    res["user"].pop("dpath")
    res["user"].pop("img_planet")
    res["user"].pop("cookie")
    res["user"]["build_deff"] = int(res["user"]["build_deff"])
    
    res["user"]["allianceBonus"] = [int(x) for x in res["user"]["allianceBonus"]]
    res["user"]["oasisBonus"] = [int(x) for x in res["user"]["oasisBonus"]]
    
    res["user"]["currentPlanetID"] = int(res["user"]["currentPlanetID"])
    res["user"]["currentGalaxy"] = int(res["user"]["currentGalaxy"])
    res["user"]["currentSystem"] = int(res["user"]["currentSystem"])
    res["user"]["currentPlanet"] = int(res["user"]["currentPlanet"])
    res["user"]["currentType"] = int(res["user"]["currentType"])
    
    # -----
    for p in res["planets"]:
        p["id"] = int(p["id"])
        p["type"] = int(p["type"])
        p["temp"] = int(p["temp"])
        p.pop("image_old")
        p.pop("image")
        p.pop("x")
        p.pop("y")
        p["builds"] = int(p["builds"])
        
        p["buildings"] = [{"id": b["id"], "level": int(b["level"])} for b in p["buildings"] if b["id"] != 90]
        
        for flot in p["flotten"]:
            flot["amount"] = int(flot["amount"])
            
        for deff in p["defence"]:
            deff["amount"] = int(deff["amount"])

    # ----
    for tech in res["tech"]:
        tech["amount"] = int(tech["amount"])
        
    # ----
    for science in res["science"]:
        science["level"] = int(science["level"])
    
    # ----
    return res
    

def fetch_g_key_overview(account_login, universe_name):
    ACC = load_account_metadata(account_login, universe_name)
    universe_key = ACC["universe_key"]
    headers = {
        "User-Agent": ACC["user_agent"],
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": f"https://xgame-online.com/{universe_key}/",
    }

    try:
        response = requests.get(f"https://xgame-online.com/{universe_key}/sim.php", 
                                headers=headers, 
                                cookies=ACC["cookies"])
        if response.status_code == 200:
            res = process_g_key_raw(response.text)
            return True, res, None
        else:
            return False, [], response.status_code
    except Exception as e:
        return False, [], str(e)


if __name__ == "__main__":
    pass
