import re

from .base import BaseAPI, HtmlTableParser
from .exceptions import SymbolNotFound


class FinViz(BaseAPI):
    """
    FinViz.com
    """

    def get_price_ratings(self):
        """
        Returns price ratings a.k.a price targets
        by analysts.

        Returned rows are:

        - date
        - status
        - analyst
        - rating
        - target price

        :return: Rows as a list of tuples where each tuple has 5 items.
        :rtype: list
        """

        try:
            html = self._get(
                f"https://finviz.com/quote.ashx?t={self.symbol.upper()}&ty=c&ta=1&p=d",
                headers={"User-Agent": self.user_agent},
            )
        except Exception as e:
            raise SymbolNotFound from e

        finds = re.findall(
            r"<td[^>]*fullview-ratings-inner[^>]*>(<table[^>]*>(?:.+?)<\/table>)",
            html.text,
            re.DOTALL,
        )
        rows = []

        for find in finds:
            parser = HtmlTableParser(columns=5)
            parser.feed(find)
            rows.extend(parser.get_data())

        return rows
