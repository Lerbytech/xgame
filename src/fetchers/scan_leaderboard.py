import requests
import json
import os
import tqdm
import datetime
import time
from bs4 import BeautifulSoup
from src.account_loader import load_account_metadata
import re

universe_key = None
ACC = None

def get_m_for_s(v_value, s_list):
    global universe_key
    global ACC
    
    headers = {
        "User-Agent": ACC["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://xgame-online.com",
        "Connection": "keep-alive",
        "Referer": f"https://xgame-online.com/{universe_key}/index.php",
    }

    res = dict()
    
    for s_value in s_list:
        data = {
              "v": v_value,
              "s": s_value,
              "m": "1",
        }
        
        response = requests.post(f"https://xgame-online.com/{universe_key}/rating.php",
                                 headers=headers,
                                 cookies=ACC["cookies"],
                                 data=data)
        soup = BeautifulSoup(response.content)
        m_block = soup.find("select", {"id": "stata_type_m"})
        
        res[s_value] = list()
        for x in m_block.find_all("option"):
            if "value" in x.attrs:
                res[s_value].append(x["value"])
    return res

def scan_stats(v_value, cur_s_dict):
    global universe_key
    global ACC
    
    headers = {
        "User-Agent": ACC["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://xgame-online.com",
        "Connection": "keep-alive",
        "Referer": f"https://xgame-online.com/{universe_key}/index.php",
    }


    res = dict()
    
    m_for_s_values = get_m_for_s(1, list(cur_s_dict.keys()))
    cur_s = list(cur_s_dict.items())
    
    for s_value, s_label in cur_s:
        for m_value in tqdm.tqdm_notebook(m_for_s_values[s_value]):

            data = {
                    "v": v_value,
                    "s": s_value,
                    "m": m_value
            }

            response = requests.post(f"https://xgame-online.com/{universe_key}/rating.php",
                                     headers=headers,
                                     cookies=ACC["cookies"],
                                     data=data)
            soup = BeautifulSoup(response.content)

            good_rows = list()
            for tr in soup.find_all("tr"):
                if len(tr.find_all("th")) == 6:
                    good_rows.append(tr)
            res[f"{s_value}_{s_label}_{m_value}"] = good_rows
            time.sleep(1)
    
    return res

def cast_time(block):
    raw = str(block)
    
    if "Забанен" in raw:
        regex = r"[0-9]{2}.[0-9]{2}.[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"
        matches = re.finditer(regex, raw, re.MULTILINE)

        return {"ban_finish_time": datetime.datetime.strptime([m.group() for m in matches][0], "%d.%m.%y %H:%M:%S")}
    else:

        raw = raw.replace(":&lt;", "!").replace("&gt;", "!").replace("&lt;br","").replace("&lt;/td","")
        words = raw.split("!")
        timestr = words[7]
        timestr = "".join([ch for ch in timestr if ch.isdigit() or ch == " "])
        time_vals = [int(x) for x in timestr.split()]
        #print(time_vals)
        if len(time_vals) == 4:
            ts = 24 * 60 * 60 * time_vals[0] + 60 * 60 * time_vals[1] + 60 * time_vals[2] + time_vals[3]
        elif len(time_vals) == 3:
            ts = 60 * 60 * time_vals[0] + 60 * time_vals[1] + time_vals[2]
        elif len(time_vals) == 2:
            ts = 60 * time_vals[0] + time_vals[1]
        else:
            ts = time_vals[0]
        return {"seconds_since_beginning": ts}
    
def process_people_row(row, s_value):
    ths = row.find_all("th")    
    
    res = dict()
    res["place"] = int(ths[0].text)
    res["value"] = int(ths[-1].text.replace("\xa0", ""))
    
    if 1 <= s_value <= 5:
        res["shift"] = int(ths[1].text) if ths[1].text != "*" else 0
    elif 6 <= s_value <= 7:
        res["failures"] = int(ths[1].text)
    elif 8<= s_value <= 10:
        res["lvl"] = int(ths[1].text)
    elif s_value == 11:
        res["students"] = int(ths[1].text)
    else:
        pass
        
    a_block = ths[2].find("a")
    if a_block is None:
        res["id"] = None
    else:
        res["id"] = int(a_block["href"].split("=")[-1])

    span_blocks = ths[2].find_all("span")
    if len(span_blocks) == 0:
        res["status"] = None
        res["player"] = ths[2].text.replace("\xa0", "")
    else:
        temp = {x["class"][0] for x in span_blocks}
        res["status"] = ",".join(temp)
        if len(temp) > 1:
            time_dict = cast_time(span_blocks[1])
            for k,v in time_dict.items():
                res[k] = v


        pos = ths[2].text.rfind("(")
        res["player"] = ths[2].text[:pos].replace("\xa0", "")
    
    if s_value != 13:
        a_block = ths[4].find("a")
        if a_block is None:
            res["alliance_id"] = None
        else:
            res["alliance_id"] = int(a_block["href"].split("=")[-1])

    return res


def process_alliance_row(row, s_value):
    ths = row.find_all("th")    
    
    res = dict()
    res["place"] = int(ths[0].text)
    
    a_block = ths[2].find("a")
    res["id"] = int(a_block["href"].split("=")[-1])
    res["name"] = ths[2].text.replace("\xa0", "")
    
    if 1 <= s_value <= 5:
        res["shift"] = int(ths[1].text) if ths[1].text != "*" else 0
        res["n_players"] = int(ths[3].text.replace("\xa0", ""))
        res["avg"] = int(ths[4].text.replace("\xa0", ""))
        res["value"] = int(ths[5].text.replace("\xa0", ""))
        
    elif s_value == 6:
        temp = ths[1].text.split("/")
        res["wars_won"] = int(temp[0])
        res["wars_lost"] = int(temp[1])
        
        res["battles_won"] = int(ths[3].text.replace("\xa0", ""))
        res["difference"] = int(ths[4].text.replace("\xa0", ""))
        res["war_score"] = int(ths[5].text.replace("\xa0", ""))
    elif s_value == 7:
        res["n_oasises"] = int(ths[1].text)
        res["gain"] = int(ths[3].text.replace("\xa0", ""))
        res["holding_time"] = ths[4].text.replace("\xa0", "")

    return res


def fetch_leaderboard(account_login, universe_name):
    global universe_key
    global ACC
    
    ACC = load_account_metadata(account_login, universe_name)
    universe_key = ACC["universe_key"]
    
    player_s = {"1": "Очки",
                "2": "Флоты",
                "3": "Исследования",
                "4": "Сооружения",
                "5": "Оборона",
                "6": "Полеты",
                "7": "Экспедиции",
                "8": "Мирный опыт",
                "9": "Боевой опыт",
                "10": "Общий опыт",
                "11": "Наставники",
                "12": "Квесты",
                "13": "Призовой фонд"}

    alliance_s = {"1": "Очки",
                 "2": "Флоты",
                 "3": "Исследования",
                 "4": "Сооружения",
                 "5": "Оборона",
                 "6": "Войны",
                 "7": "Оазисы"}

    # ---
    
    STATS = scan_stats(1, player_s)
    final_player_dict = dict()
    for k,v in STATS.items():
        key = k.split("_")[1]
        final_player_dict[key] = list()

    for k,v in STATS.items():
        s = int(k.split("_")[0])
        key = k.split("_")[1]
        #print(s)
        final_player_dict[key].extend([process_people_row(vv, s) for vv in v])
    
    # -----
    STATS = scan_stats(2, alliance_s)
    final_alliance_dict = dict()
    for k,v in STATS.items():
        key = k.split("_")[1]
        final_alliance_dict[key] = list()

    for k,v in STATS.items():
        s = int(k.split("_")[0])
        key = k.split("_")[1]
        #print(s)
        final_alliance_dict[key].extend([process_alliance_row(vv, s) for vv in v])
        
    return final_player_dict, final_alliance_dict
    