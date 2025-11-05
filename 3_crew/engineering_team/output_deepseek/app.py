import gradio as gr
from accounts import Account, get_share_price

# Initialize a single account for the demo
user_account = None

def create_account(user_id):
    global user_account
    if not user_id.strip():
        return "Error: User ID cannot be empty.", None, None, None, None
    
    user_account = Account(user_id)
    return f"Account created for {user_id}", 0.0, {}, [], 0.0

def deposit(amount):
    if user_account is None:
        return "Error: Please create an account first.", None, None, None, None
    
    try:
        amount = float(amount)
        user_account.deposit_funds(amount)
        return f"Successfully deposited ${amount:.2f}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
    except ValueError as e:
        return f"Error: {str(e)}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()

def withdraw(amount):
    if user_account is None:
        return "Error: Please create an account first.", None, None, None, None
    
    try:
        amount = float(amount)
        user_account.withdraw_funds(amount)
        return f"Successfully withdrew ${amount:.2f}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
    except ValueError as e:
        return f"Error: {str(e)}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()

def buy_shares(symbol, quantity):
    if user_account is None:
        return "Error: Please create an account first.", None, None, None, None
    
    try:
        symbol = symbol.upper()
        quantity = int(quantity)
        price = get_share_price(symbol)
        
        if price == 0:
            return f"Error: Invalid symbol '{symbol}'", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
        
        user_account.buy_shares(symbol, quantity)
        return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
    except ValueError as e:
        return f"Error: {str(e)}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()

def sell_shares(symbol, quantity):
    if user_account is None:
        return "Error: Please create an account first.", None, None, None, None
    
    try:
        symbol = symbol.upper()
        quantity = int(quantity)
        price = get_share_price(symbol)
        
        if price == 0:
            return f"Error: Invalid symbol '{symbol}'", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
        
        user_account.sell_shares(symbol, quantity)
        return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()
    except ValueError as e:
        return f"Error: {str(e)}", user_account.balance, user_account.get_holdings(), user_account.get_transactions(), user_account.get_profit_or_loss()

def format_holdings(holdings):
    if not holdings:
        return "No holdings"
    
    result = ""
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        result += f"{symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    
    return result

def format_transactions(transactions):
    if not transactions:
        return "No transactions"
    
    result = ""
    for transaction in transactions:
        if transaction[0] == "deposit":
            result += f"Deposit: ${transaction[1]:.2f}\n"
        elif transaction[0] == "withdrawal":
            result += f"Withdrawal: ${transaction[1]:.2f}\n"
        elif transaction[0] == "buy":
            result += f"Buy: {transaction[2]} shares of {transaction[1]} for ${transaction[3]:.2f}\n"
        elif transaction[0] == "sell":
            result += f"Sell: {transaction[2]} shares of {transaction[1]} for ${transaction[3]:.2f}\n"
    
    return result

def get_portfolio_summary():
    if user_account is None:
        return "Error: Please create an account first.", None, None, None, None
    
    total_value = user_account.get_portfolio_value()
    profit_loss = user_account.get_profit_or_loss()
    
    status = f"Portfolio Value: ${total_value:.2f}\nProfit/Loss: ${profit_loss:.2f}"
    return status, user_account.balance, user_account.get_holdings(), user_account.get_transactions(), profit_loss

def check_prices(symbol=None):
    if symbol:
        symbol = symbol.upper()
        price = get_share_price(symbol)
        if price == 0:
            return f"Invalid symbol: {symbol}"
        return f"{symbol}: ${price:.2f}"
    else:
        prices = {
            "AAPL": get_share_price("AAPL"),
            "TSLA": get_share_price("TSLA"),
            "GOOGL": get_share_price("GOOGL")
        }
        result = ""
        for symbol, price in prices.items():
            result += f"{symbol}: ${price:.2f}\n"
        return result

with gr.Blocks(title="Trading Account Demo") as demo:
    gr.Markdown("# Trading Account Management Demo")
    
    with gr.Tab("Account Setup"):
        with gr.Row():
            user_id_input = gr.Textbox(label="User ID")
            create_account_btn = gr.Button("Create Account")
        
        account_status = gr.Textbox(label="Status", interactive=False)
        
        create_account_btn.click(
            create_account,
            inputs=[user_id_input],
            outputs=[account_status, account_balance, account_holdings, account_transactions, account_profit_loss]
        )
    
    with gr.Tab("Funds Management"):
        with gr.Row():
            deposit_amount = gr.Number(label="Deposit Amount")
            deposit_btn = gr.Button("Deposit")
            
        with gr.Row():
            withdraw_amount = gr.Number(label="Withdraw Amount")
            withdraw_btn = gr.Button("Withdraw")
            
        funds_status = gr.Textbox(label="Status", interactive=False)
        
        deposit_btn.click(
            deposit,
            inputs=[deposit_amount],
            outputs=[funds_status, account_balance, account_holdings, account_transactions, account_profit_loss]
        )
        
        withdraw_btn.click(
            withdraw,
            inputs=[withdraw_amount],
            outputs=[funds_status, account_balance, account_holdings, account_transactions, account_profit_loss]
        )
    
    with gr.Tab("Trade Shares"):
        with gr.Row():
            share_symbol = gr.Textbox(label="Share Symbol (e.g., AAPL, TSLA, GOOGL)")
            share_quantity = gr.Number(label="Quantity", precision=0)
        
        with gr.Row():
            buy_btn = gr.Button("Buy Shares")
            sell_btn = gr.Button("Sell Shares")
            
        with gr.Row():
            check_price_btn = gr.Button("Check Available Prices")
            
        trade_status = gr.Textbox(label="Status", interactive=False)
        price_info = gr.Textbox(label="Price Information", interactive=False)
        
        buy_btn.click(
            buy_shares,
            inputs=[share_symbol, share_quantity],
            outputs=[trade_status, account_balance, account_holdings, account_transactions, account_profit_loss]
        )
        
        sell_btn.click(
            sell_shares,
            inputs=[share_symbol, share_quantity],
            outputs=[trade_status, account_balance, account_holdings, account_transactions, account_profit_loss]
        )
        
        check_price_btn.click(
            check_prices,
            inputs=[],
            outputs=[price_info]
        )
    
    with gr.Tab("Account Summary"):
        refresh_btn = gr.Button("Refresh Account Summary")
        portfolio_summary = gr.Textbox(label="Portfolio Summary", interactive=False)
        
        account_balance = gr.Number(label="Cash Balance", interactive=False)
        account_holdings = gr.Textbox(label="Holdings", interactive=False, render=format_holdings)
        account_transactions = gr.Textbox(label="Transaction History", interactive=False, render=format_transactions)
        account_profit_loss = gr.Number(label="Profit/Loss", interactive=False)
        
        refresh_btn.click(
            get_portfolio_summary,
            inputs=[],
            outputs=[portfolio_summary, account_balance, account_holdings, account_transactions, account_profit_loss]
        )

if __name__ == "__main__":
    demo.launch()