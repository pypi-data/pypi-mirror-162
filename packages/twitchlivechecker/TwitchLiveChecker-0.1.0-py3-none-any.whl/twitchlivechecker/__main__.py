import time
import requests
from bs4 import BeautifulSoup
from .config import getfollows

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }
URL = "https://www.twitch.tv/"
ISLIVE = "\"isLiveBroadcast\":true"

follows = getfollows()

def main():
    """Main function of the."""
    for s in follows:
        streamer = s.strip()
        print("Now checking: "+streamer)
        r = requests.get(URL+streamer, headers=headers)
        if r.status_code != 200:
            print("Status code: "+r.status_code)
            print("Exiting...")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        js_string = soup.script.string
        if ISLIVE in js_string:
            print(streamer+" is live!")
        else:
            print(streamer+" is offline.")

        time.sleep(3)

if __name__ == "__main__":
    main()
