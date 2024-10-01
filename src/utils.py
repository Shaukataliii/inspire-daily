import os, yaml
import pandas as pd

class Utilities:
    def update_params(new_params, params_filepath: str = "src/params.yaml"):
        with open(params_filepath, 'w') as file:
            yaml.dump(new_params, file)

    def df_file_exists() -> bool:
        """Checks if the quote_df_filepath exists.
        """
        df_filepath = Utilities.load_params()['quote_df_filepath']
        if os.path.exists(df_filepath):
            return True
        else:
            return False
        
    def load_params(params_filepath: str = "src/params.yaml"):
        with open(params_filepath, 'r') as file:
            params = yaml.safe_load(file)
        return params
    
    def load_pd_dataframe(path: str):
        """Loads the dataframe if path exists else raise exception."""
        if os.path.exists(path):
            return pd.read_csv(path)
        
        else:
            raise Exception(f"Df path doesn't exist. Path: {path}")
    

class DFHandler:
    """Handles the saving, loading of quotes dataset."""
    def __init__(self):
        self.df_filepath = Utilities.load_params()['quote_df_filepath']

    def save_df(self, df: pd.DataFrame):
        df.to_csv(self.df_filepath, index=False)

    def load_df(self):
        df = self.__load_dataset()
        return df
    
    def __load_dataset(self):
        if Utilities.df_file_exists():
            df = pd.read_csv(self.df_filepath)
            return df
        else:
            raise Exception("Provided quotes file doesn't exist.")
        
    def get_dataset_size(self, dataset):
        dataset_size = dataset.shape[0]
        return dataset_size - 1