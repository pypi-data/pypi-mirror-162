from absurdia.markets.abstract import MarketResource

class Price(MarketResource):
    OBJECT_NAME = "price"
    LATEST_PRICES = {}
    
    def __init__(self, symbol: str):
        super().__init__()
        Price.LATEST_PRICES[symbol] = self
        self.symbol = symbol

    def get(self):
        return self.get_(symbol=self.symbol)

def get_latest_price(symbol: str):
    return Price(symbol).get()