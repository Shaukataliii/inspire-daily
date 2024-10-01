from src.utils import Utilities, DFHandler
from plyer import notification
import os, time, random, subprocess, zipfile, shutil
import pandas as pd
from datetime import date
import tkinter as tk
from tkinter import messagebox




class Initializer():
    """Sets up things. Makes sure dataset is ready and runs the notification handler."""
    def set_instance_params(self, params):
        self.quote_df_filepath = params["quote_df_filepath"]
        self.hadith_df_filepath = params["hadith_df_filepath"]
        self.hours_to_wait_before_recheck = params["hours_to_wait_before_recheck"]
        self.kaggle_dataset_api_cmd = params["kaggle_dataset_api_cmd"]

    def process_initializer(self):
        params = Utilities.load_params()
        self.set_instance_params(params)
        self.make_sure_dataset_is_ready()
        notification_handler, quote_provider, hadith_provider = self.initialize_classes()
        notification_handler.display_quote_on_time(quote_provider, hadith_provider)

    def make_sure_dataset_is_ready(self):
        if Utilities.df_file_exists():
            return
        else:
            NotificationDisplayer.show_notification("Downloading dataset")
            DatasetPreparer(self.kaggle_dataset_api_cmd, self.df_filepath).download_unzip_clean_move_dataset()

    def initialize_classes(self):
        notification_handler = NotificationHandler()
        notification_handler.setter(self.hours_to_wait_before_recheck)
        
        quote_provider = QuoteProvider()
        quote_provider.setter(self.quote_df_filepath)

        hadith_provider = HadithProvider()
        hadith_provider.setter(self.hadith_df_filepath)
        return (notification_handler, quote_provider, hadith_provider)


class DatasetPreparer:
    """Downloads the dataset and makes it ready to use."""
    def __init__(self, kaggle_api_command: str, df_filepath: str):
        self.kaggle_api_command = kaggle_api_command
        self.zip_dataset_name = kaggle_api_command.split('/')[-1] + ".zip"
        self.csv_dataset_name = kaggle_api_command.split('/')[-1] + ".csv"
        self.df_filepath = df_filepath

    def download_unzip_clean_move_dataset(self):
        """Raises exception if something goes wrong."""
        self.__download_from_kaggle()
        self.__unzip_dataset()
        self.__remove_quotes_with_len_less_150()
        self.__move_dataset_to_src()
        self.__delete_useless_files()

    def __download_from_kaggle(self):
        process = subprocess.Popen(f"cmd /c {self.kaggle_api_command}", shell=True)
        process.communicate()
        if process.returncode == 0:
            print("Dataset Downloaded.")
        else:
            raise Exception("Failed to download dataset. Consider trying again and make sure internet is connected.")

    def __unzip_dataset(self):
        self.__validate_dataset_is_zipped()

        try:
            with zipfile.ZipFile(self.zip_dataset_name) as file:
                file.extractall(".")
            print("Dataset Extracted.")
        except:
            raise Exception("An error occured while unzipping the dataset!")

    def __validate_dataset_is_zipped(self):
        if zipfile.is_zipfile(self.zip_dataset_name):
            return True
        else:
            raise Exception("Downloaded dataset is not a zipfile.")
        
    def __move_dataset_to_src(self):
        try:
            shutil.move(self.csv_dataset_name, self.df_filepath)
        except:
            raise Exception("Dataset moving failed. Try downloading again.")

    def __remove_quotes_with_len_less_150():
        quote_provider = QuoteProvider()
        df = DFHandler().load_df()
        df = df[df['quote'].str.len() < 150]
        DFHandler().save_df(df)

    def __delete_useless_files(self):
        if os.path.exists(self.zip_dataset_name):
            os.remove(self.zip_dataset_name)
        if os.path.exists("test.txt"):
            os.remove("test.txt")
        if os.path.exists("train.txt"):
            os.remove("train.txt")
        if os.path.exists("valid.txt"):
            os.remove("valid.txt")
        NotificationDisplayer.show_notification("All Done.")


class NotificationHandler:
    """Handles the displays of quote on time."""
    def setter(self, hours_to_wait_before_recheck: int = 30):
        self.hours_to_wait_before_recheck = hours_to_wait_before_recheck
    
    def display_quote_on_time(self, quote_provider, hadith_provider):
        print("Running..")
        while True:
            if TimeChecker.is_time_to_notify():
                quote = quote_provider.get_quote()
                hadith = hadith_provider.get_hadith()
                NotificationDisplayer.show_notification(quote)
                NotificationDisplayer.show_hadith(hadith)
                
                TimeChecker.update_last_notified_date_as_today_in_params()
            self.wait_before_recheck()

    def wait_before_recheck(self):
        seconds_to_wait = self.convert_hours_to_seconds()
        time.sleep(seconds_to_wait)  # Check every duraction
        return
    
    def convert_hours_to_seconds(self):
        return self.hours_to_wait_before_recheck * 60 * 60


