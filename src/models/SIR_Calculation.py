# importing required python packages
import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import optimize
from scipy import integrate

#setting parameters for DataFrame
pd.set_option('display.max_rows', 500)
#importing data frame
data_raw = pd.read_csv('C:/Users/dhame/ds_covid-19/data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
country_list = data_raw['Country/Region'].unique() #making country_list
date = data_raw.columns[4:]
df_dhameli = pd.DataFrame({'Date': date})

#converting data_raw DataFrame into format that we can use for SIR algorithm
for each in country_list:
    df_dhameli[each] = np.array(data_raw[data_raw['Country/Region'] == each].iloc[:,4::].sum(axis=0)).T
df_dhameli.to_csv("C:/Users/dhame/ds_covid-19/data/processed/SIR.csv", sep = ';', index=False)

df_analyse=pd.read_csv('C:/Users/dhame/ds_covid-19/data/processed/SIR.csv',sep=';')
df_analyse.sort_values('Date',ascending=True).head()

# Intialize parameter
N0 = 1000000
beta = 0.4
gamma = 0.1
I0=df_analyse.Germany[35]
S0=N0-I0
R0=0

df_data = df_analyse[35:] # need to careful here because it difffers from each country!! But I solved it below
t = np.arange(df_data.shape[0])

# defining SIR function
def cal_SIR_model_t(SIR, t, beta, gamma):
    S,I,R=SIR
    dS_dt = -beta*I*S/N0
    dI_dt = beta*I*S/N0 - gamma*I
    dR_dt = gamma*I
    return dS_dt, dI_dt, dR_dt

# defining fit_odeint_func function for optimize parameters
def fit_odeint_func(x, beta, gamma):
    return integrate.odeint(cal_SIR_model_t, (S0, I0, R0), x, args=(beta, gamma))[:,1]

#calculating optimize parameters for every country
for country in df_data.columns[1:]:
        ydata = np.array(df_data[df_data[country]>0][country]) ## consider only value, which greater than zero to solve above mentioned problem
        t = np.arange(len(ydata))
        I0=ydata[0]
        S0=N0-I0
        R0=0
        popt=[0.4,0.1]
        fit_odeint_func(t, *popt)
        popt, pcov = optimize.curve_fit(fit_odeint_func, t, ydata, maxfev=5000)
        perr = np.sqrt(np.diag(pcov))
        fitted=fit_odeint_func(t, *popt)
        fitted_pad = np.concatenate((np.zeros(df_data.shape[0]-len(fitted)) ,fitted)) # concatenate fitted and padded array into list
        df_data[country + '_fitted'] = fitted_pad

df_data = df_data.reset_index(drop=True)
#save CSV file to local drive for future use
df_data.to_csv('C:/Users/dhame/ds_covid-19/data/processed/SIR_fitted.csv', sep = ';')
