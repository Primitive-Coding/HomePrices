from Scrapers.Zillow.zillow import Zillow


if __name__ == "__main__":

    z = Zillow(city="Martinez", state="CA")

    # z.scrape_page(page=6, export=True, overwrite=True)
    # z.test()
    z.compile_pages()
