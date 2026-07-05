import subprocess
import os

# Run scraper if output does not exist 
if not os.path.exists("ScrapeOutput.json"):
    subprocess.run(["python", "scrapeV2.py"])

# Then run formatter
subprocess.run(["python", "formatScrape.py"])