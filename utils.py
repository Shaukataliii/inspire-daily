import os, yaml
import pandas as pd

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
        

class DFHandler:
    def __init__(self):
        self.df_filepath = Utilities.load_params()['df_filepath']

    def save_df(self, df: pd.DataFrame):
        df.to_csv(self.df_filepath, index=False)

    def load_df(self):
        df = self.__load_dataset()
        return (df)
    
    def __load_dataset(self):
        if Utilities.df_file_exists():
            df = pd.read_csv(self.df_filepath)
            return df
        else:
            raise Exception("Provided quotes file doesn't exist.")
        
    def get_dataset_size(self, dataset):
        dataset_size = dataset.shape[0]
        return dataset_size - 1