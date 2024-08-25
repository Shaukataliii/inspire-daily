from plyer import notification
import time, random, os
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
                NotificationDisplayer.show_quote_notification(quote)
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
        if self.__df_file_exists():
            self.df = pd.read_csv(self.df_filepath)
            return
        else:
            raise Exception("Provided quotes file doesn't exist.")

    def __df_file_exists(self) -> bool:
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
    def show_quote_notification(quote: str):
        print("Gonna display notification..")
        notification.notify(
            title="Daily Quote",
            message=quote,
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


def process_initializer(df_filepath, notification_hour, notification_minute, seconds_to_wait_before_recheck):
    quote_provider = QuoteProvider()
    time_checker = TimeChecker()
    notification_handler = NotificationHandler()

    quote_provider.setter(df_filepath)
    time_checker.setter(notification_hour, notification_minute)
    notification_handler.setter(seconds_to_wait_before_recheck)
    notification_handler.display_quote_on_time(quote_provider)

if __name__ == "__main__":
    df_filepath = r"D:\Shaukat ali khan\programming\Data Science - Krish Naik\GenAI\langchain\AI-course-RAG\resources\no-code-files\07-quote-dateset.csv"
    seconds_to_wait_before_recheck = 59
    
    notification_hour = int(input("Enter notification hour: "))
    notification_minute = int(input("Enter notification minute: "))

    process_initializer(df_filepath, notification_hour, notification_minute, seconds_to_wait_before_recheck)
