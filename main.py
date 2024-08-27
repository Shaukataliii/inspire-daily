from plyer import notification
import time, random, os, yaml, subprocess, zipfile
import pandas as pd
from datetime import date 


class Initializer():
    """Sets up things. Makes sure dataset is ready and runs the notification handler."""
    def set_instance_params(self, params):
        self.df_filepath = params["df_filepath"]
        self.hours_to_wait_before_recheck = params["hours_to_wait_before_recheck"]
        self.kaggle_dataset_api_cmd = params["kaggle_dataset_api_cmd"]

    def process_initializer(self):
        params = Utilities.load_params()
        self.set_instance_params(params)
        self.make_sure_dataset_is_ready()

        notification_handler = NotificationHandler()
        notification_handler.setter(self.hours_to_wait_before_recheck)
        quote_provider = QuoteProvider()
        quote_provider.setter(self.df_filepath)

        notification_handler.display_quote_on_time(quote_provider)

    def make_sure_dataset_is_ready(self):
        if Utilities.df_file_exists():
            return
        else:
            NotificationDisplayer.show_notification("Downloading dataset")
            DatasetPreparer(self.kaggle_dataset_api_cmd).download_and_unzip_dataset()

      
class Utilities:
    def load_params(params_filepath: str = "params.yaml"):
        with open(params_filepath, 'r') as file:
            params = yaml.safe_load(file)
        return params
    
    def update_params(new_params, params_filepath: str = "params.yaml"):
        with open(params_filepath, 'w') as file:
            yaml.dump(new_params, file)

    def df_file_exists() -> bool:
        df_filepath = Utilities.load_params()['dataset_csv_filename']
        if os.path.exists(df_filepath):
            return True
        else:
            return False


class DatasetPreparer:
    """Downloads the dataset and makes it ready to use."""
    def __init__(self, kaggle_api_command: str):
        self.kaggle_api_command = kaggle_api_command
        self.zip_dataset_name = kaggle_api_command.split('/')[-1] + ".zip"

    def download_and_unzip_dataset(self):
        """Raises exception if something goes wrong."""
        self.__download_from_kaggle()
        self.__unzip_dataset()
        self.__remove_quotes_with_len_less_150()
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
        
    def __remove_quotes_with_len_less_150():
        quote_provider = QuoteProvider()
        df = quote_provider.__load_df()
        df = df[df['quote'].str.len() < 150]
        df.to_csv("quotes.csv", index=False)

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
    
    def display_quote_on_time(self, quote_provider):
        print("Running..")
        while True:
            if TimeChecker.is_time_to_notify():
                quote = quote_provider.get_quote()
                NotificationDisplayer.show_notification(quote)
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
        self.__load_df_update_size_var()
        index = self.__get_random_index()
        quote = self.__extract_quote_from_df_at_index(index)
        return quote

    def __load_df_update_size_var(self):
        self.__load_df()
        self.__update_dataset_size_var()
    
    def __load_df(self):
        if Utilities.df_file_exists():
            self.df = pd.read_csv(self.df_filepath)
            return
        else:
            raise Exception("Provided quotes file doesn't exist.")
        
    def __update_dataset_size_var(self):
        dataset_size = self.df.shape[0]
        self.dataset_size = dataset_size - 1

    def __get_random_index(self) -> int:
        random_index = random.randint(0,self.dataset_size)
        return random_index
    
    def __extract_quote_from_df_at_index(self, index) -> pd.Series:
        quote_details = self.df.iloc[index,:]
        quote = QuoteFormatter.format_quote(quote_details)
        return quote
    

class QuoteFormatter:
    """Formats provided quote."""
    def format_quote(quote_details: pd.Series) -> str:
        quote_details = list(quote_details)
        quote = quote_details[0]
        author = quote_details[1]
        quote = f'"{quote}" \n- {author}'
        return quote
    

class NotificationDisplayer:
    """Displays notification with provided message."""
    def show_notification(message: str):
        notification.notify(
            app_name="Inspire Daily",
            title="Daily Quote",
            message=message,
            ticker="Quote",
            timeout=20  # Notification will stay for 20 seconds
        )
        TimeChecker.update_last_notified_date_as_today_in_params()





if __name__ == "__main__":
    initializer = Initializer()
    initializer.process_initializer()
