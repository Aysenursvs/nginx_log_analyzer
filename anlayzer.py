from datetime import datetime, timedelta
from variables import bot_risk_score, suspicious_risk_score, rate_limit_risk_score

def is_bot_by_user_agent(user_agents: list[str]) -> bool:
    known_bots_pharases = ["bot", "crawl", "spider", "slurp", "archive", "checker"]

    for user_agent in user_agents:
        lower_user_agent = user_agent.lower()
        for phrase in known_bots_pharases:
            if phrase in lower_user_agent:
                return True
    return False

def check_request_count(ip_data: dict, threshold: int = 10000) -> bool:
    return ip_data.get("request_count", 0) > threshold

def is_rate_limit_exceeded(ip_data: dict, window_sec: int = 60, max_requests: int = 100) -> bool:
    now = datetime.now()
    recent_requests = [t for t in ip_data["request_times"] if now - t <= timedelta(seconds=window_sec)]
    return len(recent_requests) >= max_requests

# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
######   Eklenen Risk Skorlar değişiklik gösterebilir ya da bir değişkene atanıp o değişken değerleri kullanılabilir.
def is_unknown_or_weird_user_agent(ua: str) -> bool:
    ua = ua.strip()
    if ua == "" or ua == "-":
        return True
    if len(ua) < 10:
        return True
    if not any(c.isalpha() for c in ua):  # hiç harf içermiyorsa
        return True
    return False

def calculate_bot_risk(ip_data):
    known_safe_bots = ["google", "bing", "yandex", "baiduspider"]
    suspicious_agents = ["python", "curl", "wget", "requests", "scrapy", "aiohttp"]

    user_agents = ip_data.get("user_agents", [])
    risk = 0
    has_tool = False
    has_unknown_bot = False
    has_safe_bot = False
    has_weird_ua = False

    for ua in user_agents:
        ua_lower = ua.lower()

        if any(bot in ua_lower for bot in known_safe_bots):
            has_safe_bot = True
        elif any(tool in ua_lower for tool in suspicious_agents):
            has_tool = True
        elif "bot" in ua_lower or "spider" in ua_lower or "crawl" in ua_lower:
            has_unknown_bot = True
        elif is_unknown_or_weird_user_agent(ua_lower):
            has_weird_ua = True

    if has_tool:
        risk += 40
    if has_unknown_bot:
        risk += 25
    if has_safe_bot:
        risk += 10
    if has_weird_ua:
        risk += 20
    if len(user_agents) > 10:
        risk += 15  # Çok fazla çeşitlilik

    return risk




def calculate_suspicious_risk_by_request_count(ip_data) -> int:
    count = ip_data.get("request_count", 0)
    if count < 1000:
        return 0
    elif count < 5000:
        return 10
    elif count < 10000:
        return 20
    else:
        return 40
    
def calculate_suspicious_risk_by_suspicious_flag(ip_data) -> int:
    if ip_data.get("is_suspicious", False):
        return 30
    return 0

def calculate_rate_limit_risk(ip_data) -> int:
    if ip_data["is_limit_exceeded"]:
        return 30
    return 0

def calculate_prefix_risk(ip_data, prefix_counter, prefix_threshold=500, high_risk_score=10):
    prefix_count = prefix_counter.get(ip_data.get("prefix"), None)
    if ip_data.get("request_count") != prefix_count and prefix_count  > prefix_threshold:
        return high_risk_score
    return 0

def calculate_location_risk(ip_data):
    country = ip_data.get("country")
    suspicious_flag = ip_data.get("is_suspicious", False)

    # Suspicious flag True değilse, lokasyona göre risk ekleme
    if not suspicious_flag:
        return 0

    # Lokasyon verisi yoksa (geolocation başarısız)
    if country is None or country.strip() == "":
        return 20

    # Şüpheli ülkeler listesi
    suspicious_countries = ["RU", "CN", "KP", "IR", "NG", "BR", "VN"]

    if country in suspicious_countries:
        return 25
    else:
        return 0



def calculate_risk_score(ip_data, prefix_counter= None):
    bot_risk = calculate_bot_risk(ip_data)
    suspicious_risk = calculate_suspicious_risk_by_suspicious_flag(ip_data)
    rate_limit_risk = calculate_rate_limit_risk(ip_data)
    location_risk = calculate_location_risk(ip_data)
    prefix_risk = 0

    if prefix_counter is not None:
        prefix_risk = calculate_prefix_risk(ip_data, prefix_counter)

    ip_data["risk_components"]["bot"] = bot_risk
    ip_data["risk_components"]["suspicious"] = suspicious_risk
    ip_data["risk_components"]["rate_limit"] = rate_limit_risk
    ip_data["risk_components"]["prefix"] = prefix_risk
    ip_data["risk_components"]["location"] = location_risk

    ip_data["risk_score"] = bot_risk + suspicious_risk + rate_limit_risk + prefix_risk + location_risk

