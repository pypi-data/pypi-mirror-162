import pandas as pd
import teradataml as tdml
import os

train_dataset_filename = 'train_dataset.csv'
package_dir, _ = os.path.split(__file__)

def train_dataset():
    return pd.read_csv(os.path.join(package_dir, "data", train_dataset_filename),parse_dates =  ['datetime'])

def upload_train_dataset(table_name='train_dataset', **kwargs):
    if 'schema_name' in kwargs.keys():
        print('dataset uploaded in '+ kwargs['schema_name'] + '.' + table_name)
    else:
        print('schema_name not specified. default used')
        print('dataset uploaded in '+table_name)

    tdml.copy_to_sql(df=train_dataset(),
                     table_name=table_name,
                     types = {"events": tdml.VARCHAR(length = 1000, charset = 'LATIN')},
                     **kwargs)

    if 'schema_name' in kwargs.keys():
        df = tdml.DataFrame(tdml.in_schema(kwargs['schema_name'], table_name))
    else:
        df = tdml.DataFrame(table_name)

    return df