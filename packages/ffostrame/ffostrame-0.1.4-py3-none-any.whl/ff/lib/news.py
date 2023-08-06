import logging
import pprint


class News:
    def __init__(self):

        pass

    def get_news_categories(self, language="en"):

        from newsapi import NewsApiClient

        from utils.utils import Utils

        utils = Utils()

        newsapi = NewsApiClient(api_key="92e618ad50d14c27bc9ad8f048ab0948")
        sources = newsapi.get_sources()

        category_dict = {}
        category_list_for_menu = []
        for source in sources["sources"]:
            if source["language"] != language:
                continue
            if source["category"] not in category_dict:
                category_dict[source["category"]] = [source]
                category_list_for_menu.append({"name": source["category"]})

        categories_from_menu_list = utils.present_checkbox(category_list_for_menu)
        return categories_from_menu_list

    def get_news_by_categories(self, categories_list=["general"], language="en"):

        from newsapi import NewsApiClient

        from utils.utils import Utils

        newsapi = NewsApiClient(api_key="92e618ad50d14c27bc9ad8f048ab0948")

        articles_list = []

        for category in categories_list:

            logging.debug("Getting news stories for category %s", category)

            top_headlines = newsapi.get_top_headlines(
                category=category,
                language="en",
            )

            for article in top_headlines["articles"]:
                articles_list.append(article)

        return articles_list

    def open_article_from_checkbox(self, articles_list, articles_dict):

        import webbrowser

        from newsapi import NewsApiClient

        from utils.utils import Utils

        utils = Utils()

        articles_selected = utils.present_checkbox(articles_list)

        for article in articles_selected["category"]:
            webbrowser.open((articles_dict[article]['url']))
