import pandas as pd
import datetime as dt
from copy import deepcopy
import matplotlib.pyplot as plt

def data_handling():

    wvar_file = "covid19_PT_semanal.xlsx"
    wvar_sheet_name = "for_py"

    meas_file = "medidas.xlsx"
    meas_sheet_name = "Folha1"

    #data_file = "https://github.com/dssg-pt/covid19pt-data/blob/master/data.csv"
    data_file = "data.csv"

    wvar_df = pd.read_excel(wvar_file, sheet_name=wvar_sheet_name, usecols=["Data", "I"])
    wvar_df = wvar_df[~wvar_df.I.isnull()]
    wvar_df = wvar_df[["Data"]]

    meas_df = pd.read_excel(meas_file, sheet_name=meas_sheet_name)
    meas_df = meas_df[~meas_df.Data.isnull()]
    meas_df = meas_df[meas_df.Marker==1]
    meas_df = meas_df[:-1]

    data_df = pd.read_csv(data_file, usecols=["data", "confirmados"])
    data_df["data"] = pd.to_datetime(data_df["data"], format="%d-%m-%Y")

    data_df = data_df.rename(columns={"data": "Data"})

    df = wvar_df.merge(meas_df, how="outer", left_on="Data", right_on="Data", sort=True)

    df = df.merge(data_df, how="inner", left_on="Data", right_on="Data", sort=True)
    df["weekday"] = df["Data"].dt.dayofweek

    df["Medida"][df["Medida"].isnull()] = ""
    df["Marker"][df["Marker"].isnull()] = 0

    df["Var_I"] = df["confirmados"][df["weekday"]==0].diff(1)

    earliest_date = df["Data"].min() 
    latest_date = df["Data"].max()
    df["Var_I_New"] = [0]*len(df["Data"])

    for i in range(0, len(df["Data"])):
        weekday = df["weekday"].iloc[i]
    
        if df["Data"].iloc[i]+pd.Timedelta(days=7) <= latest_date and df["Data"].iloc[i] > earliest_date:
            prev_monday_var = df["Var_I"][df["Data"]==df["Data"].iloc[i]+pd.Timedelta(days=-weekday)].values[0]
            next_monday_var = df["Var_I"][df["Data"]==df["Data"].iloc[i]+pd.Timedelta(days=7-weekday)].values[0]
            df["Var_I_New"].iloc[i] = prev_monday_var + ((next_monday_var-prev_monday_var)/7)*weekday

        if df["Data"].iloc[i]+pd.Timedelta(days=7) >= latest_date:
            prev_monday_var = df["Var_I"][df["Data"]==df["Data"].iloc[i]+pd.Timedelta(days=-weekday)].values[0]
            next_monday_var = df["Var_I"][df["Data"]==latest_date].values[0]
            df["Var_I_New"].iloc[i] = prev_monday_var + ((next_monday_var-prev_monday_var)/7)*weekday

    return df