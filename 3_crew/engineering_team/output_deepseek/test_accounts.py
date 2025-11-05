import unittest
from unittest.mock import patch
from accounts import Account, get_share_price

class TestAccount(unittest.TestCase):
    def setUp(self):
        """Set up a new account before each test."""
        self.account = Account("test_user")
    
    def test_init(self):
        """Test account initialization."""
        self.assertEqual(self.account.user_id, "test_user")
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
    
    def test_deposit_funds_success(self):
        """Test successful deposit of funds."""
        self.account.deposit_funds(100.0)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.transactions, [("deposit", 100.0)])
    
    def test_deposit_funds_negative(self):
        """Test deposit with negative amount raises error."""
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-50.0)
    
    def test_deposit_funds_zero(self):
        """Test deposit with zero amount raises error."""
        with self.assertRaises(ValueError):
            self.account.deposit_funds(0.0)
    
    def test_withdraw_funds_success(self):
        """Test successful withdrawal of funds."""
        self.account.deposit_funds(100.0)
        self.account.withdraw_funds(50.0)
        self.assertEqual(self.account.balance, 50.0)
        self.assertEqual(self.account.transactions, [("deposit", 100.0), ("withdrawal", 50.0)])
    
    def test_withdraw_funds_negative(self):
        """Test withdrawal with negative amount raises error."""
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-50.0)
    
    def test_withdraw_funds_zero(self):
        """Test withdrawal with zero amount raises error."""
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(0.0)
    
    def test_withdraw_funds_insufficient(self):
        """Test withdrawal with insufficient balance raises error."""
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(150.0)
    
    @patch("accounts.get_share_price")
    def test_buy_shares_success(self, mock_get_price):
        """Test successful purchase of shares."""
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(100.0)
        self.account.buy_shares("AAPL", 5)
        self.assertEqual(self.account.balance, 50.0)
        self.assertEqual(self.account.holdings, {"AAPL": 5})
        self.assertEqual(self.account.transactions[1], ("buy", "AAPL", 5, 50.0))
    
    def test_buy_shares_negative_quantity(self):
        """Test buy with negative quantity raises error."""
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -5)
    
    def test_buy_shares_zero_quantity(self):
        """Test buy with zero quantity raises error."""
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 0)
    
    @patch("accounts.get_share_price")
    def test_buy_shares_insufficient_funds(self, mock_get_price):
        """Test buy with insufficient funds raises error."""
        mock_get_price.return_value = 30.0
        self.account.deposit_funds(100.0)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 5)  # Costs 150, but balance is 100
    
    @patch("accounts.get_share_price")
    def test_sell_shares_success(self, mock_get_price):
        """Test successful sale of shares."""
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(100.0)
        self.account.buy_shares("AAPL", 5)  # Costs 50
        
        # Now sell with a different price
        mock_get_price.return_value = 12.0
        self.account.sell_shares("AAPL", 3)
        
        self.assertEqual(self.account.balance, 86.0)  # 50 + (3 * 12)
        self.assertEqual(self.account.holdings, {"AAPL": 2})
        self.assertEqual(self.account.transactions[2], ("sell", "AAPL", 3, 36.0))
    
    @patch("accounts.get_share_price")
    def test_sell_shares_all(self, mock_get_price):
        """Test selling all shares removes the symbol from holdings."""
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(100.0)
        self.account.buy_shares("AAPL", 5)  # Costs 50
        self.account.sell_shares("AAPL", 5)  # Sells all
        
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.holdings, {})
    
    def test_sell_shares_negative_quantity(self):
        """Test sell with negative quantity raises error."""
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -5)
    
    def test_sell_shares_zero_quantity(self):
        """Test sell with zero quantity raises error."""
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 0)
    
    def test_sell_shares_insufficient(self):
        """Test sell with insufficient shares raises error."""
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 5)  # No shares owned
    
    @patch("accounts.get_share_price")
    def test_get_portfolio_value(self, mock_get_price):
        """Test portfolio value calculation."""
        # Set up the account with some assets
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(100.0)
        self.account.buy_shares("AAPL", 5)  # Costs 50
        
        # Now change prices for valuation
        def side_effect(symbol):
            prices = {"AAPL": 12.0}
            return prices.get(symbol, 0.0)
        
        mock_get_price.side_effect = side_effect
        
        # Balance is 50, and AAPL is worth 12*5 = 60
        self.assertEqual(self.account.get_portfolio_value(), 110.0)
    
    @patch("accounts.get_share_price")
    def test_get_profit_or_loss(self, mock_get_price):
        """Test profit/loss calculation."""
        # Set up the account with some assets and transactions
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(100.0)
        self.account.buy_shares("AAPL", 5)  # Costs 50
        self.account.withdraw_funds(20.0)  # Withdraw some funds
        
        # Now change prices for valuation
        def side_effect(symbol):
            prices = {"AAPL": 12.0}
            return prices.get(symbol, 0.0)
        
        mock_get_price.side_effect = side_effect
        
        # Deposits - withdrawals = 100 - 20 = 80
        # Portfolio value = 30 (balance) + 60 (shares) = 90
        # Profit/loss = 90 - 80 = 10
        self.assertEqual(self.account.get_profit_or_loss(), 10.0)
    
    @patch("accounts.get_share_price")
    def test_get_holdings(self, mock_get_price):
        """Test getting current holdings."""
        mock_get_price.return_value = 10.0
        self.account.deposit_funds(200.0)
        self.account.buy_shares("AAPL", 5)
        self.account.buy_shares("GOOGL", 3)
        
        expected_holdings = {"AAPL": 5, "GOOGL": 3}
        self.assertEqual(self.account.get_holdings(), expected_holdings)
    
    def test_get_transactions(self):
        """Test getting transaction history."""
        self.account.deposit_funds(100.0)
        self.account.withdraw_funds(30.0)
        
        expected_transactions = [("deposit", 100.0), ("withdrawal", 30.0)]
        self.assertEqual(self.account.get_transactions(), expected_transactions)
    
    def test_get_share_price(self):
        """Test the get_share_price function."""
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 750.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)
        self.assertEqual(get_share_price("UNKNOWN"), 0.0)

if __name__ == "__main__":
    unittest.main()