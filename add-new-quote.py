from src.utils import DFHandler
import pandas as pd

class QuoteAdder:
    def take_input_params():
        quote = input("Enter the quote: ")
        author = input("Enter author: ")
        return (quote, author)

    def main():
        print("Welcome. Let's add a new quote to the dataset.")
        QuoteAdder.take_input_handle_it()

    def take_input_handle_it():
        quote, author = QuoteAdder.take_input_params()
        
        if QuoteAdder.do_the_user_wants_to_add_provided_quote():
            QuoteAdder.add_quote_to_dataset(quote, author)
        else:
            print("Quote addition skipped.")
            exit()

    def do_the_user_wants_to_add_provided_quote():
        choice = input("Do you want to proceed (y/n): ")
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            raise Exception("Invalid input. Only y or n is allowed.")
        
    def add_quote_to_dataset(quote, author):
        try:
            new_quote = QuoteAdder.make_df_from_inputs(quote, author)
            df = DFHandler().load_df()
            df = QuoteAdder.add_new_row_in_dataset(df, new_quote)
            DFHandler().save_df(df)
            print("New quote added.")

        except Exception as e:
            raise Exception("An error occured while adding the new quote. Try later.", e)

    def make_df_from_inputs(quote, author):
        return pd.DataFrame([[quote, author,""]], columns=['quote', 'author', 'category'])
    
    def add_new_row_in_dataset(df, new_quote):
        return pd.concat([df, new_quote], axis=0, ignore_index=True)
            


QuoteAdder.main()