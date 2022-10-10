import json


class SymbolParser:
    def __init__(self):
        with open(r"C:\Users\evanh\Projects\AT\AT\symbol_info.json") as info:
            self.symbol_info = json.load(info)

    @staticmethod
    def split_symbol_source(symbol: str):
        """
        Splits symbol into data source, and symbol.
        Credit goes to jesse at https://github.com/jesse-ai/jesse.

        Parameters
        ----------
        symbol : str

        Returns
        -------
        tuple
            Contains data source and symbol string
        """
        return symbol.split("-")

    @staticmethod
    def key(source, base, quote=''):
        """
        Credit goes to jesse at https://github.com/jesse-ai/jesse.

        Parameters
        ----------
        data_source : str
        symbol : str
        """
        return "{}-{}{}".format(source, base, quote)
    
    def split_symbol(self, symbol, include_source=True):
        source, symbol = self.split_symbol_source(symbol)
        base = self.symbol_info[symbol]["baseAsset"]
        quote = self.symbol_info[symbol]["quoteAsset"]
        if not include_source:
            return base, quote
        return source, base, quote

