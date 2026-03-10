from scraper.scrapers.abercrombie import AbercrombieScraper
from scraper.scrapers.loft import LoftScraper
from scraper.scrapers.madewell import MadewellScraper
from scraper.scrapers.banana_republic import BananaRepublicScraper
from scraper.scrapers.jcrew import JCrewScraper
from scraper.scrapers.modcloth import ModClothScraper

# Active scrapers — confirmed working or likely to work without proxies
ALL_SCRAPERS = [
    AbercrombieScraper,
    LoftScraper,
    MadewellScraper,
    BananaRepublicScraper,
    JCrewScraper,
    ModClothScraper,
]

# Available but blocked without proxy rotation:
# AsosScraper, HMScraper, ZaraScraper,
# NordstromRackScraper, BloomingdalesScraper, AnthropologieScraper
