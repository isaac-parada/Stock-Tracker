from sqlite3 import OperationalError
from bs4 import BeautifulSoup
import requests
import sqlite3
from datetime import datetime
from tkinter import *

# Initiates Tkinter
root = Tk()

# Original URL
url = 'https://www.google.com/finance?q='

# Connect to the database and enable the cursor
conn = sqlite3.connect('data-stocks.db')
c = conn.cursor()

# 'Stock' Label for the entry widget
label_stock = Label(root, text='Stocks ')
label_stock.grid(row=0, column=0)

# Input the stocks into the Entry widget labeled 'Stocks'
users_stocks = Entry(root)
users_stocks.grid(row=0, column=1)

# 'Target price' Label for the entry widget
target_price_label = Label(root, text='Target Price')
target_price_label.grid(row=1, column=0)

# Input for the price the user wants the stock to reach
target_price = Entry(root)
target_price.grid(row=1, column=1)

# Enter Button, when clicked the inputs will be collected, and separated, then web scraped from 'Google.com/finance' using BeautifulSoup4. The values will then be added to the database.
button_enter = Button(root, text='Enter', command=lambda: search_it(users_stocks, target_price))
button_enter.grid(row=0, column=2)

# Show Button
button_show = Button(root, text='Show')
button_show.grid(row=1, column=2)


def search_it(STOCKS, TARGETPRICE):
    # Next button which allows users to see the next stock
    button_next = Button(root, text='Next')
    button_next.grid(row=2, column=2)

    # Scraped stock names are added to this list
    scraped_stock_name = []

    # Scraped prices are added to this list
    scraped_stock_price = []

    # User inputs stocks they want to search for, the input is then split
    users_stocks = str(STOCKS.get())
    stocks_split = users_stocks.split(',')
    print(stocks_split)

    # User inputs the target price they hope the stock reaches, the input is then split
    target_price = TARGETPRICE.get()
    target_price = target_price.split(',')
    print(target_price)

    # Show Button
    button_show = Button(root, text='Show', command=lambda: show_stocks())
    button_show.grid(row=1, column=2)

    def show_stocks():
        n = 0

        def show_next(n):
            n += 1
            label_current_time = Label(root, text=timestamp)
            label_current_time.grid(row=2, column=0)

            label_stock_name = Label(root, text=f'{scraped_stock_name[n]} is at ${scraped_stock_price[n]}')
            label_stock_name.grid(row=2, column=1)

        def go_back(n):
            n = 0
            label_current_time = Label(root, text=timestamp)
            label_current_time.grid(row=2, column=0)

            label_stock_name = Label(root, text=f'{scraped_stock_name[n]} is at ${scraped_stock_price[n]}')
            label_stock_name.grid(row=2, column=1)

        label_current_time = Label(root, text=timestamp)
        label_current_time.grid(row=2, column=0)

        label_stock_name = Label(root, text=f'{scraped_stock_name[n]} is at ${scraped_stock_price[n]}')
        label_stock_name.grid(row=2, column=1)

        # Next button which allows users to see the next stock
        button_next = Button(root, text='Next', command=lambda: show_next(n))
        button_next.grid(row=2, column=2)

        button_go_back = Button(root, text='Back', command=lambda: go_back(n))
        button_go_back.grid(row=3, column=2)

    # STOCK INFO
    for count, x in enumerate(stocks_split, start=0):
        # New URL with the stock added to it
        url = f'https://www.google.com/finance?q={x}'

        # Requests and scrape the URL
        req = requests.get(url)
        result = BeautifulSoup(req.text, 'html.parser')

        # Find the name of the stock. Use a try/ except statement to see if the stock is listed on Google finance. If not, 'I couldnt find that will be printed to the user' will be printed. If an Attribute Error occurs,'I couldnt find that!' will be printed.
        try:
            name = (result.find('div', {'class': 'zzDege'})).string
            print(url)
            scraped_stock_name += [name]
        except AttributeError:
            print('I couldnt find that!')

        # Finds the price of the stock and converts it into a float
        price = (result.find('div', {'class': 'YMlKec fxKbKc'})).string
        print(price)
        price_float = float(price[1:])
        scraped_stock_price += [price_float]

        # Timestamp when the data is being logged
        timestamp = str(datetime.now())[11:16]

        # Date of when the data is being logged
        date = str(datetime.now())[:11]

        # Use a try/ except statement to test if a table with the same name already exists.If the table exists, the values will be added to the already existing table.
        try:
            # Create table for the stock
            c.execute(f'''CREATE TABLE {x}
                    (
                    Name,
                    Date,    
                    Time,
                    Price
                    )''')

            conn.commit()

        except OperationalError:
            print('Operational Error: Could not create table.')

        # Adds the values to the database
        c.execute(f'''INSERT INTO {x} VALUES
                (
                "{name}",
                "{date}",
                "{timestamp}",
                "${price_float}"
                )''')
        conn.commit()

        # 'Finished' will be printed when the values have been added.
        print('finished')

        try:
            # If the price of the stock is less than the specified target price, a watchlist table will be created in the database and values will be added
            if price_float <= float(target_price[count]):

                # Creates a table called watchlist if one isnt created already. If an Operational Error occurs, 'Could not create table' will be displayed.
                try:
                    c.execute('''CREATE TABLE Watchlist
                        (
                        Name,
                        Date,
                        Time,
                        Price
                        )''')


                except OperationalError:
                    print('Operational Error: Could not create table.')

                # Adds values to the Watchlist database if the target price is greater than the current price
                c.execute(f'''INSERT INTO Watchlist VALUES
                    (
                    "{name}",
                    "{date}",                    
                    "{timestamp}",
                    "${price_float}"
                    )''')

                conn.commit()

                # Tells the user that the stock was added to the watchlist
                print('Stock added to watchlist')

        # IF an operational error occurs, 'Could not insert values into the watchlist' will be displayed
        except OperationalError:
            print('Operational Error: Could not insert values into the watchlist.')

        # URL resets to the original url for the next loop
        url = 'https://www.google.com/finance?q='


root.mainloop()
