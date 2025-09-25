"""
Generates users, sessions, and events CSVs for the feed_ranking_v2 experiment.
"""
import os
import uuid
import random
import hashlib
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

#Setting parameters
NUM_USERS = 5000
NUM_DAYS = 7
countries = ['US','CA','GB','AU','IN']
device_distribution = ['mobile'] * 70 + ['desktop'] * 25 + ['tablet'] * 5
experiment_id = 'feed_ranking_v2'
control_pct = 50  #splitting percent control for treatment and control

#setting event level probabilities for realistic demo
click_prob_control = 0.10
click_lift = 0.003       
save_prob_control = 0.05
save_lift = 0.002      
board_create_prob = 0.01

#setting user-level variance
user_variance_scale = 0.02  

#output paths
OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

#generating users data
users = []
for _ in range(NUM_USERS):
    user_id = str(uuid.uuid4())
    device_type = random.choice(device_distribution)
    country = random.choices(countries, weights=[50,10,15,10,15])[0]
    new_user = 1 if random.random() < 0.3 else 0
    pre_period_saves = random.randint(0,20)
    join_date = (datetime.now() - timedelta(days=random.randint(0,90))).date()

    hash_val = int(hashlib.md5(f"{user_id}:{experiment_id}".encode()).hexdigest(), 16)
    treatment = 'control' if (hash_val % 100) < control_pct else 'treatment'

    users.append({
        'user_id': user_id,
        'device_type': device_type,
        'country': country,
        'new_user': new_user,
        'pre_period_saves': pre_period_saves,
        'join_date': join_date,
        'experiment_id': experiment_id,
        'treatment': treatment
    })

users_df = pd.DataFrame(users)

#save probability per user with variance
np.random.seed(42)
users_df['save_prob_user'] = np.where(
    users_df['treatment'] == 'control',
    np.random.normal(loc=save_prob_control, scale=user_variance_scale, size=len(users_df)),
    np.random.normal(loc=save_prob_control + save_lift, scale=user_variance_scale, size=len(users_df))
)
users_df['save_prob_user'] = users_df['save_prob_user'].clip(0,1)

#save generated users data
users_df.to_csv(os.path.join(OUT_DIR, 'users.csv'), index=False)
print("Users generated:", users_df.shape)

#generate sessions data
sessions = []
for _, user in users_df.iterrows():
    for day_offset in range(NUM_DAYS):
        num_sessions_today = max(1, np.random.poisson(lam=1.2))  #average session per day
        for _ in range(num_sessions_today):
            session_id = str(uuid.uuid4())
            session_start = datetime.now() - timedelta(days=(NUM_DAYS - day_offset - 1),
                                                       minutes=random.randint(0, 1440))
            session_length = np.random.lognormal(mean=1.5, sigma=0.5)
            session_length = min(max(session_length, 2), 10)

            sessions.append({
                'session_id': session_id,
                'user_id': user['user_id'],
                'session_start': session_start,
                'session_length': session_length,
                'device_type': user['device_type'],
                'country': user['country'],
                'experiment_id': user['experiment_id'],
                'treatment': user['treatment']
            })

sessions_df = pd.DataFrame(sessions)
sessions_df.to_csv(os.path.join(OUT_DIR, 'sessions.csv'), index=False)
print("Sessions generated:", sessions_df.shape)

#generate events data
events = []
for _, session in sessions_df.iterrows():
    num_impressions = max(1, int(session['session_length'] * random.uniform(1.5, 3.0)))
    user_prob_save = users_df.loc[users_df['user_id'] == session['user_id'], 'save_prob_user'].values[0]

    for _ in range(num_impressions):
        event_id = str(uuid.uuid4())
        timestamp = session['session_start'] + timedelta(seconds=random.randint(0, int(session['session_length']*60)))
        pin_id = str(uuid.uuid4())
        treatment = session['treatment']
        click_prob = click_prob_control + (click_lift if treatment == 'treatment' else 0)

        events.append({
            'event_id': event_id,
            'user_id': session['user_id'],
            'timestamp': timestamp.isoformat(),
            'session_id': session['session_id'],
            'event_type': 'impression',
            'pin_id': pin_id,
            'board_id': None,
            'experiment_id': session['experiment_id'],
            'treatment': treatment,
            'device_type': session['device_type'],
            'country': session['country']
        })

        if random.random() < click_prob:
            events.append({
                'event_id': str(uuid.uuid4()),
                'user_id': session['user_id'],
                'timestamp': timestamp.isoformat(),
                'session_id': session['session_id'],
                'event_type': 'click',
                'pin_id': pin_id,
                'board_id': None,
                'experiment_id': session['experiment_id'],
                'treatment': treatment,
                'device_type': session['device_type'],
                'country': session['country']
            })

        if random.random() < user_prob_save:
            board_id = str(uuid.uuid4()) if random.random() < board_create_prob else None
            events.append({
                'event_id': str(uuid.uuid4()),
                'user_id': session['user_id'],
                'timestamp': timestamp.isoformat(),
                'session_id': session['session_id'],
                'event_type': 'save',
                'pin_id': pin_id,
                'board_id': board_id,
                'experiment_id': session['experiment_id'],
                'treatment': treatment,
                'device_type': session['device_type'],
                'country': session['country']
            })

events_df = pd.DataFrame(events)
events_df.to_csv(os.path.join(OUT_DIR, 'events.csv'), index=False)
print("Events generated:", events_df.shape)

print("Storing Data:", OUT_DIR)
