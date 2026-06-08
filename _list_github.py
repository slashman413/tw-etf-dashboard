import json, ssl, urllib.request
PAT = "GITHUB_PAT_PLACEHOLDER"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
req = urllib.request.Request(
    "https://api.github.com/repos/slashman413/tw-etf-dashboard/contents?ref=main",
    headers={"Authorization":"token "+PAT,"Accept":"application/vnd.github.v3+json","User-Agent":"tw-etf/1.0"})
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    files = json.loads(r.read())
for f in sorted(files, key=lambda x: x["name"]):
    print(f["name"].ljust(30), f["type"].ljust(5), str(f["size"]//1024)+"KB")
