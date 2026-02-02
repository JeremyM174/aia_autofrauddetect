import pandas as pd
import os, json, joblib
from datetime import datetime, date
from io import StringIO
from sqlalchemy import create_engine
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

neontable=os.getenv('SQL') #Do not forget the .env file; you MUST set its variables for the system to work!
#For obvious reasons, I didn't provide my own credentials; NEVER share yours, refer to the `.env_example.md` file!



# ========== API ETL TASKGROUP ==========



def process_api_data(**context):
    df_temp = pd.DataFrame()
    for file in os.listdir('./data/json'):
        if file.endswith('.json'):
            with open(f'./data/json/{file}', "r", encoding='utf-8') as source_json:
                source_file = source_json.read()
                usable_source = StringIO(json.loads(source_file))
                json_temp = pd.read_json(usable_source, orient='split')
                df_temp = pd.concat([df_temp, json_temp])
        else:
            print(f'Error: {file} is not a json!')
    print(df_temp.head())
    context['task_instance'].xcom_push(key='transformed_data', value=df_temp)


def write_api_data(**context):
    df_temp = context['task_instance'].xcom_pull(key='transformed_data')
    df_logs = df_temp.copy(deep=True)
    engine = create_engine(neontable, echo=False)
    df_temp.to_sql('detect_data', engine, if_exists='replace', index=False)
    print('API data forwarded to NeonDB for detection!')
    df_logs.to_sql('logs', engine, if_exists='append', index=False)
    print('Logs copy sent to NeonDB!')



# ========== API PREDICT TASKGROUP ==========



### ===Extract/transform including feature engineering===

def pull_neon_data(**context):
    df_neon = pd.DataFrame()
    engine = create_engine(neontable, echo=False)
    df_neon = pd.read_sql_table('detect_data', engine)
    print((df_neon).head())
    context['task_instance'].xcom_push(key='raw_neondata', value=df_neon)


def age(born):
    born  = datetime.strptime(born, '%Y-%m-%d').date()
    today  = date.today()
    return today.year  - born.year  - ((today.month,today.day) < (born.month,born.day))


def make_date_feature(df, col):
    df[col] = pd.to_datetime(df[col])
    df['time'] = pd.to_datetime(df[col]).dt.time
    df['hour'] = pd.to_datetime(df[col]).dt.hour
    df['is_night'] = df['hour'].between(22, 6, inclusive="left").astype(int)
    df['is_morning'] = df['hour'].between(6, 12, inclusive="left").astype(int)
    df['is_afternoon'] = df['hour'].between(12, 18, inclusive="left").astype(int)
    df['is_evening'] = df['hour'].between(18, 22, inclusive="left").astype(int)
    df['is_business_hour'] = df['hour'].between(8, 17).astype(int)
    df['year'] = df[col].dt.year
    df['month'] = df[col].dt.month
    df['day'] = df[col].dt.day
    df['dayofweek'] = df[col].dt.day_of_week
    df['is_we'] = df['dayofweek'].between(5, 6).astype(int)


def transform_neondata(**context):
    df_trans = context['task_instance'].xcom_pull(key='raw_neondata')
    print(f'\n{df_trans.head()}\n')
    print(df_trans.columns)
    context['task_instance'].xcom_push(key='transaction_ids', value=pd.DataFrame(df_trans['trans_num']))
    df_trans['age'] = df_trans.apply(lambda row:age(row['dob']),axis=1)
    make_date_feature(df_trans, col='current_time')
    df_trans = df_trans.drop(['dob', 'trans_num', 'first', 'last', 'time', 'current_time', 'street', 'city', 'state', 'zip', 'is_fraud'], axis=1)
    print(f'\n{df_trans.head()}\n')
    print(df_trans.columns)
    context['task_instance'].xcom_push(key='ready_neondata', value=df_trans)


### === Predict ===

def consume_neondata(**context):
    df_id = context['task_instance'].xcom_pull(key='transaction_ids')
    df_prep = context['task_instance'].xcom_pull(key='ready_neondata')
    preprocessor = joblib.load('./data/model/preprocessor')
    df_predict = preprocessor.transform(df_prep)
    model = joblib.load('./data/model/detect_model')
    predictions = model.predict(df_predict)
    #You can change the content of the 'predictions' variable above to replace its input and simulate fraud detection:
    #Put model.predict as a comment (adding # before it) and feed it a list instead, e.g. 'predictions = [0,1,1]'
    #It must have the same length as how many json were fed as input - and don't forget to restore the original code after!
    print(predictions)
    print(df_id)
    df_predict = pd.DataFrame({'prediction':predictions})
    df_concat = pd.concat([df_id, df_predict], axis=1)
    print(df_concat)
    context['task_instance'].xcom_push(key='analyzed_data', value=df_concat)


def flag_checker(**context):
    df_check = context['task_instance'].xcom_pull(key='analyzed_data')
    for transaction_id, prediction_flag in zip(df_check['trans_num'], df_check['prediction']):
        if prediction_flag==1:
            print(f'===ALERT!=== Transaction {transaction_id} requires attention!')
            #The following variables are also part of your .env file; remember you can send a mail to yourself!
            sender_email = os.getenv('smtp_sender')
            app_password = os.getenv('smtpass')
            receiver_email = os.getenv('smtp_receiver')
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Detection system alert: possible fraud identified!"

            body = f"""Attention, administrator!

A potential fraud has been identified and requires double-checking.

Please refer to the appropriate logs for transaction number {transaction_id} and advise relevant teams.

Have a good day!"""
            msg.attach(MIMEText(body))

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, app_password)

                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)

                print("E-mail alert sent!")
            except Exception as e:
                print(f"Error sending mail: {e}")
            finally:
                server.quit()
        else:
            print(f'Transaction {transaction_id} was evaluated as safe.')