import requests

NAS_URL = "https://192.168.1.132:5001"

url = f"{NAS_URL}/webapi/query.cgi"
params = {
    "api": "SYNO.API.Info",
    "version": "1",
    "method": "query",
    "query": "SYNO.API.Auth,SYNO.FileStation.List"
}

resp = requests.get(url, params=params, verify=False, timeout=10)
print(resp.status_code)
print(resp.text)