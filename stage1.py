
import requests
from bs4 import BeautifulSoup
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
SCRAPED_FILE = "active_proxies.txt"


FREE_PROXY_URL = "https://free-proxy-list.net/en/"
PROXYSCRAPE_URL = (
    "https://api.proxyscrape.com/v4/free-proxy-list/get"
    "?request=displayproxies&protocol=http&timeout=10000"
    "&country=all&ssl=all&anonymity=all&skip=0&limit=100000"
)
GEONODE_URL = "https://proxylist.geonode.com/api/proxy-list"
PROXYSCRAPE_FORMATTED_URL = (
    "https://api.proxyscrape.com/v4/free-proxy-list/get"
    "?request=display_proxies&proxy_format=protocolipport&format=text"
)
PROXYDB_BASE = "https://proxydb.net/"

# New GitHub proxy lists
PROXIFLY_URL = "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/all/data.txt"
SPEEDX_HTTP_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
SPEEDX_SOCKS4_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"
SPEEDX_SOCKS5_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"

# ---------------- Scraping ----------------

def fetch_free_proxy_list():
    try:
        r = requests.get(FREE_PROXY_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print("free-proxy-list failed:", e)
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="table")
    proxies = []
    if table and table.tbody:
        for tr in table.tbody.find_all("tr"):
            cols = tr.find_all("td")
            if len(cols) >= 2:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                proxies.append(f"{ip}:{port}")
    return proxies

def fetch_proxyscrape():
    try:
        r = requests.get(PROXYSCRAPE_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
    except Exception as e:
        print("proxyscrape failed:", e)
        return []
    matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b", text)
    return list(dict.fromkeys(matches))

def fetch_geonode_page(page):
    url = f"{GEONODE_URL}?limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        data = r.json()
        proxies = [f"{i['ip']}:{i['port']}" for i in data.get("data", []) if i.get("ip") and i.get("port")]
        print(f"  geonode page {page} fetched {len(proxies)}")
        return proxies
    except Exception as e:
        print(f"  geonode page {page} failed:", e)
        return []

def fetch_geonode(max_pages=25, threads=10):
    all_proxies = []
    with ThreadPoolExecutor(max_workers=threads) as exe:
        futures = [exe.submit(fetch_geonode_page, p) for p in range(1, max_pages+1)]
        for f in as_completed(futures):
            all_proxies.extend(f.result())
    return all_proxies

def fetch_proxyscrape_formatted():
    try:
        r = requests.get(PROXYSCRAPE_FORMATTED_URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
        proxies = [line.strip() for line in text.splitlines() if line.strip()]
        return list(dict.fromkeys(proxies))
    except Exception as e:
        print("proxyscrape formatted API failed:", e)
        return []

def fetch_proxydb_page(offset):
    url = f"{PROXYDB_BASE}?offset={offset}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="table")
        proxies = []
        if table and table.tbody:
            for tr in table.tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    ip_tag = tds[0].find("a")
                    port_tag = tds[1].find("a")
                    if ip_tag and port_tag:
                        ip = ip_tag.get_text(strip=True)
                        port = port_tag.get_text(strip=True)
                        if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", ip) and re.match(r"^\d{1,5}$", port):
                            proxies.append(f"{ip}:{port}")
        else:
            matches = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b", r.text)
            proxies.extend(matches)
        print(f"  proxydb offset={offset} fetched {len(proxies)}")
        return proxies
    except Exception as e:
        print(f"  proxydb offset={offset} failed:", e)
        return []

def fetch_proxydb(max_offset=5500, step=30, batch_size=10, sleep_per_batch=10):
    offsets = list(range(0, max_offset + 1, step))
    all_proxies = []
    for i in range(0, len(offsets), batch_size):
        batch = offsets[i:i+batch_size]
        print(f"\nFetching batch offsets: {batch}")
        with ThreadPoolExecutor(max_workers=batch_size) as exe:
            futures = {exe.submit(fetch_proxydb_page, off): off for off in batch}
            for f in as_completed(futures):
                all_proxies.extend(f.result())
        print(f"Batch finished, sleeping {sleep_per_batch} seconds before next batch...")
        time.sleep(sleep_per_batch)
    return all_proxies

def fetch_github_list(url, name):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        text = r.text
        proxies = [line.strip() for line in text.splitlines() if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$", line.strip())]
        print(f"{name} fetched {len(proxies)} proxies")
        return proxies
    except Exception as e:
        print(f"{name} failed:", e)
        return []

def combine_and_save(*lists):
    seen = set()
    combined = []
    for lst in lists:
        for item in lst:
            it = item.strip()
            if it and it not in seen:
                seen.add(it)
                combined.append(it)
    with open(SCRAPED_FILE, "w") as f:
        f.write("\n".join(combined))
    print(f"\nSaved {len(combined)} unique proxies to {SCRAPED_FILE}")
    return combined

# ---------------- Testing ----------------
# (unchanged testing functions omitted for brevity)

# ---------------- Main ----------------

def main():
    print("Fetching proxies from all sources...\n")
    list1 = fetch_free_proxy_list()
    list2 = fetch_proxyscrape()
    list3 = fetch_geonode(max_pages=25, threads=10)
    list4 = fetch_proxyscrape_formatted()
    list5 = fetch_proxydb(max_offset=5500, step=30, batch_size=20)

    # New GitHub lists
    list6 = fetch_github_list(PROXIFLY_URL, "proxifly")
    list7 = fetch_github_list(SPEEDX_HTTP_URL, "speedx-http")
    list8 = fetch_github_list(SPEEDX_SOCKS4_URL, "speedx-socks4")
    list9 = fetch_github_list(SPEEDX_SOCKS5_URL, "speedx-socks5")
    
    all_proxies = combine_and_save(list1, list2, list3, list4, list5, list6, list7, list8, list9)
    
if __name__=="__main__":
    main()
