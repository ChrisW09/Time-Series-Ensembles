import pandas as pd

from utils.helpers import identify_date_column, target_covariate_split, aggregate_data, vprint
from utils.mappings import FREQ_MAPPING


### For debugging:
### from paths import *
### import os
### FILE_PATH = os.path.join(SIMDATA_DIR, 'noisy_simdata.csv')
### df = pd.read_csv(FILE_PATH)


def pipe1_data_preprocessing(df,
                             date_col='infer', date_format=None,
                             target='infer', covariates='infer', exclude=None,
                             agg_method=None, agg_freq=None,
                             verbose=False, *args, **kwargs):
    
    """
    Preprocesses the input DataFrame for further analysis.

    Args:
        df (pandas.DataFrame):                  Input DataFrame.
        date_col (str or int):                  Name or positional index of the column containing date information.
        date_format (str, optional):            Format of the date column.
        target (str or int):                    Name or positional index of the target column.
        covariates (str, int, list, or None):   Name(s) or positional index(es) of the covariate column(s), or None if there are no covariates.
        exclude (str, int, list, or None):      Name(s) or positional index(es) of the columns to exclude, or None if no columns need to be excluded.
        agg_method (str, optional):             Aggregation method to use if data aggregation is desired.
        agg_freq (str, optional):               Frequency to which data will be aggregated if aggregation is desired.
        verbose (bool, optional):               Whether to print verbose output.
        *args:                                  Additional positional arguments.
        **kwargs:                               Additional keyword arguments.

    Returns:
        tuple: A tuple containing the target and covariate DataFrames.
    """
    # Print preprocessing start message
    vprint("\n====================================================="
           "\n== Starting Step 1 in Pipeline: Data Preprocessing =="
           "\n=====================================================\n")

    # Transform positional indices of target, covariate, and exclude to labels and perform input validation

    # Target
    initial_column_names = df.columns
    if isinstance(target, int):
        target = initial_column_names[target]
    elif not isinstance(target, str):
        raise ValueError('Target must be provided as str or positional int.')
    
    # Covariates
    if isinstance(covariates, int):
        covariates = initial_column_names[covariates]
    elif isinstance(covariates, list):
        covariates = [element if isinstance(element, str) else initial_column_names[element] for element in covariates]
    elif not isinstance(covariates, str) and covariates is not None:
        raise ValueError('If not None, covariates must be provided as str, positional int or list of str/int.')
    
    # Excluded columns
    if isinstance(exclude, int):
        covariates = initial_column_names[exclude]
    elif isinstance(exclude, list):
        exclude = [element if isinstance(element, str) else initial_column_names[element] for element in exclude]
    elif not isinstance(exclude, str) and exclude is not None:
        raise ValueError('If not None, excluded columns must be provided as str, positional int or list of str/int.')

    # Identify position and name of date column if not provided
    # Transform positional index to column label
    if isinstance(date_col, int):
        date_col = df.columns[date_col]
    # Identify position and name of date column if not provided and set as index
    elif date_col == 'infer':
        vprint('Searching for time information...')
        date_col = identify_date_column(df, date_format=date_format)
        vprint(f'Dates found in \'{date_col}\' column!')
    elif isinstance(date_col, str):
        pass
    else:
        raise ValueError('date_col must be either \'infer\' or of type str or positional int.')
    
    # Set given/inferred date_col as the index column if it is not yet in the index
    if date_col != 'index':
        df.set_index(date_col, inplace=True)

    # Transform index to DateTime Index
    df.index = pd.to_datetime(arg=df.index, format=date_format)

    # Infer frequency and map to common frequency aliases
    inferred_freq = pd.infer_freq(df.index)
    df.index.freq = inferred_freq
    mapped_inferred_frequency = FREQ_MAPPING[inferred_freq] if (
            inferred_freq in FREQ_MAPPING.keys()) else inferred_freq
    
    ### vprint('Inferring frequency...')
    vprint(f'Inferred frequency: {mapped_inferred_frequency}')
    vprint(f"Data from goes from {df.index[0].date()} to {df.index[-1].date()}, "
           f"resulting in {len(df)} observations.\n")

    # If desired, perform data aggregation
    if agg_method is not None and agg_freq is not None:
        agg_mapped_frequency = FREQ_MAPPING[agg_freq] if (
                agg_freq in FREQ_MAPPING.keys()) else agg_freq
        vprint(f'Aggregating data to frequency \'{agg_mapped_frequency}\' using method \'{agg_method}\''
               + ' and dropping NaNs'
               + '...'
               )
        df = aggregate_data(data=df, method=agg_method, agg_freq=agg_freq, drop_nan=True)
        vprint(f'...finished!' 
               f'\nData now has {len(df)} observations.\n')
    elif (agg_method is not None) ^ (agg_freq is not None):
        raise ValueError('Arguments \'agg_method\' and \'agg_freq\' must always be specified together.')

    # Split DataFrame into target and covariates (if covariates exist)
    vprint('Selecting target' + (' and covariates' if covariates is not None else '') + '...')
    target, covariates = target_covariate_split(df, target=target, covariates=covariates, exclude=exclude)

    # Print selected covariates and target
    vprint("Target: " + target.name)
    vprint("Covariates: " + (", ".join(covariates.columns) if covariates is not None else 'None'))

    # Provide data insight
    vprint("\nData Insight:\n")
    vprint(pd.concat([target, covariates], axis=1).head())

    # Merge target and covariates to tuple
    output_tuple = (target, covariates)

    return output_tuple


### For debugging:
### y, X = pipe1_data_preprocessing(df=df, forecasters=forecasting_models, verbose=True)
### print(y, X)
