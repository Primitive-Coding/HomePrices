from Scrapers.Zillow.zillow import Zillow


def test():

    t = ""

    f = t.split(" ")


if __name__ == "__main__":

    z = Zillow(city="Martinez", state="CA")
    # test()
    # z.scrape_page(page=20, export=True, overwrite=True)
    # z.test()
    z.compile_pages(export=True)
