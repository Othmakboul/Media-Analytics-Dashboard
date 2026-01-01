import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_dummy_data(n=1000):
    print(f"Generating {n} dummy articles...")
    
    # Setup data
    start_date = datetime(2022, 1, 1)
    dates = [start_date + timedelta(days=random.randint(0, 700)) for _ in range(n)]
    
    topics = ['Politique', 'Économie', 'Santé', 'Sport', 'Culture', 'Technologie', 'Environnement']
    locations = ['Paris', 'Londres', 'Washington', 'Moscou', 'Pékin', 'Bruxelles', 'Berlin', 'Dakar', 'Alger']
    orgs = ['ONU', 'UE', 'OTAN', 'OMS', 'FMI', 'Google', 'Tesla', 'Total', 'Sanofi']
    persons = ['Macron', 'Biden', 'Poutine', 'Zelensky', 'Musk', 'Mbappé', 'Von der Leyen', 'Xi Jinping']
    
    data = []
    
    for d in dates:
        topic = random.choice(topics)
        
        # Determine entities based on some probability to create patterns
        kws = [topic] + random.sample(topics, k=random.randint(0, 2))
        loc = random.sample(locations, k=random.randint(1, 3))
        org = random.sample(orgs, k=random.randint(0, 2))
        per = random.sample(persons, k=random.randint(0, 2))
        
        title = f"Article sur {topic} et {kws[-1]}"
        content = f"Ceci est un article fictif parlant de {', '.join(kws)} à {', '.join(loc)}."
        
        # Store as stringified lists to match user schema
        data.append({
            'date': d,
            'title': title,
            'kws': str(kws),
            'loc': str(loc),
            'org': str(org),
            'per': str(per),
            'content': content
        })
        
    df = pd.DataFrame(data)
    output_path = 'data/processed/clean_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Saved dummy data to {output_path}")

if __name__ == '__main__':
    generate_dummy_data()
