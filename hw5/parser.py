import httpx
from bs4 import BeautifulSoup

SITEMAP_RU_ORIGINS = "https://minecraft.fandom.com/ru/sitemap-newsitemapxml-index.xml"
FILE_NAME = "dataset.txt"

def create_ul_text(content):
    text = ""
    rows = content.find_all("li")
    for i in range(len(rows)):
        if len(rows[i].text) > 20 and not rows[i].find("ul"):
            if len(rows[i].text) > 200:
                text += f"{i+1}. {rows[i].text[:200]}\n"
            else:
                text += f"{i+1}. {rows[i].text}\n"
    return text

def perform_url_scrapping(url):
    page = httpx.get(url)
    contents = BeautifulSoup(page.text).find_all(["p","ul"])
    pure_texts = []
    for i in range(len(contents)):
        if contents[i].name == "p" and contents[i+1].name == "ul":
            text = contents[i].text
            ul_text = create_ul_text(contents[i+1])
            pure_texts.append(text+ul_text)
        elif contents[i].name == "p" and len(contents[i].text) > 100:
            text = contents[i].text
            pure_texts.append(text)
    return pure_texts 
    # returns list of texts

def main():
    r = httpx.get(SITEMAP_RU_ORIGINS)
    f = open(FILE_NAME,"w",encoding="utf-8")
    f.write("<SEP>")
    if r.status_code != httpx.codes.OK:
        print("Unreachable sitemap origins")
        return
    try:
        bs_origin = BeautifulSoup(r.text,"xml")
        sitemaps = bs_origin.find_all("sitemap")
        if not sitemaps:
            print(f"Something wrong with sitemaps\nAdditional INFO:\nbs_origin: {bs_origin}\nresponse text:{r.text}")
        for sitemap in sitemaps:
            try: 
                r1 = httpx.get(sitemap.loc.text)
                print(f"USING SITEMAP\n{sitemap.loc.text}\nUSING SITEMAP")
                bs_cur = BeautifulSoup(r1.text,"xml")
                links = bs_cur.find_all("url")
                assert links, "Current sitemap has no links, is it right?"
            except KeyboardInterrupt:
                print("Parser Interrupted. Saving parsed data to file.")
                f.close()
                return
            except:
                print(f"ERROR while processing sitemap: {sitemap}")
            else:
                for link in links:
                    print(f"LINK: {link}")
                    try:
                        res = perform_url_scrapping(link.loc.text)
                    except KeyboardInterrupt:
                        print("Parser Interrupted. Saving parsed data to file.")
                        f.close()
                        return
                    except:
                        print(f"ERROR while scrapping {link.loc.text}")
                    else:
                        for text in res:
                            f.write(text)
                            f.write("<SEP>")
                        # здесь выполняем сохранение
                        # использовать сначала txt, потом Qdrant? или всё хранить в Qdrant?
    except KeyboardInterrupt:
        print("Parser Interrupted. Saving parsed data to file.")
    # except:
    #     print("Unexpected err with sitemaps parsing occured")
    finally:
        f.close()


if __name__ == "__main__":
    main()