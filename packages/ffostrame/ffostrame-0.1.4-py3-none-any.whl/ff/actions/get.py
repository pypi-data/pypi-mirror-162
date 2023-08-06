import logging
import tabulate
import pprint
import rich_click as click


@click.group(help="Get something")
@click.pass_obj
@click.pass_context
def get(ctx, profile):

    profiles_dict = ctx
    ctx.obj = profiles_dict.obj
    pass


@get.command(help="Get news via NewAPI")
#TODO Make this better and reusable
@click.option("--log-level", required=True, default="info", help="Logging level")
@click.pass_obj
def news(ctx, log_level):

    # do something with context if needed in near future
    # print(ctx)

    logging.basicConfig(level=log_level.upper())

    from utils.utils import Utils
    from lib.news import News

    news = News()
    utils = Utils()

    news_category_list = news.get_news_categories()
    logging.debug("News category list: %s", news_category_list)
    articles_list = news.get_news_by_categories(news_category_list['category'])
    print_list = []
    print_header = ['Title', 'URL']
    menu_list = []
    menu_dict = {}
    for article in articles_list:
        logging.debug(article)
        print_list.append([ article['title']])
        menu_list.append({'name': article['title']})
        menu_dict[article['title']] = {
            'url': article['url']
        }

    news.open_article_from_checkbox(menu_list, menu_dict)