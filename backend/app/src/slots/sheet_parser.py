import pandas as pd
from datetime import datetime
from src.db.db import Slot, db


def parse_sheet() -> pd.DataFrame:
    time_df = pd.read_excel(io="../data/sheet.xlsx", sheet_name='Master Schedule', parse_dates=['Time (V/JV)'])
    time_df = time_df.drop(['AT Coverage', 'Notes', 'Score', 'Type', 'Home', 'Visitor'], axis=1)
    time_df = time_df.loc[time_df['Site'] == 'Carter']
    time_df['Date'] = time_df['Date'].dt.strftime('%Y-%m-%d')
    time_df = time_df.reset_index(drop=True)

    def standardize_time(time_str) -> str:
        # Check if the time string contains a range (e.g., '9:30/10:30 AM')
        if '/' in time_str:
            start_time, end_time = time_str.split('/')
            return f'{start_time} - {end_time}'
        else:
            return time_str

    def convert_to_24_hour(time_str) -> str:
        try:
            time_obj = pd.to_datetime(time_str, format='%I:%M%p').time()
            return time_obj.strftime('%H:%M')
        except ValueError:
            return time_str

    # Apply the function to standardize the Time column
    time_df['Time (V/JV)'] = time_df['Time (V/JV)'].apply(standardize_time)
    # Apply the function to convert all times to 24-hour format
    time_df['Time (V/JV)'] = time_df['Time (V/JV)'].apply(convert_to_24_hour)

    # Function to split time and calculate end time
    def split_and_calculate_end_time(time_str) -> tuple[str, str]:
        if '-' in time_str:
            if 'PM' in time_str:
                half = ' PM'
            else:
                half = ' AM'
            times = time_str.split(' - ')
            start_time = times[0] + half
            start_time = datetime.strptime(start_time, "%I:%M %p")
            start_time = start_time.strftime("%H:%M %p")[:-3]
            if len(start_time) == 5:
                start_time = start_time + ':00'
            end_time = (pd.to_datetime(start_time, format='%H:%M:%S') + pd.Timedelta(hours=3)).strftime('%H:%M')
            if len(end_time) == 5:
                end_time = end_time + ':00'
        else:
            start_time = time_str
            end_time = (pd.to_datetime(time_str, format='%H:%M:%S') + pd.Timedelta(hours=2)).strftime('%H:%M')
        if len(end_time) == 5:
            end_time = end_time + ':00'
        return start_time, end_time

    # Apply the function to create 'Start Time' and 'End Time' columns
    time_df[['Start Time', 'End Time']] = time_df['Time (V/JV)'].apply(split_and_calculate_end_time).apply(pd.Series)
    time_df['Start Time'] = time_df['Date'].astype(str) + ' ' + time_df['Start Time'].astype(str)
    time_df['End Time'] = time_df['Date'].astype(str) + ' ' + time_df['End Time'].astype(str)
    time_df.drop(columns=['Date'], inplace=True)
    # Drop the original 'Time' column
    time_df.drop(columns=['Time (V/JV)'], inplace=True)
    return time_df


def insert_sheet_into_db(sheet: pd.DataFrame) -> None:
    with db.session.begin():
        for _, row in sheet.iterrows():
            slot = Slot(startTime=row['Start Time'], endTime=row['End Time'], sport=row['Sport'], subSection=row['Site'])
            db.session.add(slot)
