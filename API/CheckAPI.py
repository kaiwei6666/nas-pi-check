import requests

url = "https://192.168.1.132:5001/webapi/query.cgi"
params = {
    "api": "SYNO.API.Info",
    "version": "1",
    "method": "query",
    "query": "SYNO.FileStation.CreateFolder,SYNO.FileStation.CopyMove,SYNO.FileStation.List"
}

resp = requests.get(url, params=params, verify=False)
print(resp.text)