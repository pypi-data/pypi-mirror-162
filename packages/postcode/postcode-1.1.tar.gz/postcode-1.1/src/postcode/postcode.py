def getPostcode(ville):
    url = "https://worldpostalcode.com/geocode"

    payload = "type=2&address=" + ville
    headers = {
        "authority": "worldpostalcode.com",
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://worldpostalcode.com",
        "referer": "https://worldpostalcode.com/lookup",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    
    return json.loads(response.text)["postcode"]
