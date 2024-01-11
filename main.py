from ramler import RamblerPars
from correlation import Correlation


if __name__ == '__main__':
    parser = RamblerPars()
    parser.page_request()
    correlation = Correlation()
    correlation.correlation()
