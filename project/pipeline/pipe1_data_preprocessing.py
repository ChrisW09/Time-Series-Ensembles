# Wird noch ordentlich in Funktion gewrapped und auch auf externe Daten / daily data anwendbar

import pandas as pd

# Define the directory path and file name
sim_dir = r'C:/Users/Work/OneDrive/GAU/3. Semester/Statistisches Praktikum/Git/NEW_Ensemble_Techniques_TS_FC/project/data/simulations/'
file_name = 'noisy_simdata.csv'

# Combine the directory path and file name
file_path = sim_dir + file_name


# Read and preprocess Dataset
df = pd.read_csv(file_path, index_col = "Date")


def pipe1_data_preprocessing(df, verbose=False):
    if verbose:
        print("=====================================================")
        print("== Starting Step 1 in Pipeline: Data Preprocessing ==")
        print("=====================================================")
    
    # index in index abspeichern, nicht als Spalte! wichtig für preprocessing
    # # if Bedingung: if freq is not given or gibt error:
    
    infered_freq = pd.infer_freq(df.index)
    df.index = pd.to_datetime(df.index)
    df.index.freq = infered_freq # or given freq     
      
    if "M" in infered_freq:
        infered_freq = "M"  
        
    # Convert DataFrame to TimeSeries and split target and predictors
    
    # Indicator if DataFrame includes covariates
    #contains_covariates = bool(predictors_names)  
    target = df['y']
    covariates = df.iloc[:, 1:] # default: None    
    target.index = pd.PeriodIndex(target.index, freq=infered_freq)
    #if covariates is not None:
    covariates.index = pd.PeriodIndex(covariates.index, freq=infered_freq)  
    
    if verbose:
        print("Target:", target.name)
        print("Covariates:", ", ".join(covariates.columns)) 
          
    return target, covariates      



        #input pandas dataframe
        # argument for target
        #argument for covariates
        # argument for data
        # argument freq

        # date="index", freq="infer", 

        # # if not "index" please provide an array-like, pandas Series of dates, DatetimeIndex or PeriodIndex as input
        #     if date != "index":
        #         target.index, covariates.index = date
        #         covariates.index = date
                
        #     if freq == "infer":
        #         freq = pd.infer_freq(target.index)
        
        #     # change "MS" and "ME" to "M" for PeriodIndex
        #     if "M" in freq:
        #         freq = "M"
                
        #             # Change data index to period index for sktime
        #     target.index = pd.PeriodIndex(target.index, freq=infered_freq)

