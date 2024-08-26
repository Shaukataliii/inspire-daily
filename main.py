from plyer import notification
import time, random, os, yaml, subprocess, zipfile
import pandas as pd
from datetime import datetime


class NotificationHandler:
    def setter(self, seconds_to_wait_before_recheck_time: int = 30):
        self.seconds_to_wait_before_recheck_time = seconds_to_wait_before_recheck_time
    
    def display_quote_on_time(self, quote_provider):
        print("Running..")
        while True:
            if TimeChecker.is_time_to_notify():
                quote = quote_provider.get_quote()
                NotificationDisplayer.show_notification(quote)
            self.wait_before_recheck()

    def wait_before_recheck(self):
        time.sleep(self.seconds_to_wait_before_recheck_time)  # Check every duraction
        return


class QuoteProvider:
    def setter(self, df_filepath):
        self.df_filepath = df_filepath
        self.dataset_size = None
        self.df = None

    def get_quote(self):
        print("Getting quote..")
        quote = self.__get_random_quote()
        return quote

    def __get_random_quote(self) -> str:
        self.load_df_update_size_var()
        index = self.__get_random_index()
        quote = self.__extract_quote_from_df_at_index(index)
        return quote

    def load_df_update_size_var(self):
        self.__load_df()
        self.__update_dataset_size_var()
    
    def __load_df(self):
        if self.df_file_exists():
            self.df = pd.read_csv(self.df_filepath)
            return
        else:
            raise Exception("Provided quotes file doesn't exist.")

    def df_file_exists(self) -> bool:
        if os.path.exists(self.df_filepath):
            return True
        else:
            return False
        
    def __update_dataset_size_var(self):
        dataset_size = self.df.shape[0]
        self.dataset_size = dataset_size - 1
        print(f"Dataset size is set to: {dataset_size}")

    def __get_random_index(self) -> int:
        random_index = random.randint(0,self.dataset_size)
        return random_index
    
    def __extract_quote_from_df_at_index(self, index) -> pd.Series:
        quote_details = self.df.iloc[index,:]
        quote = QuoteFormatter.format_quote(quote_details)
        return quote
    

class QuoteFormatter:
    def format_quote(quote_details: pd.Series) -> str:
        quote_details = list(quote_details)
        quote = quote_details[0]
        author = quote_details[1]
        quote = f'"{quote}" \n- {author}'
        return quote

    
class NotificationDisplayer:
    def show_notification(message: str):
        notification.notify(
            app_name="Inspire Daily",
            title="Daily Quote",
            message=message,
            ticker="Quote",
            timeout=10  # Notification will stay for 10 seconds
        )
        time.sleep(50)  # Sleep to avoid multiple notifications within the same minute


class TimeChecker:
    def setter(self, notification_hour: int = 9, notification_minute: int = 00):
        TimeChecker.notification_hour = notification_hour
        TimeChecker.notification_minute = notification_minute

    def is_time_to_notify():
        print("Checking if it's time to notify..")
        current_time = TimeChecker._get_current_time()
        if TimeChecker.__is_notification_hour(current_time.hour) and TimeChecker.__is_notification_minute(current_time.minute):
            return True
        else:
            return False
        
    def _get_current_time():
        return datetime.now().time()
    
    def __is_notification_hour(current_hour):
        if current_hour == TimeChecker.notification_hour:
            return True
        else:
            return False

    def __is_notification_minute(current_minute):
        if current_minute == TimeChecker.notification_minute:
            return True
        else:
            return False


class DatasetPreparer:
    def __init__(self, kaggle_api_command: str):
        self.kaggle_api_command = kaggle_api_command
        self.zip_dataset_name = kaggle_api_command.split('/')[-1] + ".zip"

    def download_and_unzip_dataset(self):
        """Raises exception if something goes wrong."""
        self.__download_from_kaggle()
        self.__unzip_dataset()
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
  

class Initializer(QuoteProvider):
    def load_instance_params(self, params_filepath: str = "params.yaml"):
        with open(params_filepath, 'r') as file:
            params = yaml.safe_load(file)

        self.df_filepath = params["df_filepath"]
        self.notification_hour = params["notification_hour"]
        self.notification_minute = params["notification_minute"]
        self.seconds_to_wait_before_recheck = params["seconds_to_wait_before_recheck"]
        self.kaggle_dataset_api_cmd = params["kaggle_dataset_api_cmd"]

    def process_initializer(self):
        self.load_instance_params()
        self.make_sure_dataset_is_ready()

        quote_provider = QuoteProvider()
        time_checker = TimeChecker()
        notification_handler = NotificationHandler()

        quote_provider.setter(self.df_filepath)
        time_checker.setter(self.notification_hour, self.notification_minute)
        notification_handler.setter(self.seconds_to_wait_before_recheck)

        notification_handler.display_quote_on_time(quote_provider)

    def make_sure_dataset_is_ready(self):
        if self.df_file_exists():
            return
        else:
            # download and prepare dataset here
            NotificationDisplayer.show_notification("Downloading dataset")
            DatasetPreparer(self.kaggle_dataset_api_cmd).download_and_unzip_dataset()

      


if __name__ == "__main__":
    initializer = Initializer()
    initializer.process_initializer()
