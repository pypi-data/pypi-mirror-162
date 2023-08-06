import os
import re
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datupapi.configure.config import Config
from pandas.tseries.offsets import MonthEnd

class Stocks(Config):

        def __init__(self, config_file, logfile, log_path, *args, **kwargs):
            Config.__init__(self, config_file=config_file, logfile=logfile)
            self.log_path = log_path

        # SALES HISTORY-----------------------------------------------------------------------
        def extract_sales_history (self,df_prep, df_invopt,date_cols,location=True):  
            """
            Returns a data frame that incorporates the Sales History column into the inventory data frame.

            : param df_prep: Dataframe prepared for Forecast
            : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional)
            : param date_cols: Column name of date from df_prep
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : return df_extract: Dataframe with addition the column Sales History in the Inventory's Dataframe

            >>> df_extract = extract_sales_history (df_prep,df_invopt,date_cols='timestamp', location=self.use_location)
            >>> df_extract =
                                                Item    Location  DemandHistory
                                    idx0          85      905        200
                                    idx1          102     487        100
            """      
            try:
                df_prep_history = df_prep[df_prep[date_cols]== df_prep[date_cols].max()]
                if location:
                    dict_names = {'item_id':'Item',
                                    'location':'Location',
                                    'demand':'DemandHistory'}
                    df_prep_history.rename(columns=dict_names,inplace=True)

                    df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                    df_prep_history['Location'] = df_prep_history['Location'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_history[['Item','Location','DemandHistory']],on=['Item','Location'],how='left')
                else:
                    dict_names =  {'item_id':'Item',
                                    'demand':'DemandHistory'}
                    df_prep_history.rename(columns=dict_names,inplace=True)

                    df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)

                    df_extract = pd.merge(df_invopt,df_prep_history[['Item','DemandHistory']],on=['Item'],how='left')

            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_extract

        #FORECAST-----------------------------------------------------------------------

        def extract_forecast(self,df_fcst,df_invopt,date_cols,frequency_,months_,location,column_forecast='ForecastCollab',weeks_=4,join_='left'):      
            """
            Returns a data frame that incorporates the Suggested Forecast column into the inventory data frame.

            : param df_fcst: Forecast's Dataframe 
            : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), DemandHistory
            : param date_cols: Column name of date from df_fcst
            : param frequency_: Target frequency to the dataset
            : param months_: Number of months
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : param column_forecast: name of the column where the desired forecast is located 
            : param join_: type of join with forecast 

            >>> df_extract = extract_forecast (df_prep,df_fcst,df_invopt,date_cols='Date', location=self.use_location, frequency_= self.dataset_frequency,join_='left')
            >>> df_extract =
                                                Item    Location  DemandHistory   SuggestedForecast
                                    idx0          85      905         23              200
                                    idx1          102     487         95              100
            """ 
            try:
                if frequency_ == 'M':
                    df_fcst_sug = df_fcst[df_fcst[date_cols]>= (df_fcst[date_cols].max() - relativedelta(months=months_))]
                    if location:
                        df_fcst_sug = df_fcst_sug.groupby(['Item', 'Location'], as_index=False)\
                                                                        .agg({column_forecast: sum})\
                                                                        .reset_index(drop=True)
                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_invopt['Location'] = df_invopt['Location'].astype(str)
                        df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                        df_fcst_sug['Location'] = df_fcst_sug['Location'].astype(str)
                        df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location',column_forecast]],on=['Item','Location'],how=join_)
                    else:
                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                        df_extract = pd.merge(df_invopt,df_fcst_sug[['Item',column_forecast]],on=['Item'],how=join_)
                
                elif frequency_ == 'W':
                    df_fcst_sug = df_fcst[df_fcst[date_cols]>= (df_fcst[date_cols].max() - relativedelta(weeks=weeks_))]
                    if location:
                        df_fcst_sug = df_fcst_sug.groupby(['Item', 'Location'], as_index=False)\
                                                                        .agg({column_forecast: sum})\
                                                                        .reset_index(drop=True)
                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_invopt['Location'] = df_invopt['Location'].astype(str)
                        df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                        df_fcst_sug['Location'] = df_fcst_sug['Location'].astype(str)
                        df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location',column_forecast]],on=['Item','Location'],how=join_)
                    else:
                        df_fcst_sug = df_fcst_sug.groupby(['Item'], as_index=False)\
                                              .agg({column_forecast: sum})\
                                              .reset_index(drop=True)
                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                        df_extract = pd.merge(df_invopt,df_fcst_sug[['Item',column_forecast]],on=['Item'],how=join_)

            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_extract

        # FORECAST ---------------------------------------------------------------------

        def suggested_forecast(self,df_LeadTimes ,df_Forecast,df_Prep,df_inv,column_forecast,frequency_,location,actualdate,join_='left'):
            """
            Returns a data frame that incorporates the Suggested Forecast column into the inventory data frame, taking into account delivery times 

            : param df_LeadTimes: LeadTime's Dataframe
            : param df_Forecast: Forecast's Dataframe 
            : param df_Prep: Dataframe prepared for Forecast
            : param df_inv: Inventory's Dataframe with the columns Item, Location(Optional), DemandHistory
            : param column_forecast: name of the column where the desired forecast is located 
            : param frequency_: Target frequency to the dataset
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : param actualdate: current day   
            : param join_: type of join with forecast   
            
            
            >>> df_forecats = suggested_forecast(df_LeadTimes=df_lead_time, 
                                                            df_Forecast=df_fcst,
                                                            df_Prep=df_prep,
                                                            df_inv=df_inv,
                                                            column_forecast='SuggestedForecast',
                                                            frequency_ = 'W',
                                                            location = True/False,
                                                            actualdate=timestamp,
                                                            join_='left')
            >>> suggested_forecast =
                                                Item    Location  DemandHistory   SuggestedForecast
                                    idx0          85      905         23              200
                                    idx1          102     487         95              100
            """ 
            try:
                df_lead_cruce= df_LeadTimes.copy()
                df_lead_cruce=df_lead_cruce.groupby(['Item','ReorderDays'], as_index=False).mean()
                df_lead_cruce=df_lead_cruce[['Item','ReorderDays']].drop_duplicates() 
                df_fcst_cruce = df_Forecast.copy()
                df_final_fcst = pd.merge(df_fcst_cruce,df_lead_cruce,on=['Item'],how='left')  

                d1 = pd.Period(str('28'+'-02-'+actualdate[0:4]),freq='M').end_time.date()
                d2 = str('29'+'-02-'+actualdate[0:4])

                if (df_Prep['timestamp'].max()).date() == d1:
                  pmonth=1
                  finfebrero='28'
                elif str((df_Prep['timestamp'].max()).date()) == d2:
                  pmonth=1
                  finfebrero='29'
                else:
                  pmonth=0
                  finfebrero='28'

                lastdayDict={'1':'31', '2': finfebrero, '3':'31', '4':'30', '5':'31', '6':'30', '7':'31', '8':'31', '9':'30', '10':'31', '11':'30', '12':'31'}
                DayOfMonth= int(actualdate[6:8])
                Month=str(int(actualdate[4:6]))
                DaysOfMonth = int(lastdayDict[Month])
                DayOfWeek = int(datetime.datetime.today().weekday())+1 
                DaysOfWeek =7 

                columns_group=list(df_inv.columns)

                if frequency_ == 'M':
                  df_final_fcst.loc[df_final_fcst['ReorderDays'].isnull(),'ReorderDays'] = 29
                  df_final_fcst['Periods'] = (df_final_fcst['ReorderDays']+DayOfMonth-1)//DaysOfMonth

                  #CURRENT PERIOD --------------------------------------------------------------
                  df_fcst_current = df_final_fcst[(df_final_fcst['Date']>df_Prep['timestamp'].max())&
                      (df_final_fcst['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                  df_fcst_current=df_fcst_current.iloc[:,:18]
                  df_fcst_current=df_fcst_current.drop_duplicates()
                  df_extract_fcst_current = self.extract_forecast(df_fcst_current, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                      date_cols = 'Date',months_= 1,weeks_= 4,join_=join_).fillna(0) 
                  df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({column_forecast:sum})           
                  df_extract_fcst_current[column_forecast]=df_extract_fcst_current[column_forecast]*(1-DayOfMonth/DaysOfMonth)
                  df_extract_fcst_current.rename(columns={column_forecast:'Current'},inplace=True)
                  df_extract_fcst_current=df_extract_fcst_current[['Item','Current']]


                  # LESS THAN A PERIOD-----------------------------------------------------
                  df_fcst_0 = df_final_fcst[df_final_fcst['Periods'] == 0]
                  if not df_fcst_0.empty:
                      df_fcst_0 = df_fcst_0[(df_fcst_0['Date']>df_Prep['timestamp'].max())&
                                  (df_fcst_0['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                      df_fcst_0=df_fcst_0.iloc[:,:18]
                      df_fcst_0=df_fcst_0.drop_duplicates()
                      df_extract_forecast_0 = self.extract_forecast(df_fcst_0, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                              date_cols = 'Date',months_= 1,weeks_= 4,join_=join_).fillna(0) 
                      df_final_0 = df_extract_forecast_0.groupby(columns_group, as_index=False).agg({column_forecast:sum})  
                      df_final_0 [column_forecast]=df_final_0 [column_forecast]*(1-DayOfMonth/DaysOfMonth)
                    
                  if df_fcst_0.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_0 =  pd.DataFrame(columns = columns)

                  # ONE PERIOD-----------------------------------------------------
                  df_fcst_1 = df_final_fcst[df_final_fcst['Periods'] == 1]
                  if not df_fcst_1.empty:
                      itemslist_1=list(df_fcst_1['Item'].unique())
                      df_fcst_1_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_1)]
                      
                      df_fcst_1 = df_fcst_1[(df_fcst_1['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                      (df_fcst_1['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=2)+MonthEnd(pmonth)))] 
                      df_fcst_1a=df_fcst_1.iloc[:,:18].copy()
                      df_fcst_1a=df_fcst_1a.drop_duplicates()
                      df_extract_forecast1 = self.extract_forecast(df_fcst_1a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 2,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast1 = df_extract_forecast1.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast1.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_1b=df_fcst_1[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_1= pd.merge(df_extract_forecast1,df_fcst_1b,on=['Item'],how='left')
                      df_final_1= pd.merge(df_final_1,df_fcst_1_current,on=['Item'],how='left')
                      df_final_1[column_forecast]=df_final_1['Current'] + df_final_1['Next']*((df_final_1['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_1['Periods']*DaysOfMonth))
                      df_final_1 = df_final_1.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_1.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_1 = pd.DataFrame(columns = columns)

                  # TWO PERIODS-----------------------------------------------------
                  df_fcst_2 = df_final_fcst[df_final_fcst['Periods'] == 2]
                  if not df_fcst_2.empty:
                      itemslist_2=list(df_fcst_2['Item'].unique())
                      df_fcst_2_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_2)]
                      
                      df_fcst_2 = df_fcst_2[(df_fcst_2['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_2['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=3)+MonthEnd(pmonth)))]    
                      df_fcst_2a=df_fcst_2.iloc[:,:18].copy()
                      df_fcst_2a=df_fcst_2a.drop_duplicates()
                      df_extract_forecast2 = self.extract_forecast(df_fcst_2a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 3,weeks_= 3,join_=join_).fillna(0) 
                      df_extract_forecast2 = df_extract_forecast2.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast2.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_2b=df_fcst_2[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_2= pd.merge(df_extract_forecast2,df_fcst_2b,on=['Item'],how='left')
                      df_final_2= pd.merge(df_final_2,df_fcst_2_current,on=['Item'],how='left')
                      df_final_2[column_forecast]=df_final_2['Current'] + df_final_2['Next']*((df_final_2['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_2['Periods']*DaysOfMonth))
                      df_final_2 = df_final_2.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_2.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_2 = pd.DataFrame(columns = columns)
                  
                  # THREE PERIODS-----------------------------------------------------
                  df_fcst_3 = df_final_fcst[df_final_fcst['Periods'] == 3]
                  if not df_fcst_3.empty:
                      itemslist_3=list(df_fcst_3['Item'].unique())
                      df_fcst_3_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_3)]
                      
                      df_fcst_3 = df_fcst_3[(df_fcst_3['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_3['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=4)+MonthEnd(pmonth)))]    
                      df_fcst_3a=df_fcst_3.iloc[:,:18].copy()
                      df_fcst_3a=df_fcst_3a.drop_duplicates()
                      df_extract_forecast3 = self.extract_forecast(df_fcst_3a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 4,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast3 = df_extract_forecast3.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast3.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_3b=df_fcst_3[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_3= pd.merge(df_extract_forecast3,df_fcst_3b,on=['Item'],how='left')
                      df_final_3= pd.merge(df_final_3,df_fcst_3_current,on=['Item'],how='left')
                      df_final_3[column_forecast]=df_final_3['Current'] + df_final_3['Next']*((df_final_3['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_3['Periods']*DaysOfMonth))
                      df_final_3 = df_final_3.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_3.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_3 = pd.DataFrame(columns = columns)
                  
                  # FOUR PERIODS-----------------------------------------------------
                  df_fcst_4 = df_final_fcst[df_final_fcst['Periods'] == 4]
                  if not df_fcst_4.empty:
                      itemslist_4=list(df_fcst_4['Item'].unique())
                      df_fcst_4_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_4)]
                      
                      df_fcst_4 = df_fcst_4[(df_fcst_4['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_4['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=5)+MonthEnd(pmonth)))]  
                      df_fcst_4a=df_fcst_4.iloc[:,:18].copy()
                      df_fcst_4a=df_fcst_4a.drop_duplicates()
                      df_extract_forecast4 = self.extract_forecast(df_fcst_4a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 5,weeks_= 5,join_=join_).fillna(0) 
                      df_extract_forecast4 = df_extract_forecast4.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast4.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_4b=df_fcst_4[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_4= pd.merge(df_extract_forecast4,df_fcst_4b,on=['Item'],how='left')
                      df_final_4= pd.merge(df_final_4,df_fcst_4_current,on=['Item'],how='left')
                      df_final_4[column_forecast]=df_final_4['Current'] + df_final_4['Next']*((df_final_4['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_4['Periods']*DaysOfMonth))
                      df_final_4 = df_final_4.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_4.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_4 = pd.DataFrame(columns = columns)
                  
                  # FIVE PERIODS-----------------------------------------------------
                  df_fcst_5 = df_final_fcst[df_final_fcst['Periods'] == 5]
                  if not df_fcst_5.empty:
                      itemslist_5=list(df_fcst_5['Item'].unique())
                      df_fcst_5_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_5)]
                      
                      df_fcst_5 = df_fcst_5[(df_fcst_5['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_5['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=6)+MonthEnd(pmonth)))]
                      df_fcst_5a=df_fcst_5.iloc[:,:18].copy()
                      df_fcst_5a=df_fcst_5a.drop_duplicates()
                      df_extract_forecast5 = self.extract_forecast(df_fcst_5a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 6,weeks_= 6,join_=join_).fillna(0) 
                      df_extract_forecast5 = df_extract_forecast5.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast5.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_5b=df_fcst_5[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_5= pd.merge(df_extract_forecast5,df_fcst_5b,on=['Item'],how='left')
                      df_final_5= pd.merge(df_final_5,df_fcst_5_current,on=['Item'],how='left')
                      df_final_5[column_forecast]=df_final_5['Current'] + df_final_5['Next']*((df_final_5['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_5['Periods']*DaysOfMonth))
                      df_final_5 = df_final_5.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_5.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_5 = pd.DataFrame(columns = columns)

                  # SIX PERIODS-----------------------------------------------------
                  df_fcst_6 = df_final_fcst[df_final_fcst['Periods'] == 6]
                  if not df_fcst_6.empty:
                      itemslist_6=list(df_fcst_6['Item'].unique())
                      df_fcst_6_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_6)]
                      
                      df_fcst_6 = df_fcst_6[(df_fcst_6['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_6['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=7)+MonthEnd(pmonth)))]   
                      df_fcst_6a=df_fcst_6.iloc[:,:18].copy()
                      df_fcst_6a=df_fcst_6a.drop_duplicates()
                      df_extract_forecast6 = self.extract_forecast(df_fcst_6a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 7,weeks_= 7,join_=join_).fillna(0) 
                      df_extract_forecast6 = df_extract_forecast6.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast6.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_6b=df_fcst_6[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_6= pd.merge(df_extract_forecast6,df_fcst_6b,on=['Item'],how='left')
                      df_final_6= pd.merge(df_final_6,df_fcst_6_current,on=['Item'],how='left')
                      df_final_6[column_forecast]=df_final_6['Current'] + df_final_6['Next']*((df_final_6['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_6['Periods']*DaysOfMonth))
                      df_final_6 = df_final_6.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_6.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_6 = pd.DataFrame(columns = columns)

                  # SEVEN PERIODS-----------------------------------------------------
                  df_fcst_7 = df_final_fcst[df_final_fcst['Periods'] == 7]
                  if not df_fcst_7.empty:
                      itemslist_7=list(df_fcst_7['Item'].unique())
                      df_fcst_7_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_7)]
                      
                      df_fcst_7= df_fcst_7[(df_fcst_7['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                      df_fcst_7a=df_fcst_7.iloc[:,:18].copy()
                      df_fcst_7a=df_fcst_7a.drop_duplicates()
                      df_extract_forecast7 = self.extract_forecast(df_fcst_7a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 12,weeks_= 12,join_=join_).fillna(0) 
                      df_extract_forecast7 = df_extract_forecast7.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast7.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_7b=df_fcst_7[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_7= pd.merge(df_extract_forecast7,df_fcst_7b,on=['Item'],how='left')
                      df_final_7= pd.merge(df_final_7,df_fcst_7_current,on=['Item'],how='left')
                      df_final_7[column_forecast]=df_final_7['Current'] + df_final_7['Next']*((df_final_7['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_7['Periods']*DaysOfMonth))
                      df_final_7 = df_final_7.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_7.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_7 = pd.DataFrame(columns = columns)

                
                
                if frequency_ == 'W':
                  df_final_fcst.loc[df_final_fcst['ReorderDays'].isnull(),'ReorderDays'] = 6
                  df_final_fcst['Periods'] = (df_final_fcst['ReorderDays']+DayOfWeek)//DaysOfWeek

                  #CURRENT PERIOD --------------------------------------------------------------
                  df_fcst_current = df_final_fcst[(df_final_fcst['Date']>df_Prep['timestamp'].max())&
                              (df_final_fcst['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                  df_fcst_current=df_fcst_current.iloc[:,:18]
                  df_fcst_current=df_fcst_current.drop_duplicates()
                  df_extract_fcst_current = self.extract_forecast(df_fcst_current, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                        date_cols = 'Date',months_= 1,weeks_= 1,join_=join_).fillna(0) 
                  df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({column_forecast:sum})
                  df_extract_fcst_current[column_forecast]=df_extract_fcst_current[column_forecast] *(1-DayOfWeek/DaysOfWeek)
                  df_extract_fcst_current.rename(columns={column_forecast:'Current'},inplace=True)
                  df_extract_fcst_current=df_extract_fcst_current[['Item','Current']]

                  # LESS THAN A PERIOD-----------------------------------------------------
                  df_fcst_0 = df_final_fcst[df_final_fcst['Periods'] == 0]
                  if not df_fcst_0.empty:
                      df_fcst_0 = df_fcst_0[(df_fcst_0['Date']>df_Prep['timestamp'].max())&
                                (df_fcst_0['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                      df_fcst_0=df_fcst_0.iloc[:,:18]
                      df_fcst_0=df_fcst_0.drop_duplicates()
                      df_extract_forecast_0 = self.extract_forecast(df_fcst_0, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                              date_cols = 'Date',months_= 1,weeks_= 1,join_=join_).fillna(0) 
                      df_final_0 = df_extract_forecast_0.groupby(columns_group, as_index=False).agg({column_forecast:sum})
                      df_final_0[column_forecast]=df_final_0[column_forecast] *(1-DayOfWeek/DaysOfWeek)
                  
                  if df_fcst_0.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_0 =  pd.DataFrame(columns = columns)
                  
                  # ONE PERIOD-----------------------------------------------------
                  df_fcst_1 = df_final_fcst[df_final_fcst['Periods'] == 1]
                  if not df_fcst_1.empty:
                      itemslist_1=list(df_fcst_1['Item'].unique())
                      df_fcst_1_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_1)]
                      
                      df_fcst_1 = df_fcst_1[(df_fcst_1['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_1['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=2)))]
                      df_fcst_1a=df_fcst_1.iloc[:,:18].copy()
                      df_fcst_1a=df_fcst_1a.drop_duplicates()
                      df_extract_forecast1 = self.extract_forecast(df_fcst_1a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 2,weeks_= 2,join_=join_).fillna(0) 
                      df_extract_forecast1 = df_extract_forecast1.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast1.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_1b=df_fcst_1[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_1= pd.merge(df_extract_forecast1,df_fcst_1b,on=['Item'],how='left')
                      df_final_1= pd.merge(df_final_1,df_fcst_1_current,on=['Item'],how='left')
                      df_final_1[column_forecast]=df_final_1['Current'] + df_final_1['Next']*((df_final_1['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_1['Periods']*DaysOfWeek))
                      df_final_1 = df_final_1.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_1.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_1 = pd.DataFrame(columns = columns)

                  # TWO PERIODS-----------------------------------------------------
                  df_fcst_2 = df_final_fcst[df_final_fcst['Periods'] == 2]
                  if not df_fcst_2.empty:
                      itemslist_2=list(df_fcst_2['Item'].unique())
                      df_fcst_2_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_2)]
                      
                      df_fcst_2 = df_fcst_2[(df_fcst_2['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_2['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=3)))]
                      df_fcst_2a=df_fcst_2.iloc[:,:18].copy()
                      df_fcst_2a=df_fcst_2a.drop_duplicates()
                      df_extract_forecast2 = self.extract_forecast(df_fcst_2a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 3,weeks_= 3,join_=join_).fillna(0) 
                      df_extract_forecast2 = df_extract_forecast2.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast2.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_2b=df_fcst_2[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_2= pd.merge(df_extract_forecast2,df_fcst_2b,on=['Item'],how='left')
                      df_final_2= pd.merge(df_final_2,df_fcst_2_current,on=['Item'],how='left')
                      df_final_2[column_forecast]=df_final_2['Current'] + df_final_2['Next']*((df_final_2['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_2['Periods']*DaysOfWeek))
                      df_final_2 = df_final_2.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_2.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_2 = pd.DataFrame(columns = columns)
                  
                  # THREE PERIODS-----------------------------------------------------
                  df_fcst_3 = df_final_fcst[df_final_fcst['Periods'] == 3]
                  if not df_fcst_3.empty:
                      itemslist_3=list(df_fcst_3['Item'].unique())
                      df_fcst_3_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_3)]
                      
                      df_fcst_3 = df_fcst_3[(df_fcst_3['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_3['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=4)))]
                      df_fcst_3a=df_fcst_3.iloc[:,:18].copy()
                      df_fcst_3a=df_fcst_3a.drop_duplicates()
                      df_extract_forecast3 = self.extract_forecast(df_fcst_3a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 4,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast3 = df_extract_forecast3.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast3.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_3b=df_fcst_3[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_3= pd.merge(df_extract_forecast3,df_fcst_3b,on=['Item'],how='left')
                      df_final_3= pd.merge(df_final_3,df_fcst_3_current,on=['Item'],how='left')
                      df_final_3[column_forecast]=df_final_3['Current'] + df_final_3['Next']*((df_final_3['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_3['Periods']*DaysOfWeek))
                      df_final_3 = df_final_3.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_3.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_3 = pd.DataFrame(columns = columns)
                  
                  # FOUR PERIODS-----------------------------------------------------
                  df_fcst_4 = df_final_fcst[df_final_fcst['Periods'] == 4]
                  if not df_fcst_4.empty:
                      itemslist_4=list(df_fcst_4['Item'].unique())
                      df_fcst_4_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_4)]
                      
                      df_fcst_4 = df_fcst_4[(df_fcst_4['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_4['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=5)))]
                      df_fcst_4a=df_fcst_4.iloc[:,:18].copy()
                      df_fcst_4a=df_fcst_4a.drop_duplicates()
                      df_extract_forecast4 = self.extract_forecast(df_fcst_4a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 5,weeks_= 5,join_=join_).fillna(0) 
                      df_extract_forecast4 = df_extract_forecast4.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast4.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_4b=df_fcst_4[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_4= pd.merge(df_extract_forecast4,df_fcst_4b,on=['Item'],how='left')
                      df_final_4= pd.merge(df_final_4,df_fcst_4_current,on=['Item'],how='left')
                      df_final_4[column_forecast]=df_final_4['Current'] + df_final_4['Next']*((df_final_4['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_4['Periods']*DaysOfWeek))
                      df_final_4 = df_final_4.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_4.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_4 = pd.DataFrame(columns = columns)
                  
                  # FIVE PERIODS-----------------------------------------------------
                  df_fcst_5 = df_final_fcst[df_final_fcst['Periods'] == 5]
                  if not df_fcst_5.empty:
                      itemslist_5=list(df_fcst_5['Item'].unique())
                      df_fcst_5_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_5)]
                      
                      df_fcst_5 = df_fcst_5[(df_fcst_5['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_5['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=6)))]
                      df_fcst_5a=df_fcst_5.iloc[:,:18].copy()
                      df_fcst_5a=df_fcst_5a.drop_duplicates()
                      df_extract_forecast5 = self.extract_forecast(df_fcst_5a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 6,weeks_= 6,join_=join_).fillna(0) 
                      df_extract_forecast5 = df_extract_forecast5.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast5.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_5b=df_fcst_5[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_5= pd.merge(df_extract_forecast5,df_fcst_5b,on=['Item'],how='left')
                      df_final_5= pd.merge(df_final_5,df_fcst_5_current,on=['Item'],how='left')
                      df_final_5[column_forecast]=df_final_5['Current'] + df_final_5['Next']*((df_final_5['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_5['Periods']*DaysOfWeek))
                      df_final_5 = df_final_5.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_5.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_5 = pd.DataFrame(columns = columns)

                  # SIX PERIODS-----------------------------------------------------
                  df_fcst_6 = df_final_fcst[df_final_fcst['Periods'] == 6]
                  if not df_fcst_6.empty:
                      itemslist_6=list(df_fcst_6['Item'].unique())
                      df_fcst_6_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_6)]
                      
                      df_fcst_6 = df_fcst_6[(df_fcst_6['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_6['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=7)))]
                      df_fcst_6a=df_fcst_6.iloc[:,:18].copy()
                      df_fcst_6a=df_fcst_6a.drop_duplicates()
                      df_extract_forecast6 = self.extract_forecast(df_fcst_6a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 7,weeks_= 7,join_=join_).fillna(0) 
                      df_extract_forecast6 = df_extract_forecast6.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast6.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_6b=df_fcst_6[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_6= pd.merge(df_extract_forecast6,df_fcst_6b,on=['Item'],how='left')
                      df_final_6= pd.merge(df_final_6,df_fcst_6_current,on=['Item'],how='left')
                      df_final_6[column_forecast]=df_final_6['Current'] + df_final_6['Next']*((df_final_6['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_6['Periods']*DaysOfWeek))
                      df_final_6 = df_final_6.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_6.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_6 = pd.DataFrame(columns = columns)

                  # SEVEN PERIODS-----------------------------------------------------
                  df_fcst_7 = df_final_fcst[df_final_fcst['Periods'] == 7]
                  if not df_fcst_7.empty:
                      itemslist_7=list(df_fcst_7['Item'].unique())
                      df_fcst_7_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_7)]
                      
                      df_fcst_7 = df_fcst_7[(df_fcst_7['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                      df_fcst_7a=df_fcst_7.iloc[:,:18].copy()
                      df_fcst_7a=df_fcst_7a.drop_duplicates()
                      df_extract_forecast7 = self.extract_forecast(df_fcst_7a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 12,weeks_= 12,join_=join_).fillna(0) 
                      df_extract_forecast7 = df_extract_forecast7.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast7.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_7b=df_fcst_7[['Item','ReorderDays','Periods']].drop_duplicates() 
                      df_final_7= pd.merge(df_extract_forecast7,df_fcst_7b,on=['Item'],how='left')
                      df_final_7= pd.merge(df_final_7,df_fcst_7_current,on=['Item'],how='left')
                      df_final_7[column_forecast]=df_final_7['Current'] + df_final_7['Next']*((df_final_7['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_7['Periods']*DaysOfWeek))
                      df_final_7 = df_final_7.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_7.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_7 = pd.DataFrame(columns = columns)

                # Forecast -----------------------------------------------------------------  
                df_fcst = pd.concat([df_final_0,df_final_1,df_final_2,df_final_3,df_final_4,df_final_5,df_final_6,df_final_7],ignore_index=True)
                df_fcst = df_fcst.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                
            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_fcst

        def suggested_forecast_location(self,df_LeadTimes,df_Forecast,df_Prep,df_inv,column_forecast,frequency_,location,actualdate,join_='left'):      
            """
            Returns a data frame that incorporates the Suggested Forecast column into the inventory data frame, taking into account delivery times and location

            : param df_LeadTimes: LeadTime's Dataframe
            : param df_Forecast: Forecast's Dataframe 
            : param df_Prep: Dataframe prepared for Forecast
            : param df_inv : Inventory's Dataframe with the columns Item, Location(Optional), DemandHistory
            : param column_forecast: name of the column where the desired forecast is located 
            : param frequency_: Target frequency to the dataset
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : param actualdate: current day   
            : param join_: type of join with forecast  
            
            
            >>> df_forecast = suggested_forecast_location(df_LeadTimes=df_lead_time, 
                                                            df_Forecast=df_fcst,
                                                            df_Prep=df_prep,
                                                            df_inv=df_inv,
                                                            column_forecast='SuggestedForecast',
                                                            frequency_ = 'W',
                                                            location = True/False,
                                                            actualdate=timestamp,
                                                            join_='left')
            >>> suggested_forecast_location =
                                                Item    Location  DemandHistory   SuggestedForecast
                                    idx0          85      905         23              200
                                    idx1          102     487         95              100
            """ 
            try:
                df_lead_cruce= df_LeadTimes.copy()
                df_lead_cruce=df_lead_cruce.groupby(['Item','Location','ReorderDays'], as_index=False).mean()
                df_lead_cruce=df_lead_cruce[['Item','Location','ReorderDays']].drop_duplicates() 
                df_fcst_cruce = df_Forecast.copy()
                df_fcst_cruce['Location']=df_fcst_cruce['Location'].astype(str)
                df_final_fcst = pd.merge(df_fcst_cruce,df_lead_cruce,on=['Item','Location'],how='left')  

                d1 = pd.Period(str('28'+'-02-'+actualdate[0:4]),freq='M').end_time.date()
                d2 = str('29'+'-02-'+actualdate[0:4])

                if (df_Prep['timestamp'].max()).date() == d1:
                  pmonth=1
                  finfebrero='28'
                elif str((df_Prep['timestamp'].max()).date()) == d2:
                  pmonth=1
                  finfebrero='29'
                else:
                  pmonth=0
                  finfebrero='28'

                lastdayDict={'1':'31', '2': finfebrero, '3':'31', '4':'30', '5':'31', '6':'30', '7':'31', '8':'31', '9':'30', '10':'31', '11':'30', '12':'31'}
                DayOfMonth= int(actualdate[6:8])
                Month=str(int(actualdate[4:6]))
                DaysOfMonth = int(lastdayDict[Month])
                DayOfWeek = int(datetime.datetime.today().weekday())+1 
                DaysOfWeek =7 

                columns_group=list(df_inv.columns)

                if frequency_ == 'M':
                  df_final_fcst.loc[df_final_fcst['ReorderDays'].isnull(),'ReorderDays'] = 29
                  df_final_fcst['Periods'] = (df_final_fcst['ReorderDays']+DayOfMonth-1)//DaysOfMonth

                  #CURRENT PERIOD --------------------------------------------------------------
                  df_fcst_current = df_final_fcst[(df_final_fcst['Date']>df_Prep['timestamp'].max())&
                      (df_final_fcst['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                  df_fcst_current=df_fcst_current.iloc[:,:19]
                  df_fcst_current=df_fcst_current.drop_duplicates()
                  df_extract_fcst_current = self.extract_forecast(df_fcst_current, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                      date_cols = 'Date',months_= 1,weeks_= 4,join_=join_).fillna(0) 
                  df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({column_forecast:sum})           
                  df_extract_fcst_current[column_forecast]=df_extract_fcst_current[column_forecast]*(1-DayOfMonth/DaysOfMonth)
                  df_extract_fcst_current.rename(columns={column_forecast:'Current'},inplace=True)
                  df_extract_fcst_current=df_extract_fcst_current[['Item','Location','Current']]


                  # LESS THAN A PERIOD-----------------------------------------------------
                  df_fcst_0 = df_final_fcst[df_final_fcst['Periods'] == 0]
                  if not df_fcst_0.empty:
                      df_fcst_0 = df_fcst_0[(df_fcst_0['Date']>df_Prep['timestamp'].max())&
                                  (df_fcst_0['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                      df_fcst_0=df_fcst_0.iloc[:,:19]
                      df_fcst_0=df_fcst_0.drop_duplicates()
                      df_extract_forecast_0 = self.extract_forecast(df_fcst_0, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                              date_cols = 'Date',months_= 1,weeks_= 4,join_=join_).fillna(0) 
                      df_final_0 = df_extract_forecast_0.groupby(columns_group, as_index=False).agg({column_forecast:sum})  
                      df_final_0 [column_forecast]=df_final_0 [column_forecast]*(1-DayOfMonth/DaysOfMonth)
                    
                  if df_fcst_0.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_0 =  pd.DataFrame(columns = columns)

                  # ONE PERIOD-----------------------------------------------------
                  df_fcst_1 = df_final_fcst[df_final_fcst['Periods'] == 1]
                  if not df_fcst_1.empty:
                      itemslist_1=list(df_fcst_1['Item'].unique())
                      df_fcst_1_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_1)]
                      
                      df_fcst_1 = df_fcst_1[(df_fcst_1['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                      (df_fcst_1['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=2)+MonthEnd(pmonth)))] 
                      df_fcst_1a=df_fcst_1.iloc[:,:19].copy()
                      df_fcst_1a=df_fcst_1a.drop_duplicates()
                      df_extract_forecast1 = self.extract_forecast(df_fcst_1a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 2,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast1 = df_extract_forecast1.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast1.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_1b=df_fcst_1[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_1= pd.merge(df_extract_forecast1,df_fcst_1b,on=['Item','Location'],how='left')
                      df_final_1= pd.merge(df_final_1,df_fcst_1_current,on=['Item','Location'],how='left')
                      df_final_1[column_forecast]=df_final_1['Current'] + df_final_1['Next']*((df_final_1['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_1['Periods']*DaysOfMonth))
                      df_final_1 = df_final_1.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_1.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_1 = pd.DataFrame(columns = columns)

                  # TWO PERIODS-----------------------------------------------------
                  df_fcst_2 = df_final_fcst[df_final_fcst['Periods'] == 2]
                  if not df_fcst_2.empty:
                      itemslist_2=list(df_fcst_2['Item'].unique())
                      df_fcst_2_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_2)]
                      
                      df_fcst_2 = df_fcst_2[(df_fcst_2['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_2['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=3)+MonthEnd(pmonth)))]    
                      df_fcst_2a=df_fcst_2.iloc[:,:19].copy()
                      df_fcst_2a=df_fcst_2a.drop_duplicates()
                      df_extract_forecast2 = self.extract_forecast(df_fcst_2a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 3,weeks_= 3,join_=join_).fillna(0) 
                      df_extract_forecast2 = df_extract_forecast2.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast2.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_2b=df_fcst_2[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_2= pd.merge(df_extract_forecast2,df_fcst_2b,on=['Item','Location'],how='left')
                      df_final_2= pd.merge(df_final_2,df_fcst_2_current,on=['Item','Location'],how='left')
                      df_final_2[column_forecast]=df_final_2['Current'] + df_final_2['Next']*((df_final_2['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_2['Periods']*DaysOfMonth))
                      df_final_2 = df_final_2.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_2.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_2 = pd.DataFrame(columns = columns)
                  
                  # THREE PERIODS-----------------------------------------------------
                  df_fcst_3 = df_final_fcst[df_final_fcst['Periods'] == 3]
                  if not df_fcst_3.empty:
                      itemslist_3=list(df_fcst_3['Item'].unique())
                      df_fcst_3_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_3)]
                      
                      df_fcst_3 = df_fcst_3[(df_fcst_3['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_3['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=4)+MonthEnd(pmonth)))]    
                      df_fcst_3a=df_fcst_3.iloc[:,:19].copy()
                      df_fcst_3a=df_fcst_3a.drop_duplicates()
                      df_extract_forecast3 = self.extract_forecast(df_fcst_3a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 4,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast3 = df_extract_forecast3.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast3.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_3b=df_fcst_3[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_3= pd.merge(df_extract_forecast3,df_fcst_3b,on=['Item','Location'],how='left')
                      df_final_3= pd.merge(df_final_3,df_fcst_3_current,on=['Item','Location'],how='left')
                      df_final_3[column_forecast]=df_final_3['Current'] + df_final_3['Next']*((df_final_3['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_3['Periods']*DaysOfMonth))
                      df_final_3 = df_final_3.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_3.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_3 = pd.DataFrame(columns = columns)
                  
                  # FOUR PERIODS-----------------------------------------------------
                  df_fcst_4 = df_final_fcst[df_final_fcst['Periods'] == 4]
                  if not df_fcst_4.empty:
                      itemslist_4=list(df_fcst_4['Item'].unique())
                      df_fcst_4_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_4)]
                      
                      df_fcst_4 = df_fcst_4[(df_fcst_4['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_4['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=5)+MonthEnd(pmonth)))]  
                      df_fcst_4a=df_fcst_4.iloc[:,:19].copy()
                      df_fcst_4a=df_fcst_4a.drop_duplicates()
                      df_extract_forecast4 = self.extract_forecast(df_fcst_4a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 5,weeks_= 5,join_=join_).fillna(0) 
                      df_extract_forecast4 = df_extract_forecast4.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast4.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_4b=df_fcst_4[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_4= pd.merge(df_extract_forecast4,df_fcst_4b,on=['Item','Location'],how='left')
                      df_final_4= pd.merge(df_final_4,df_fcst_4_current,on=['Item','Location'],how='left')
                      df_final_4[column_forecast]=df_final_4['Current'] + df_final_4['Next']*((df_final_4['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_4['Periods']*DaysOfMonth))
                      df_final_4 = df_final_4.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_4.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_4 = pd.DataFrame(columns = columns)
                  
                  # FIVE PERIODS-----------------------------------------------------
                  df_fcst_5 = df_final_fcst[df_final_fcst['Periods'] == 5]
                  if not df_fcst_5.empty:
                      itemslist_5=list(df_fcst_5['Item'].unique())
                      df_fcst_5_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_5)]
                      
                      df_fcst_5 = df_fcst_5[(df_fcst_5['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_5['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=6)+MonthEnd(pmonth)))]
                      df_fcst_5a=df_fcst_5.iloc[:,:19].copy()
                      df_fcst_5a=df_fcst_5a.drop_duplicates()
                      df_extract_forecast5 = self.extract_forecast(df_fcst_5a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 6,weeks_= 6,join_=join_).fillna(0) 
                      df_extract_forecast5 = df_extract_forecast5.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast5.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_5b=df_fcst_5[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_5= pd.merge(df_extract_forecast5,df_fcst_5b,on=['Item','Location'],how='left')
                      df_final_5= pd.merge(df_final_5,df_fcst_5_current,on=['Item','Location'],how='left')
                      df_final_5[column_forecast]=df_final_5['Current'] + df_final_5['Next']*((df_final_5['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_5['Periods']*DaysOfMonth))
                      df_final_5 = df_final_5.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_5.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_5 = pd.DataFrame(columns = columns)

                  # SIX PERIODS-----------------------------------------------------
                  df_fcst_6 = df_final_fcst[df_final_fcst['Periods'] == 6]
                  if not df_fcst_6.empty:
                      itemslist_6=list(df_fcst_6['Item'].unique())
                      df_fcst_6_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_6)]
                      
                      df_fcst_6 = df_fcst_6[(df_fcst_6['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))&
                                              (df_fcst_6['Date']<= (df_Prep['timestamp'].max()+relativedelta(months=7)+MonthEnd(pmonth)))]   
                      df_fcst_6a=df_fcst_6.iloc[:,:19].copy()
                      df_fcst_6a=df_fcst_6a.drop_duplicates()
                      df_extract_forecast6 = self.extract_forecast(df_fcst_6a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 7,weeks_= 7,join_=join_).fillna(0) 
                      df_extract_forecast6 = df_extract_forecast6.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast6.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_6b=df_fcst_6[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_6= pd.merge(df_extract_forecast6,df_fcst_6b,on=['Item','Location'],how='left')
                      df_final_6= pd.merge(df_final_6,df_fcst_6_current,on=['Item','Location'],how='left')
                      df_final_6[column_forecast]=df_final_6['Current'] + df_final_6['Next']*((df_final_6['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_6['Periods']*DaysOfMonth))
                      df_final_6 = df_final_6.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_6.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_6 = pd.DataFrame(columns = columns)

                  # SEVEN PERIODS-----------------------------------------------------
                  df_fcst_7 = df_final_fcst[df_final_fcst['Periods'] == 7]
                  if not df_fcst_7.empty:
                      itemslist_7=list(df_fcst_7['Item'].unique())
                      df_fcst_7_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_7)]
                      
                      df_fcst_7= df_fcst_7[(df_fcst_7['Date']>(df_Prep['timestamp'].max()+relativedelta(months=1)+MonthEnd(pmonth)))] 
                      df_fcst_7a=df_fcst_7.iloc[:,:19].copy()
                      df_fcst_7a=df_fcst_7a.drop_duplicates()
                      df_extract_forecast7 = self.extract_forecast(df_fcst_7a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 12,weeks_= 12,join_=join_).fillna(0) 
                      df_extract_forecast7 = df_extract_forecast7.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast7.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_7b=df_fcst_7[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_7= pd.merge(df_extract_forecast7,df_fcst_7b,on=['Item','Location'],how='left')
                      df_final_7= pd.merge(df_final_7,df_fcst_7_current,on=['Item','Location'],how='left')
                      df_final_7[column_forecast]=df_final_7['Current'] + df_final_7['Next']*((df_final_7['ReorderDays']-DaysOfMonth+DayOfMonth)/(df_final_7['Periods']*DaysOfMonth))
                      df_final_7 = df_final_7.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_7.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_7 = pd.DataFrame(columns = columns)

                if frequency_ == 'W':
                  df_final_fcst.loc[df_final_fcst['ReorderDays'].isnull(),'ReorderDays'] = 6
                  df_final_fcst['Periods'] = (df_final_fcst['ReorderDays']+DayOfWeek)//DaysOfWeek

                  #CURRENT PERIOD --------------------------------------------------------------
                  df_fcst_current = df_final_fcst[(df_final_fcst['Date']>df_Prep['timestamp'].max())&
                              (df_final_fcst['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                  df_fcst_current=df_fcst_current.iloc[:,:19]
                  df_fcst_current=df_fcst_current.drop_duplicates()
                  df_extract_fcst_current = self.extract_forecast(df_fcst_current, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                        date_cols = 'Date',months_= 1,weeks_= 1,join_=join_).fillna(0) 
                  df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({column_forecast:sum})
                  df_extract_fcst_current[column_forecast]=df_extract_fcst_current[column_forecast] *(1-DayOfWeek/DaysOfWeek)
                  df_extract_fcst_current.rename(columns={column_forecast:'Current'},inplace=True)
                  df_extract_fcst_current=df_extract_fcst_current[['Item','Location','Current']]

                  # LESS THAN A PERIOD-----------------------------------------------------
                  df_fcst_0 = df_final_fcst[df_final_fcst['Periods'] == 0]
                  if not df_fcst_0.empty:
                      df_fcst_0 = df_fcst_0[(df_fcst_0['Date']>df_Prep['timestamp'].max())&
                                (df_fcst_0['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                      df_fcst_0=df_fcst_0.iloc[:,:19]
                      df_fcst_0=df_fcst_0.drop_duplicates()
                      df_extract_forecast_0 = self.extract_forecast(df_fcst_0, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                              date_cols = 'Date',months_= 1,weeks_= 1,join_=join_).fillna(0) 
                      df_final_0 = df_extract_forecast_0.groupby(columns_group, as_index=False).agg({column_forecast:sum})
                      df_final_0[column_forecast]=df_final_0[column_forecast] *(1-DayOfWeek/DaysOfWeek)
                  
                  if df_fcst_0.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_0 =  pd.DataFrame(columns = columns)
                  
                  # ONE PERIOD-----------------------------------------------------
                  df_fcst_1 = df_final_fcst[df_final_fcst['Periods'] == 1]
                  if not df_fcst_1.empty:
                      itemslist_1=list(df_fcst_1['Item'].unique())
                      df_fcst_1_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_1)]
                      
                      df_fcst_1 = df_fcst_1[(df_fcst_1['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_1['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=2)))]
                      df_fcst_1a=df_fcst_1.iloc[:,:19].copy()
                      df_fcst_1a=df_fcst_1a.drop_duplicates()
                      df_extract_forecast1 = self.extract_forecast(df_fcst_1a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 2,weeks_= 2,join_=join_).fillna(0) 
                      df_extract_forecast1 = df_extract_forecast1.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast1.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_1b=df_fcst_1[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_1= pd.merge(df_extract_forecast1,df_fcst_1b,on=['Item','Location'],how='left')
                      df_final_1= pd.merge(df_final_1,df_fcst_1_current,on=['Item','Location'],how='left')
                      df_final_1[column_forecast]=df_final_1['Current'] + df_final_1['Next']*((df_final_1['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_1['Periods']*DaysOfWeek))
                      df_final_1 = df_final_1.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_1.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_1 = pd.DataFrame(columns = columns)

                  # TWO PERIODS-----------------------------------------------------
                  df_fcst_2 = df_final_fcst[df_final_fcst['Periods'] == 2]
                  if not df_fcst_2.empty:
                      itemslist_2=list(df_fcst_2['Item'].unique())
                      df_fcst_2_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_2)]
                      
                      df_fcst_2 = df_fcst_2[(df_fcst_2['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_2['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=3)))]
                      df_fcst_2a=df_fcst_2.iloc[:,:19].copy()
                      df_fcst_2a=df_fcst_2a.drop_duplicates()
                      df_extract_forecast2 = self.extract_forecast(df_fcst_2a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 3,weeks_= 3,join_=join_).fillna(0) 
                      df_extract_forecast2 = df_extract_forecast2.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast2.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_2b=df_fcst_2[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_2= pd.merge(df_extract_forecast2,df_fcst_2b,on=['Item','Location'],how='left')
                      df_final_2= pd.merge(df_final_2,df_fcst_2_current,on=['Item','Location'],how='left')
                      df_final_2[column_forecast]=df_final_2['Current'] + df_final_2['Next']*((df_final_2['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_2['Periods']*DaysOfWeek))
                      df_final_2 = df_final_2.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_2.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_2 = pd.DataFrame(columns = columns)
                  
                  # THREE PERIODS-----------------------------------------------------
                  df_fcst_3 = df_final_fcst[df_final_fcst['Periods'] == 3]
                  if not df_fcst_3.empty:
                      itemslist_3=list(df_fcst_3['Item'].unique())
                      df_fcst_3_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_3)]
                      
                      df_fcst_3 = df_fcst_3[(df_fcst_3['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_3['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=4)))]
                      df_fcst_3a=df_fcst_3.iloc[:,:19].copy()
                      df_fcst_3a=df_fcst_3a.drop_duplicates()
                      df_extract_forecast3 = self.extract_forecast(df_fcst_3a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 4,weeks_= 4,join_=join_).fillna(0) 
                      df_extract_forecast3 = df_extract_forecast3.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast3.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_3b=df_fcst_3[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_3= pd.merge(df_extract_forecast3,df_fcst_3b,on=['Item','Location'],how='left')
                      df_final_3= pd.merge(df_final_3,df_fcst_3_current,on=['Item','Location'],how='left')
                      df_final_3[column_forecast]=df_final_3['Current'] + df_final_3['Next']*((df_final_3['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_3['Periods']*DaysOfWeek))
                      df_final_3 = df_final_3.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_3.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_3 = pd.DataFrame(columns = columns)
                  
                  # FOUR PERIODS-----------------------------------------------------
                  df_fcst_4 = df_final_fcst[df_final_fcst['Periods'] == 4]
                  if not df_fcst_4.empty:
                      itemslist_4=list(df_fcst_4['Item'].unique())
                      df_fcst_4_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_4)]
                      
                      df_fcst_4 = df_fcst_4[(df_fcst_4['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_4['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=5)))]
                      df_fcst_4a=df_fcst_4.iloc[:,:19].copy()
                      df_fcst_4a=df_fcst_4a.drop_duplicates()
                      df_extract_forecast4 = self.extract_forecast(df_fcst_4a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 5,weeks_= 5,join_=join_).fillna(0) 
                      df_extract_forecast4 = df_extract_forecast4.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast4.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_4b=df_fcst_4[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_4= pd.merge(df_extract_forecast4,df_fcst_4b,on=['Item','Location'],how='left')
                      df_final_4= pd.merge(df_final_4,df_fcst_4_current,on=['Item','Location'],how='left')
                      df_final_4[column_forecast]=df_final_4['Current'] + df_final_4['Next']*((df_final_4['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_4['Periods']*DaysOfWeek))
                      df_final_4 = df_final_4.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_4.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_4 = pd.DataFrame(columns = columns)
                  
                  # FIVE PERIODS-----------------------------------------------------
                  df_fcst_5 = df_final_fcst[df_final_fcst['Periods'] == 5]
                  if not df_fcst_5.empty:
                      itemslist_5=list(df_fcst_5['Item'].unique())
                      df_fcst_5_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_5)]
                      
                      df_fcst_5 = df_fcst_5[(df_fcst_5['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_5['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=6)))]
                      df_fcst_5a=df_fcst_5.iloc[:,:19].copy()
                      df_fcst_5a=df_fcst_5a.drop_duplicates()
                      df_extract_forecast5 = self.extract_forecast(df_fcst_5a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 6,weeks_= 6,join_=join_).fillna(0) 
                      df_extract_forecast5 = df_extract_forecast5.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast5.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_5b=df_fcst_5[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_5= pd.merge(df_extract_forecast5,df_fcst_5b,on=['Item','Location'],how='left')
                      df_final_5= pd.merge(df_final_5,df_fcst_5_current,on=['Item','Location'],how='left')
                      df_final_5[column_forecast]=df_final_5['Current'] + df_final_5['Next']*((df_final_5['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_5['Periods']*DaysOfWeek))
                      df_final_5 = df_final_5.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_5.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_5 = pd.DataFrame(columns = columns)

                  # SIX PERIODS-----------------------------------------------------
                  df_fcst_6 = df_final_fcst[df_final_fcst['Periods'] == 6]
                  if not df_fcst_6.empty:
                      itemslist_6=list(df_fcst_6['Item'].unique())
                      df_fcst_6_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_6)]
                      
                      df_fcst_6 = df_fcst_6[(df_fcst_6['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))&
                                  (df_fcst_6['Date']<= (df_Prep['timestamp'].max()+relativedelta(weeks=7)))]
                      df_fcst_6a=df_fcst_6.iloc[:,:19].copy()
                      df_fcst_6a=df_fcst_6a.drop_duplicates()
                      df_extract_forecast6 = self.extract_forecast(df_fcst_6a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 7,weeks_= 7,join_=join_).fillna(0) 
                      df_extract_forecast6 = df_extract_forecast6.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast6.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_6b=df_fcst_6[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_6= pd.merge(df_extract_forecast6,df_fcst_6b,on=['Item','Location'],how='left')
                      df_final_6= pd.merge(df_final_6,df_fcst_6_current,on=['Item','Location'],how='left')
                      df_final_6[column_forecast]=df_final_6['Current'] + df_final_6['Next']*((df_final_6['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_6['Periods']*DaysOfWeek))
                      df_final_6 = df_final_6.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_6.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_6 = pd.DataFrame(columns = columns)

                  # SEVEN PERIODS-----------------------------------------------------
                  df_fcst_7 = df_final_fcst[df_final_fcst['Periods'] == 7]
                  if not df_fcst_7.empty:
                      itemslist_7=list(df_fcst_7['Item'].unique())
                      df_fcst_7_current=df_extract_fcst_current[df_extract_fcst_current['Item'].isin(itemslist_7)]
                      
                      df_fcst_7 = df_fcst_7[(df_fcst_7['Date']>(df_Prep['timestamp'].max()+relativedelta(weeks=1)))]
                      df_fcst_7a=df_fcst_7.iloc[:,:19].copy()
                      df_fcst_7a=df_fcst_7a.drop_duplicates()
                      df_extract_forecast7 = self.extract_forecast(df_fcst_7a, df_inv, column_forecast=column_forecast, location=location,frequency_= frequency_ ,
                                                            date_cols = 'Date',months_= 12,weeks_= 12,join_=join_).fillna(0) 
                      df_extract_forecast7 = df_extract_forecast7.groupby(columns_group, as_index=False).agg({column_forecast:sum}) 
                      df_extract_forecast7.rename(columns={column_forecast:'Next'},inplace=True)
                  
                      df_fcst_7b=df_fcst_7[['Item','Location','ReorderDays','Periods']].drop_duplicates() 
                      df_final_7= pd.merge(df_extract_forecast7,df_fcst_7b,on=['Item','Location'],how='left')
                      df_final_7= pd.merge(df_final_7,df_fcst_7_current,on=['Item','Location'],how='left')
                      df_final_7[column_forecast]=df_final_7['Current'] + df_final_7['Next']*((df_final_7['ReorderDays']-DaysOfWeek+DayOfWeek)/(df_final_7['Periods']*DaysOfWeek))
                      df_final_7 = df_final_7.groupby(columns_group, as_index=False).agg({column_forecast:max}) 
                        
                  if df_fcst_7.empty:
                      columns=list(df_inv.columns)
                      columns.append(column_forecast)
                      df_final_7 = pd.DataFrame(columns = columns)

                # Forecast -----------------------------------------------------------------  
                df_fcst = pd.concat([df_final_0,df_final_1,df_final_2,df_final_3,df_final_4,df_final_5,df_final_6,df_final_7],ignore_index=True)

                df_fcst = df_fcst.groupby(columns_group, as_index=False).agg({column_forecast:max}) 

            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_fcst


        # AVERAGE DAILY -----------------------------------------------------------------

        def extract_avg_daily(self,df_prep, df_invopt,date_cols,location=True,months_=4,weeks_=4,frequency_='M'): 
            """
            Return a dataframe with addition the column AvgDailyUsage  in the Inventory's Dataframe

            : param df_prep: Dataframe prepared for Forecast
            : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, Transit
            : param date_cols: Column name of date from df_prep
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : param months_: Target Number months 
            : param weeks_: Target Number weeks 
            : param frequency_: Target frequency to the dataset

            >>> df_extract = extract_avg_daily(df_prep, df_invopt, date_cols='timestamp', location=fmt.use_location, months_= 4, frequency_= fmt.dataset_frequency)
            >>> df_extract =
                                                Item    Location   Inventory   Transit     AvgDailyUsage
                                    idx0          85      905         23            0             20
                                    idx1          102     487         95            0             10
            """

            try:
                
                if frequency_ == 'M':
                    df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(months=months_))) & 
                                        (df_prep[date_cols] <= df_prep[date_cols].max() )]
                    if location:
                        df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                            .agg({'demand': sum})\
                                                                                            .reset_index(drop=True)
                        df_prep_avg['demand'] = df_prep_avg['demand']/(30*months_)

                        dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'AvgDailyUsage'}
                        df_prep_avg.rename(columns=dict_names,inplace=True)
                        df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                        df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)

                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_invopt['Location'] = df_invopt['Location'].astype(str)

                        df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','AvgDailyUsage']],on=['Item','Location'],how='left')
                    else:
                        df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                    .agg({'demand': sum})\
                                                                                    .reset_index(drop=True)
                        df_prep_avg['demand'] = df_prep_avg['demand']/(30*months_)
                        dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'AvgDailyUsage'}
                        df_prep_avg.rename(columns=dict_names,inplace=True)
                        df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)

                        df_invopt['Item'] = df_invopt['Item'].astype(str)

                        df_extract = pd.merge(df_invopt,df_prep_avg[['Item','AvgDailyUsage']],on=['Item'],how='left')

                elif frequency_ == 'W': 
                    week_ = weeks_
                    df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(days=7*week_))) & 
                                        (df_prep[date_cols] <= df_prep[date_cols].max() )]
                    if location:
                        df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                            .agg({'demand': sum})\
                                                                                            .reset_index(drop=True)
                        df_prep_avg['demand'] = df_prep_avg['demand']/(7*week_)

                        dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'AvgDailyUsage'}
                        df_prep_avg.rename(columns=dict_names,inplace=True)
                        df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                        df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)

                        df_invopt['Item'] = df_invopt['Item'].astype(str)
                        df_invopt['Location'] = df_invopt['Location'].astype(str)

                        df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','AvgDailyUsage']],on=['Item','Location'],how='left')

                    else:
                        df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                    .agg({'demand': sum})\
                                                                                    .reset_index(drop=True)
                        df_prep_avg['demand'] = df_prep_avg['demand']/(7*week_)
                        dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'AvgDailyUsage'}
                        df_prep_avg.rename(columns=dict_names,inplace=True)
                        df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)

                        df_invopt['Item'] = df_invopt['Item'].astype(str)

                        df_extract = pd.merge(df_invopt,df_prep_avg[['Item','AvgDailyUsage']],on=['Item'],how='left')
                
                
                df_extract['AvgDailyUsage'] = round(df_extract['AvgDailyUsage'],3)
                df_extract.loc[(df_extract['AvgDailyUsage']>0)&(df_extract['AvgDailyUsage']<=1),'AvgDailyUsage'] = 1.0
            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_extract


        # MAX SALES ----------------------------------------------------------------

        def extract_max_daily(self,df_prep, df_invopt,date_cols,location=True,weeks_=16,months_=4,frequency_='W'):
            """
            Return a dataframe with addition the column MaxDailyUsage in the Inventory's Dataframe

            : param df_prep: Dataframe prepared for Forecast
            : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, Transit
            : param date_cols: Column name of date from df_prep
            : param location: Boolean to enable the use of Location in the Inventory's dataframe
            : param months_: Target Number months 
            : param weeks_: Target Number weeks 
            : param frequency_: Target frequency to the dataset
            : return df_extract: Dataframe with addition the column MaxDailyUsage in the Inventory's Dataframe

            >>> df_extract = extract_max_daily (df_prep, df_invopt, date_cols='timestamp', location=fmt.use_location, months_= 4, frequency_= fmt.dataset_frequency)
            >>> df_extract =
                                                Item    Location   Inventory   Transit     MaxDailyUsage
                                    idx0          85      905         23            0             20
                                    idx1          102     487         95            0             10
            """
            
            try:      
              if frequency_ == 'M':
                df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(months=months_))) & 
                                    (df_prep[date_cols] <= df_prep[date_cols].max() )]
                if location:
                    df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                        .agg({'demand': np.std})\
                                                                                        .reset_index(drop=True)
                    df_prep_avg['demand'] = (2*df_prep_avg['demand'])/(30*months_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'MaxDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)
                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailyUsage']],on=['Item','Location'],how='left')

                else:
                    df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                .agg({'demand': np.std})\
                                                                                .reset_index(drop=True)
                    df_prep_avg['demand'] = (2*df_prep_avg['demand'])/(30*months_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'MaxDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','MaxDailyUsage']],on=['Item'],how='left')

              if frequency_ == 'W':

                df_prep_avg = df_prep[(df_prep[date_cols] > (df_prep[date_cols].max() - relativedelta(weeks=weeks_))) & 
                                      (df_prep[date_cols] <= df_prep[date_cols].max() )]
                if location:
                    df_prep_avg = df_prep_avg.groupby(['item_id', 'location'], as_index=False)\
                                                                                        .agg({'demand': np.std})\
                                                                                        .reset_index(drop=True)
                    df_prep_avg['demand'] = (2*df_prep_avg['demand'])/(7*weeks_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','location':'Location','demand':'MaxDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_prep_avg['Location'] = df_prep_avg['Location'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_invopt['Location'] = df_invopt['Location'].astype(str)
                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','Location','MaxDailyUsage']],on=['Item','Location'],how='left')

                else:
                    df_prep_avg = df_prep_avg.groupby(['item_id'], as_index=False)\
                                                                                .agg({'demand': np.std})\
                                                                                .reset_index(drop=True)
                    df_prep_avg['demand'] = (2*df_prep_avg['demand'])/(7*weeks_)
                    dict_names = {'item_id':'Item','timestamp':'Fecha','demand':'MaxDailyUsage'}
                    df_prep_avg.rename(columns=dict_names,inplace=True)
                    df_prep_avg['Item'] = df_prep_avg['Item'].astype(str)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_prep_avg[['Item','MaxDailyUsage']],on=['Item'],how='left')

              df_extract['MaxDailyUsage'] = round(df_extract['MaxDailyUsage'],3)
              df_extract['MaxDailyUsage'] = df_extract['AvgDailyUsage'] + df_extract['MaxDailyUsage']
              df_extract.loc[(df_extract['MaxDailyUsage']>0)&(df_extract['MaxDailyUsage']<=1),'MaxDailyUsage'] = 1.0

            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df_extract

        #INDICADORES -----------------------------------------------------------

        def functions_inventory(self,df_inv,min_inv=False,div_purfac=False):

            """
            Return a dataframe with all the indicators 
          
            : param df_inv: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, Transit, DemandHistory  SuggestedForecast AvgDailyUsage MaxDailyUsage           
            : param min_inv: Boolean to allow the minimum amount of inventory in location
            : param div_purfac: Boolean to allow data divided by purchase days 

            >>> df_inv = functions_inventory(df_inv,min_inv=False,div_purfac=False)  

            """
            try:
                df=df_inv.copy()
                
                df['InventoryTransit'] = df['Inventory'] + df['Transit']
                
                df['InventoryTransitForecast'] = df['InventoryTransit'] - df['SuggestedForecast']
                
                df['LeadTimeDemand'] = df['AvgLeadTime'] * df['AvgDailyUsage']
                
                df['SecurityStock'] = ((df['MaxDailyUsage']*df['MaxLeadTime']) - (df['AvgDailyUsage']*df['AvgLeadTime']))
                df['SecurityStock'] = df['SecurityStock'].fillna(0)
                df['SecurityStock'] = df['SecurityStock'].map(lambda x: 1 if x <= 1 else x)
                
                df['SecurityStockDays'] = (df['SecurityStock']) / (df['AvgDailyUsage'])
                df['SecurityStockDays'] = df['SecurityStockDays'].fillna(0)
                df['SecurityStockDays'] = df['SecurityStockDays'].map(lambda x: 0 if x < 0 else x)
                df['SecurityStockDays'] = df['SecurityStockDays'].astype(str).str.replace('-inf', '0').str.replace('inf', '0').str.replace('nan', '0')
                df['SecurityStockDays'] = df['SecurityStockDays'].astype(float)
                
                df['ReorderPoint'] = (df['LeadTimeDemand'] + df['SecurityStock'])
                df['ReorderPoint'] = df['ReorderPoint'].map(lambda x: 0 if x < 0 else x)
                
                df['ReorderPointDays'] = (df['LeadTimeDemand'] + df['SecurityStock']) / (df['AvgDailyUsage'])
                df['ReorderPointDays'] = df['ReorderPointDays'].fillna(0)
                df['ReorderPointDays'] = df['ReorderPointDays'].astype(str).str.replace('-inf', '0').str.replace('inf', '0').str.replace('nan', '0')
                df['ReorderPointDays'] = df['ReorderPointDays'].astype(float)
                
                df['SuggestedReorderQty'] = df['InventoryTransit'] -df['SuggestedForecast'] - df['SecurityStock']
                df['ReorderStatus']=df[['SuggestedReorderQty','ReorderPoint']].apply(lambda x: 'Order' if x['SuggestedReorderQty']<0 or x['SuggestedReorderQty']<= x['ReorderPoint'] else 'Hold', axis=1)
                                  
                if min_inv == False:
                  df['RQty'] = (df['Inventory']+df['Transit']-df['Committed']-df['SuggestedForecast']-df['SecurityStock']).abs()
                  df['ReorderQty'] = df[['ReorderStatus','RQty']].apply(lambda x: x['RQty'] if (x['ReorderStatus']=='Order') else 0 , axis=1 )
                  df['ReorderQty']    = df[['ReorderQty','ReorderStatus']].apply(lambda x: (1 if (x['ReorderQty'] <= 1) else x['ReorderQty']) if(x['ReorderStatus']=='Order') else x['ReorderQty'], axis=1)
                  
                if min_inv == True:
                  df['RQty'] = (df['Inventory']+df['Transit']-df['Committed']-df['SuggestedForecast']-df['SecurityStock']).abs()
                  df['ReorderQty'] = df[['ReorderStatus','RQty','DemandHistory']].apply(lambda x: x['RQty'] if (x['ReorderStatus']=='Order') else x['DemandHistory'] , axis=1 )
                  df['ReorderQty'] = df[['ReorderQty','ReorderStatus']].apply(lambda x: (1 if (x['ReorderQty'] <= 1) else x['ReorderQty']), axis=1)
                  
                df['MinQty'] = (df['Inventory']+df['Transit']-df['Committed']-(df['NextSuggestedForecast'])-df['SecurityStock'] ).abs()   
                df['MaxQty'] = (df['Inventory']+df['Transit']-df['Committed']-(df['BackSuggestedForecast'])-df['SecurityStock'] ).abs()
                
                df['MinReorderQty'] = df[['ReorderStatus','MinQty','MaxQty']].apply(lambda x: (x['MinQty'] if (x['MinQty']<x['MaxQty']) else x['MaxQty']) if (x['ReorderStatus']=='Order') else 0 , axis=1 )
                df['MinReorderQty'] = df[['MinReorderQty','ReorderStatus']].apply(lambda x: (1 if (x['MinReorderQty'] <= 1) else x['MinReorderQty']) if(x['ReorderStatus']=='Order') else x['MinReorderQty'], axis=1)
                
                df['MaxReorderQty'] = df[['ReorderStatus','MinQty','MaxQty']].apply(lambda x: (x['MinQty'] if (x['MinQty']>x['MaxQty']) else x['MaxQty']) if (x['ReorderStatus']=='Order') else 0 , axis=1 )
                df['MaxReorderQty'] = df[['MaxReorderQty','ReorderStatus']].apply(lambda x: (1 if (x['MaxReorderQty'] <= 1 )else x['MaxReorderQty']) if(x['ReorderStatus']=='Order') else x['MaxReorderQty'], axis=1)
                
                df['RQtyTwoPeriods'] = (df['Inventory']+df['Transit']-df['Committed']-df['SuggestedForecast_2p']-df['SecurityStock']).abs()
                df['ReorderQtyTwoPeriods'] = df[['ReorderStatus','RQtyTwoPeriods']].apply(lambda x: x['RQtyTwoPeriods'] if (x['ReorderStatus']=='Order') else 0 , axis=1 )
                df['ReorderQtyTwoPeriods'] = df[['ReorderQtyTwoPeriods','ReorderStatus']].apply(lambda x: (1 if (x['ReorderQtyTwoPeriods'] <= 1) else x['ReorderQtyTwoPeriods']) if(x['ReorderStatus']=='Order') else x['ReorderQtyTwoPeriods'], axis=1)
                
                df['RQtyThreePeriods'] = (df['Inventory']+df['Transit']-df['Committed']-df['SuggestedForecast_3p']-df['SecurityStock']).abs()
                df['ReorderQtyThreePeriods'] = df[['ReorderStatus','RQtyThreePeriods']].apply(lambda x: x['RQtyThreePeriods'] if (x['ReorderStatus']=='Order') else 0 , axis=1 )
                df['ReorderQtyThreePeriods'] = df[['ReorderQtyThreePeriods','ReorderStatus']].apply(lambda x: (1 if (x['ReorderQtyThreePeriods'] <= 1) else x['ReorderQtyThreePeriods']) if(x['ReorderStatus']=='Order') else x['ReorderQtyThreePeriods'], axis=1)
                
                df.drop(columns=['RQty','MinQty','MaxQty','RQtyTwoPeriods','RQtyThreePeriods'],inplace=True)
                
                df['StockoutDays']=(df['Inventory']-df['SecurityStock'])/df['AvgDailyUsage']
                df['StockoutDays'] = df['StockoutDays'].fillna(0)
                df['StockoutDays'] = df['StockoutDays'].map(lambda x: 0 if x < 0 else x)
                df['StockoutDays'] = df['StockoutDays'].astype(str).str.replace('-inf', '0').str.replace('inf', '0').str.replace('nan', '0')
                df['StockoutDays'] = df['StockoutDays'].astype(float)

                df['InvTransStockoutDays']=(df['InventoryTransit']-df['SecurityStock'])/df['AvgDailyUsage']
                df['InvTransStockoutDays'] = df['InvTransStockoutDays'].fillna(0)
                df['InvTransStockoutDays'] = df['InvTransStockoutDays'].map(lambda x: 0 if x < 0 else x)
                df['InvTransStockoutDays'] = df['InvTransStockoutDays'].astype(str).str.replace('-inf', '0').str.replace('inf', '0').str.replace('nan', '0')
                df['InvTransStockoutDays'] = df['InvTransStockoutDays'].astype(float)
                
                df['ForecastStockoutDays']=(df['InventoryTransitForecast']-df['SecurityStock'])/df['AvgDailyUsage']
                df['ForecastStockoutDays'] = df['ForecastStockoutDays'].fillna(0)
                df['ForecastStockoutDays'] = df['ForecastStockoutDays'].map(lambda x: 0 if x < 0 else x)
                df['ForecastStockoutDays'] = df['ForecastStockoutDays'].astype(str).str.replace('-inf', '0').str.replace('inf', '0').str.replace('nan', '0')
                df['ForecastStockoutDays'] = df['ForecastStockoutDays'].astype(float)

                if div_purfac == False:
                  df['ReorderQtyFactor']=round(df['ReorderQty']/df['PurchaseFactor'])
                  df['ReorderQtyTwoPeriodsFactor']=round(df['ReorderQtyTwoPeriods']/df['PurchaseFactor'])
                  df['ReorderQtyThreePeriodsFactor']=round(df['ReorderQtyThreePeriods']/df['PurchaseFactor'])
                if div_purfac == True:
                  df['ReorderQtyFactor']=df['ReorderQty']   
                  df['ReorderQtyTwoPeriodsFactor']=df['ReorderQtyTwoPeriods']
                  df['ReorderQtyThreePeriodsFactor']=df['ReorderQtyThreePeriods']   

                if 'UnitCost' not in df.columns:
                  df.loc[:,'UnitCost'] = 0           

                if 'TotalCost' not in df.columns:        
                  df.loc[:,'TotalCost'] = df['UnitCost']*df['ReorderQty']
                
            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise         
            return df

        #FORMAT-------------------------------------------------
        def clean_and_format(self,df_invopt):
            """
            Return a dataframe with the correct format       
            : param df: Inventory's Dataframe 
              
            >>> df = clean_and_format(df)
            """           
            try:
                df=df_invopt.copy()
                indicators=['Item','ItemDescription','Location','LocationDescription','Inventory','Transit',
                        'Committed','InventoryTransit','InventoryTransitForecast','StockoutDays','InvTransStockoutDays',
                        'DemandHistory','SuggestedForecast','NextSuggestedForecast','BackSuggestedForecast',
                        'SuggestedForecast_2p','SuggestedForecast_3p','ForecastStockoutDays',
                        'Ranking','AvgDailyUsage','MaxDailyUsage','AvgLeadTime','MaxLeadTime','LeadTimeDemand','SecurityStock',
                        'SecurityStockDays','ReorderPoint','ReorderPointDays','SuggestedReorderQty',
                        'ReorderQty','MinReorderQty','MaxReorderQty','ReorderQtyTwoPeriods','ReorderQtyThreePeriods',
                        'ReorderStatus','ReorderDays',
                        'PurchaseFactor','ReorderQtyFactor','ReorderQtyTwoPeriodsFactor','ReorderQtyThreePeriodsFactor',
                        'Provider','ProviderDescription','UM','MinOrderQty','DeliveryFactor','UnitCost','TotalCost','Customer','Country',
                        'ProductType','Dimension','Color','Origen','Gama','Marca','JefeProducto','GrupoCompra','Familia','InventoryUnit']

                for val,name in enumerate(indicators):
                    if name not in df.columns:
                        df[name] = "N/A"

                cols1 = ['InventoryUnit','Inventory', 'ReorderDays', 'Transit', 'Committed',           
                    'DemandHistory','SuggestedForecast','NextSuggestedForecast','BackSuggestedForecast',
                    'SuggestedForecast_2p','SuggestedForecast_3p',
                    'InventoryTransit', 'InventoryTransitForecast','SecurityStock', 'SecurityStockDays',
                    'ReorderPoint','ReorderPointDays', 'SuggestedReorderQty',
                    'ReorderQty', 'MinReorderQty', 'MaxReorderQty',
                    'ReorderQtyTwoPeriods','ReorderQtyThreePeriods',
                    'ReorderQtyFactor','ReorderQtyTwoPeriodsFactor','ReorderQtyThreePeriodsFactor',
                    'StockoutDays', 'ForecastStockoutDays','InvTransStockoutDays']

                for a in cols1:
                    df[a] = df[a].astype(str).replace("N/A",'0')
                    df[a] = df[a].astype(float) 
                    df[a] = df[a].apply(np.ceil)
                    df[a] = df[a].astype(int) 

                cols =  df.select_dtypes(['float']).columns
                df[cols] =  df[cols].apply(lambda x: round(x, 3))
                
                df = df[indicators]
                df = df.drop_duplicates().reset_index(drop=True)  

            except KeyError as err:
                self.logger.exception(f'No column found. Please check columns names: {err}')
                print(f'No column found. Please check columns names')
                raise
            return df