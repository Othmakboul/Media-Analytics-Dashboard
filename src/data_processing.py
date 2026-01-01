import pandas as pd
import ast
from functools import lru_cache
import numpy as np

# Use lru_cache to load data once into memory
@lru_cache(maxsize=1)
def load_data(filepath='data/processed/clean_data.csv'):
    """
    Loads the dataset and performs initial preprocessing.
    Parses stringified lists in 'kws', 'loc', 'org', 'per'.
    Converts 'date' to datetime objects.
    """
    try:
        df = pd.read_csv(filepath)
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Cols that need parsing from string representation of list to actual list
        list_cols = ['kws', 'loc', 'org', 'per']
        for col in list_cols:
            if col in df.columns:
                # ast.literal_eval safely evaluates a string containing a generic Python literal
                # We handle NaNs by treating them as empty lists
                df[col] = df[col].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) and isinstance(x, str) and x.startswith('[') else [])
        
        # Fill NaN for text content just in case
        if 'content' in df.columns:
            df['content'] = df['content'].fillna('')
            
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def explode_entities(df, column):
    """
    Explodes validity of a list column to allow counting individual entities.
    Returns a Series of all entities found in that column.
    """
    if column not in df.columns:
        return pd.Series(dtype='object')
    return df[column].explode().dropna()

def compute_cooccurrence_matrix(df, entity_col='kws', top_n=30):
    """
    Computes a co-occurrence matrix for the top_n most frequent entities in a column.
    Useful for heatmaps.
    """
    # Filter valid lists
    docs = df[entity_col].dropna()
    
    # Get top N entities to keep matrix manageable
    all_entities = docs.explode().value_counts().head(top_n).index.tolist()
    
    # Filter inner lists to only contain top entities
    filtered_docs = docs.apply(lambda x: [i for i in x if i in all_entities])
    
    # Create co-occurrence matrix
    cooc_mat = pd.DataFrame(0, index=all_entities, columns=all_entities)
    
    for doc in filtered_docs:
        for i in range(len(doc)):
            for j in range(i + 1, len(doc)):
                e1, e2 = doc[i], doc[j]
                # Increment both ways for symmetry
                cooc_mat.loc[e1, e2] += 1
                cooc_mat.loc[e2, e1] += 1
                
    return cooc_mat

def filter_data(df, start_date=None, end_date=None, keywords=None, locations=None):
    """
    Generic filtering function for cross-filtering.
    keywords and locations should be lists of strings to match.
    Logic is OR within a category (if any match), AND across categories.
    """
    dff = df.copy()
    
    # Date Filter
    if start_date and end_date:
        dff = dff[(dff['date'] >= start_date) & (dff['date'] <= end_date)]
        
    # Keyword Filter (if any selected keyword is in the article's kws list)
    if keywords:
        # Check if set intersection is not empty
        kws_set = set(keywords)
        dff = dff[dff['kws'].apply(lambda x: not kws_set.isdisjoint(x))]
        
    # Location Filter
    if locations:
        locs_set = set(locations)
        dff = dff[dff['loc'].apply(lambda x: not locs_set.isdisjoint(x))]
        
    return dff
