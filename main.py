from ramler import RamblerPars, data_input
from correlation import Correlation

# from sys import argv

# prog_name, days, pages, weeks = argv


if __name__ == '__main__':
    # days, pages, weeks = data_input()
    # parser = RamblerPars(days=int(days), pages=int(pages))
    # parser.page_request()
    # correlation = Correlation(k=int(weeks))
    correlation = Correlation(k=4)
    correlation.all_news_to_excel()
    correlation.all_percent_news_to_excel()
    correlation.all_dependency_news_to_excel()
    correlation.correlation()
