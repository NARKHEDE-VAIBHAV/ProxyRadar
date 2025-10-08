
# 🛰️ ProxyRadar

**ProxyRadar** is a simple Python tool to find **working proxies** and save them in `active_proxies.txt`.

---

## 🚀 How to Run

```bash
git clone https://github.com/NARKHEDE-VAIBHAV/ProxyRadar
cd ProxyRadar
python3 run.py
````

After running, working proxies will be saved in `active_proxies.txt`.

---

## 📝 What ProxyRadar Does

* Reads candidate proxies from `proxies_list` in `run.py`
* Tests each proxy for connectivity
* Saves **working proxies** in `active_proxies.txt`
* Prints a console summary with counts and stats

---

## 🔧 Supported Proxy Formats

* `http://IP:PORT`
* `https://IP:PORT`
* `socks5://IP:PORT`
* `socks4://IP:PORT`

Example:

```python
proxies_list = [
    "http://46.101.92.46:3128",
    "http://91.103.120.49:443",
    "socks5://43.163.85.187:1080",
    "http://119.148.39.241:2727",
    "http://47.238.223.95:3128",
]
```

---

## ⚙️ Requirements

* Python 3.8+
* Install packages:

```bash
pip install requests pysocks tqdm
```

---

## 🔧 Config Options (`run.py`)

* `proxies_list` → list of candidate proxies
* `TEST_URL` → URL used to test proxies (use your own echo server for best results)
* `TIMEOUT` → per-proxy timeout (seconds)
* `MAX_WORKERS` → concurrency level for testing

---

## 📤 Output

* `active_proxies.txt` → validated proxies (one per line)
* Console summary:

  * Total candidates
  * Number of working proxies
  * Duration of the run

---

## 💡 Tips

* Pre-filter candidates: remove private IPs, duplicates, and malformed entries
* Use a TCP probe first to drop dead proxies quickly
* Host your own echo server to avoid public rate-limits
* Increase `TIMEOUT` if proxies are slow
* Tune `MAX_WORKERS` based on your system

---

## ⚠️ Legal & Security

* Never send passwords or sensitive info through unknown proxies
* Do not perform unauthorized scanning, attacks, or spamming
* Use only for **research, testing, or permissioned scenarios**

---

## 🌟 Optional Enhancements

* Save latency and response codes to CSV
* Add anonymity checks
* Retry logic with exponential backoff
* Geolocation or ASN filtering

---