class TimeChecker():
    """Checks if it is the time to show quote notification."""
    def is_time_to_notify():
        print("Checking if it's time to notify..")
        if not TimeChecker.__is_notification_done_today():
            return True
        else:
            return False
        
    def __is_notification_done_today():
        last_notified_date = TimeChecker.__get_last_notified_date_str()
        date_today = TimeChecker.__get_current_date_str()

        if last_notified_date == date_today:
            return True
        else:
            return False
        
    def __get_last_notified_date_str():
        params = Utilities.load_params()
        last_notified_date = params['last_notified_date']
        return last_notified_date
    
    def update_last_notified_date_as_today_in_params():
        params = Utilities.load_params()
        date_today = TimeChecker.__get_current_date_str()
        params['last_notified_date'] = date_today
        Utilities.update_params(params)
        print("Last notified time updated.")

    def __get_current_date_str():
        return str(date.today())


class QuoteProvider:
    """Provides random quote from the quotes dataset."""
    def setter(self, df_filepath):
        self.df_filepath = df_filepath
        self.dataset_size = None
        self.df = None

    def get_quote(self):
        print("Getting quote..")
        quote = self.__get_random_quote()
        return quote

    def __get_random_quote(self) -> str:
        self.__load_df_and_set_size()
        index = self.__get_random_index()
        quote = self.__extract_quote_from_df_at_index(index)
        quote = self.__format_quote(quote)
        return quote
    
    def __load_df_and_set_size(self):
        self.df = DFHandler().load_df()
        self.dataset_size = DFHandler().get_dataset_size(self.df)

    def __get_random_index(self) -> int:
        random_index = random.randint(0,self.dataset_size)
        return random_index
    
    def __extract_quote_from_df_at_index(self, index) -> pd.Series:
        quote_details = self.df.iloc[index,:]
        return quote_details
    
    def __format_quote(self, quote_details):
        quote = QuoteFormatter.format_quote(quote_details)
        return quote


class HadithProvider:
    """Provides random hadith from the hadiths dataset."""
    def setter(self, df_filepath):
        self.df_filepath = df_filepath
        self.dataset_size = None
        self.df = None

    def get_hadith(self):
        print("Getting quote..")
        quote = self.__get_random_quote()
        return quote

    def __get_random_quote(self) -> str:
        self.__load_df_and_set_size()
        index = self.__get_random_index()
        quote = self.__extract_quote_from_df_at_index(index)
        quote = self.__format_quote(quote)
        return quote
    
    def __load_df_and_set_size(self):
        self.df = Utilities.load_pd_dataframe(self.df_filepath)
        self.dataset_size = DFHandler().get_dataset_size(self.df)

    def __get_random_index(self) -> int:
        random_index = random.randint(0,self.dataset_size)
        return random_index
    
    def __extract_quote_from_df_at_index(self, index) -> pd.Series:
        quote_details = self.df.iloc[index,:]
        return quote_details
    
    def __format_quote(self, quote_details):
        quote = QuoteFormatter.format_quote(quote_details)
        return quote


class QuoteFormatter:
    """Formats provided quote/hadith. Treats 0th index as content and 1st index as source."""
    def format_quote(details: pd.Series) -> str:
        details = list(details)
        content = details[0]
        detail = details[1]
        content = f'"{content}" \n- {detail}'
        return content
    

class NotificationDisplayer:
    """Displays notification and hadith."""
    def show_notification(message: str):
        notification.notify(
            app_name="Inspire Daily",
            title="Daily Quote",
            message=message,
            ticker="Quote",
            timeout=20  # Notification will stay for 20 seconds
        )
        print("Notification done.")

    def show_hadith(hadith: str):
        """Displays the provided hadith using tkinter.

        Args:
            hadith (str): The hadith to display.
        """
        # Create the main window
        root = tk.Tk()
        root.title("InspireD Daily Hadith.")
        
        # Set the window size
        root.geometry("400x200")
        
        # Add a label with the content
        label = tk.Label(root, text=hadith, wraplength=350, justify="left")
        label.pack(pady=20)
        
        # Add a close button
        close_button = tk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=30)
        
        # Run the Tkinter loop
        root.mainloop()



if __name__ == "__main__":
    initializer = Initializer()
    initializer.process_initializer()



# move the hadith to index 0 and source to 1