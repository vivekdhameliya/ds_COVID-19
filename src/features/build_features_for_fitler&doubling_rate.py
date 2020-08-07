#importing required packageas
import numpy as np
from sklearn import linear_model
reg = linear_model.LinearRegression(fit_intercept=True)
import pandas as pd
from scipy import signal

# creating function for calculating doubling rate via regression
def calculate_doubling_time_via_regression(in_array):
    y = np.array(in_array)
    X = np.arange(-1,2).reshape(-1, 1)
    assert len(in_array)==3
    reg.fit(X,y)
    intercept=reg.intercept_
    slope=reg.coef_
    return intercept/slope

# create function for savgol_filter for groupby operation
def savgol_filter(df_input,column='confirmed',window=5):
    degree=1
    df_result=df_input
    # fillup empty raw with 0 value in dataframe
    filter_in=df_input[column].fillna(0)
    # window size is used for filtering
    result=signal.savgol_filter(np.array(filter_in),window,1)
    df_result[str(column+'_filtered')]=result
    return df_result

def rolling_reg_func(df_input,col='confirmed'):
    days_back=3
    result=df_input[col].rolling(window=days_back,min_periods=days_back)\
                        .apply(calculate_doubling_time_via_regression,raw=False)
    return result

# definig calculate savgol_filter which return to merged DataFrame
def calc_filtered_data(df_input,filter_on='confirmed'):
    must_contain=set(['state','country',filter_on])
    assert must_contain.issubset(set(df_input.columns)), ' Erro in calc_filtered_data not all columns in data frame'
    # Make a copy of df_input here otherwise it will be overwritten
    df_output=df_input.copy()

    df_filtered_result=df_output[['state','country',filter_on]].groupby(['state','country']).apply(savgol_filter)#.reset_index()
    df_output=pd.merge(df_output,df_filtered_result[[str(filter_on+'_filtered')]],left_index=True,right_index=True,how='left')
    return df_output.copy()

#defining a function for calculation of doubling rate
def calc_doubling_rate(df_input,filter_on='confirmed'):

    must_contain=set(['state','country',filter_on])
    assert must_contain.issubset(set(df_input.columns)), ' Erro in calc_filtered_data not all columns in data frame'
    df_doubling_rate= df_input.groupby(['state','country']).apply(rolling_reg_func,filter_on).reset_index()
    df_doubling_rate=df_doubling_rate.rename(columns={filter_on:filter_on+'_DR',
                             'level_2':'index'})
    #Performing merging on the index of big table and on the index column after groupby operation
    df_output=pd.merge(df_input,df_doubling_rate[['index',str(filter_on+'_DR')]],left_index=True,right_on=['index'],how='left')
    df_output=df_output.drop(columns=['index'])
    return df_output


if __name__ == '__main__':
    test_data_reg=np.array([2,4,6])
    result=calculate_doubling_time_via_regression(test_data_reg)
    print('The slope of regression plot is: '+str(result))

    df_JH_data=pd.read_csv('C:/Users/dhame/ds_covid-19/data/processed/COVID_relational_confirmed.csv',sep=';',parse_dates=[0])
    df_JH_data=df_JH_data.sort_values('date',ascending=True).copy()

    df_result_large=calc_filtered_data(df_JH_data)
    df_result_large=calc_doubling_rate(df_result_large)
    df_result_large=calc_doubling_rate(df_result_large,'confirmed_filtered')

    mask_threshold=df_result_large['confirmed']>100
    df_result_large['confirmed_filtered_DR']=df_result_large['confirmed_filtered_DR'].where(mask_threshold, other=np.NaN)
    df_result_large.to_csv('C:/Users/dhame/ds_covid-19/data/processed/COVID_final_set.csv',sep=';',index=False)
    #print(df_result_large[df_result_large['country']=='Germany'].tail())
    print('calculation has been performed successfully')
