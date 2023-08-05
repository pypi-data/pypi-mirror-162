from mediawiki import DisambiguationError

from wikifaces.downloader import WikiFace

if __name__ == '__main__':
    wf = WikiFace()
    cats = ['David Wagner']
    pgs = []
    for cat in cats:
        try:
            pgs = wf.wikidata.page(title=cat, auto_suggest=False)
        except DisambiguationError as e:
            pages = wf.wikidata.opensearch(cat)
            pages = [page for page in pages if page[0] != cat]
            pgs = [page[0] for page in pages if ':' not in page[0]]
    print(pgs)