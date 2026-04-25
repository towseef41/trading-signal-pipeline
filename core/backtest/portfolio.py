class Portfolio:
    """
    Tracks capital and updates based on trades.
    """

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.capital = initial_capital

    def update(self, pnl: float):
        self.capital += pnl

    def current_value(self, unrealized_pnl: float = 0.0):
        return self.capital + unrealized_pnl