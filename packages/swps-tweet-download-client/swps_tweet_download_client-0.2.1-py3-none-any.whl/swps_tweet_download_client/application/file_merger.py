import glob
import os

import pandas as pd


class FileMerger:

    def merge_files(self, root_directory: str):
        all_files = [
            filename for filename in glob.iglob(os.path.join(root_directory, '**'), recursive=True)
            if filename.endswith('.csv')
        ]
        merged_df = pd.DataFrame()
        for it in all_files:
            df = pd.read_csv(it, lineterminator='\n')
            merged_df = pd.concat([merged_df, df])
        return merged_df.drop_duplicates(subset=['id'], keep='last')

    def save_output(self, dataframe: pd.DataFrame, output_file: str):
        extension = os.path.splitext(output_file)[1]
        if extension == '.csv':
            dataframe.to_csv(output_file, index=False)
        elif extension == '.xlsx':
            dataframe.to_excel(output_file, index=False, engine='xlsxwriter')
        else:
            raise Exception(f'Extension {extension} not supported')

    def merge(self, root_directory: str, output_file: str):
        df = self.merge_files(root_directory)
        self.save_output(df, output_file)
