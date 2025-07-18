import re
from datetime import datetime


def parse_log_line(line):
    """
    Parses a single line of the log file and extracts relevant information.
    
    :param line: A line from the log file
    :return: A dictionary containing the parsed information
    """
    # Example: 172.18.0.1 - - [14/Jul/2025:07:53:41 +0000] "GET /auth/login-page HTTP/1.1" 200 2104 "http://localhost/" "Googlebot/2.1 (+http://www.google.com/bot.html)"
    try:
        match = re.match(r'(\S+) - - \[([^\]]+)\] "([^"]+)" (\d+) (\d+) "([^"]*)" "([^"]*)"', line)
        if not match:
            return None
        ip = match.group(1)
        datetime_str = match.group(2).split(' ')[0]
        utc = match.group(2).split(' ')[1] if ' ' in match.group(2) else ''
        request = match.group(3)
        status = match.group(4)
        size = match.group(5)
        referer = match.group(6)
        user_agent = match.group(7)

        dt_obj = None
        try:
            dt_obj = datetime.strptime(datetime_str, "%d/%b/%Y:%H:%M:%S %z")  # offset'li dene
        except ValueError:
            try:
                dt_obj = datetime.strptime(datetime_str, "%d/%b/%Y:%H:%M:%S")  # offset'siz dene
            except ValueError:
                return None
        
        return {
            "ip": ip,
            "datetime": datetime_str,
            "datetime_obj": dt_obj,
            "utc": utc,
            "request": request,
            "status": status,
            "size": size,
            "referer": referer,
            "user_agent": user_agent
        }
    except ValueError:
        return None
