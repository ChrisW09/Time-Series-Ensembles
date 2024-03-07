import pandas as pd

from utils.helpers import identify_date_column, target_covariate_split, aggregate_data, vprint
from utils.mappings import FREQ_MAPPING


### For debugging:
### from paths import *
### import os
### FILE_PATH = os.path.join(SIMDATA_DIR, 'noisy_simdata.csv')
### df = pd.read_csv(FILE_PATH)


def pipe1_data_preprocessing(
        df, start=None, end=None,
        date_col='infer', date_format=None,
        target='infer', covariates='infer', exclude=None,
        agg_method=None, agg_freq=None,
        verbose=False,
        *args, **kwargs):
    """
    Preprocesses the input DataFrame for further analysis, i.e., aggregation, column, filtering, and index operations.

    Parameters:
    -----------
        df : pandas.DataFrame
            Input DataFrame containing date, targets (and optionally covariates).
        start : str, optional
            Filter data to start from date string. Expects ISO DateTimeIndex format "YYYY-MMMM-DDD" (default: None).
        end : str, optional
            Filter data to end on date string. Expects ISO DateTimeIndex format "YYYY-MMMM-DDD" (default: None).
        date_col : str or int, optional
            Name or index of the date column in the input data (default: 'infer', searches for ISO formatted column).
        date_format : str, optional
            Custom format of the date column if date_col is specified (default: None, expects ISO format YYYY-MM-DD).
        target : str, int, optional
            Name or positional index of the target column in the input data (default: 'infer', takes first column
            after the date was set).
        covariates : str, int, or list, optional
            Names of covariates columns in the input data (default: 'infer', takes all columns after date and target
            are inferred.).
        exclude : str, int, or list, optional
            List of columns (string or positional index) to exclude from the input data (default: None).
        agg_method : str, optional
            Aggregation method for preprocessing.
            One of the pandas methods 'first', 'last', 'min', 'max', and 'mean' (default: None).
        agg_freq : str, optional):
            DateTimeIndex aggregation frequency for preprocessing (default: None).
        verbose : bool, optional):
            If True, prints and logs intermediate steps of data preprocessing to console and to log file
            (default: False).
        *args:
            Additional positional arguments.
        **kwargs:
            Additional keyword arguments.

    Returns:
    --------
        tuple: A tuple containing the target and covariate DataFrames. Index is a pandas PeriodIndex containing dates,
        respectively.
        
    """

    # Print preprocessing start message
    vprint("\n========================================="
           "\n== Pipeline Step 1: Data Preprocessing =="
           "\n=========================================\n")

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

    # Take subsetset of data
    if start is not None and end is not None:
        df = df.loc[start:end]  # Slice from start to end
    elif start is not None:
        df = df.loc[start:]  # Slice from the start index to the end
    elif end is not None:
        df = df.loc[:end]  # Slice from the beginning to the end index

    # Infer frequency and map to common frequency aliases
    inferred_freq = pd.infer_freq(df.index)
    df.index.freq = inferred_freq
    mapped_inferred_frequency = FREQ_MAPPING[inferred_freq] if (
            inferred_freq in FREQ_MAPPING.keys()) else inferred_freq

    # Verbose print data information (frequency, start, end, number of observations)
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
