import json
import pandas as pd
import os
import glob

# --- CONFIGURATION ---
RAW_DATA_PATH = os.path.join("data", "raw")
PROCESSED_DATA_PATH = os.path.join("data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DATA_PATH, "clean_data.csv")

def get_articles_from_file(content):
    """
    Cette fonction sert à 'ouvrir la boîte' peu importe son format.
    """
    # Cas 1 : C'est directement une liste (Sac transparent)
    if isinstance(content, list):
        return content
    
    # Cas 2 : C'est un dictionnaire (Carton fermé)
    if isinstance(content, dict):
        # On cherche la liste cachée dans les clés connues
        if 'data' in content:
            # Sous-cas : data -> all -> liste (Le format Sputnik complexe)
            if isinstance(content['data'], dict) and 'all' in content['data']:
                return content['data']['all']
            # Sous-cas : data -> liste (Le format standard)
            if isinstance(content['data'], list):
                return content['data']
        
        # Autres clés possibles
        if 'data-all' in content and isinstance(content['data-all'], list):
            return content['data-all']
        if 'items' in content and isinstance(content['items'], list):
            return content['items']
            
    return [] # Si on ne trouve rien

def load_and_clean():
    all_data = []
    json_files = glob.glob(os.path.join(RAW_DATA_PATH, "*.json"))
    
    print(f"Fichiers trouvés : {len(json_files)}")

    for file in json_files:
        print(f"Lecture de {os.path.basename(file)}...", end=" ")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # C'est ICI la différence : on utilise la fonction intelligente
            articles = get_articles_from_file(content)
            
            if len(articles) > 0:
                all_data.extend(articles)
                print(f"-> {len(articles)} articles récupérés.")
            else:
                print("-> 0 article trouvé (Format vide ou inconnu).")
                
        except Exception as e:
            print(f"Erreur : {e}")

    # Vérification
    if len(all_data) == 0:
        print("STOP : Aucun article trouvé au total. Vérifie le problème 'inspect.py'.")
        return

    # 2. Convertir en DataFrame
    print(f"\nCréation du tableau avec {len(all_data)} articles...")
    df = pd.DataFrame(all_data)

    # 3. Nettoyage Date
    # On cherche la bonne colonne
    col_date = None
    for c in ['date_published', 'date', 'created_at', 'published_at']:
        if c in df.columns:
            col_date = c
            break
            
    if col_date:
        print(f"Formatage des dates (colonne: {col_date})...")
        df[col_date] = pd.to_datetime(df[col_date], errors='coerce')
        df = df.dropna(subset=[col_date])
        df = df.rename(columns={col_date: 'date'}) # On standardise le nom
        
        # On garde les colonnes vitales
        cols_utiles = ['date', 'title', 'kws', 'loc', 'org', 'per', 'url', 'content']
        cols_finales = [c for c in cols_utiles if c in df.columns]
        df = df[cols_finales]
        
        # Sauvegarde
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Succès ! Fichier sauvegardé : {OUTPUT_FILE}")
    else:
        print("Erreur : Impossible de trouver une date dans les colonnes:", df.columns)

if __name__ == "__main__":
    load_and_clean()