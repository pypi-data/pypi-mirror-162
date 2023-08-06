import pandas as pd
from pathlib import Path
import os
import json

def structured_json_bosch_sensor(path_to_json,saved_folder_path,result):
    # 
    # Read the json file
    json_file_path = path_to_json
    with open(json_file_path, 'r') as j:
     contents = json.loads(j.read())
    #  
    # Transform the 'rawDataBody' from the JSON file into a dataframe
    try:
        data = contents['rawDataBody']
    except:
        raise TypeError('The JSON file provided does not follow the structure of the BME688 sensor',
        'Please check for the expected data format [from page 52]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/application_notes_1/bst-bme688-an001.pdf')
    # 
    df = pd.json_normalize(data, record_path =['dataBlock'])
    # 
    df = df.rename(columns={df.columns[0]: 'sensor_index',  
                            df.columns[1]: 'sensor_id',
                            df.columns[2]: 'time_since_power_on',
                            df.columns[3]: 'real_time_clock',
                            df.columns[4]: 'temperature',
                            df.columns[5]: 'pressure',
                            df.columns[6]: 'relative_humidity',
                            df.columns[7]: 'resistance_gas_sensor',
                            df.columns[8]: 'heater_profile_step_index',
                            df.columns[9]: 'scanning_enabled',
                            df.columns[10]: 'label_tab',
                            df.columns[11]: 'error_code'
    })
    df['real_time_clock'] = pd.to_datetime(df['real_time_clock'], unit='s', origin='unix') 
    # 
    # Check the number of sensors and the number of steps per heating cycle
    num_sensor = df['sensor_index'].nunique()
    num_steps = df['heater_profile_step_index'].nunique()
    # 
    # Create a dictionay with a list of dataframes - one per sensor (e.g. df_dict['sensor_0'])
    df_sensor_list = []
    for i in range(num_sensor):
        df_exp_list = []
        exp_unique_id = 0
        # 
        df_sensor = df[df['sensor_index']==i].set_index('real_time_clock')
        df_sensor = df_sensor.add_suffix(f'_sensor_{i}')
        # 
        for i in range(0, df_sensor.shape[0], num_steps):
            df_temp = df_sensor[i:i+num_steps]
            df_temp['exp_unique_id'] = exp_unique_id
            exp_unique_id += 1
            df_exp_list.append(df_temp)
        
        df_merge = pd.concat(df_exp_list, axis=0)
        df_sensor_list.append(df_merge)
    # 
    df_dict = {}
    # 
    for i in range(num_sensor):
        df_dict[f'sensor_{i}'] = df_sensor_list[i].reset_index()
    # 
    # Concatenate the dataframe horizontally to have the features as columns of the different sensors
    # In sensor-0, we want to keep some useful information (exp_unique_id, and 'real_time_clock')
    # In the rest of the sensors, we only want to keep informaiton about 'gas' 'temperature', 'humidity', 'pressure'
    # 
    df_temp_list = []
    for i in range(num_sensor):
        column_name = 'sensor_' + str(i)
        df_temp = df_dict[column_name]
        if i == 0:
            # In sensor-0, we want to keep some useful information (exp_unique_id, and 'real_time_clock')
            df_temp = df_temp
        else:
            # Drop the non-relevant information from the other sensors before concatenating
            column_names = ['heater_profile_step_index_sensor_'+str(i),'scanning_enabled_sensor_'+str(i),
                            'label_tab_sensor_'+str(i),'error_code_sensor_'+str(i),'exp_unique_id',
                            'real_time_clock','sensor_index_sensor_'+str(i),'sensor_id_sensor_'+str(i), 
                            'time_since_power_on_sensor_'+str(i)]
            df_temp.drop(column_names, axis=1, inplace=True)
            df_temp.dropna()
            
        # 
        df_temp_list.append(df_temp)
    # 
    df_all = pd.concat(df_temp_list, axis=1)
    # 
    # Delete other non-useful columns from sensor 1
    columns_to_delete = ['sensor_index_sensor_0','sensor_id_sensor_0','heater_profile_step_index_sensor_0',
                    'scanning_enabled_sensor_0','label_tab_sensor_0','error_code_sensor_0',
                    'time_since_power_on_sensor_0']
    df_all.drop(columns_to_delete, axis=1, inplace=True)
    # 
    # Move the 'exp_unique_id' to the first column to aid in the visualisation in a software
    first_column = df_all.pop('exp_unique_id')
    df_all.insert(0, 'exp_unique_id', first_column)
    # 
    df_all.reset_index(inplace=True)
    df_all.drop('index', axis=1, inplace=True)
    pd.to_datetime(df_all['real_time_clock'])
    df_all= df_all[df_all['exp_unique_id'].notna()]
    # 
    # Add the result column, based on the input to the function
    try:
        df_all['result'] = result
    except:
        pass
    # 
    # Add timestep counter per experiment
    df_all['timesteps'] = ''
    print(df_all['exp_unique_id'].nunique())
    for i in range(df_all['exp_unique_id'].nunique()):
        df_temp = df_all[df_all['exp_unique_id'] == i]
        time_steps_list = df_temp.index - df_temp.index[0]
        df_all.loc[df_temp.index[0]:df_temp.index[-1],'timesteps'] = time_steps_list
    # 
    # Save file to target folder
    try:
        original_filename = Path(path_to_json).stem
        filepath_to_output = saved_folder_path + '/' + original_filename + '.csv'
        df_all.to_csv(filepath_to_output)
    except:
        print('It was not possible to save the file')
    # 
    return df_all

