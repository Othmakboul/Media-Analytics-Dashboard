"""
AI Prompt Engineering Module
Contains system prompts, context templates, and helper functions for Groq AI integration.
"""

import pandas as pd

# --- System Prompts ---

SYSTEM_PROMPT_BASE = """Vous êtes un analyste IA pour un tableau de bord d'analytique média analysant un corpus d'articles de presse français.

Votre rôle est de fournir des analyses pertinentes basées sur l'ensemble de données actuellement filtré par l'utilisateur.

Les données disponibles contiennent :
- date : Date de publication
- title : Titre de l'article
- kws : Mots-clés
- loc : Lieux mentionnés
- org : Organisations mentionnées
- per : Personnalités mentionnées
- content : Contenu de l'article

Fournissez des réponses claires, concises et basées sur les données en français. Utilisez des puces et un formatage structuré quand approprié.

IMPORTANT : Basez vos réponses UNIQUEMENT sur les données fournies dans le contexte. Ne faites pas d'affirmations non fondées sur les données."""

SYSTEM_PROMPT_TREND = """Vous êtes un analyste IA spécialisé dans l'analyse de tendances pour un tableau de bord d'analytique média.

Analysez les tendances temporelles, l'évolution des thématiques, et les changements dans le corpus d'articles filtrés.

Concentrez-vous sur :
- L'évolution dans le temps
- Les pics d'activité
- Les changements de fréquence
- Les patterns émergents

Basez-vous UNIQUEMENT sur les données fournies."""

SYSTEM_PROMPT_SENTIMENT = """Vous êtes un analyste IA spécialisé dans l'analyse de sentiment pour un tableau de bord d'analytique média.

Analysez le ton, le sentiment et la perception dans les articles filtrés.

Considérez :
- Les mots-clés positifs/négatifs
- Le contexte des mentions
- Les entités associées
- Le ton général

Basez-vous UNIQUEMENT sur les données fournies."""

SYSTEM_PROMPT_SUMMARY = """Vous êtes un analyste IA spécialisé dans la synthèse pour un tableau de bord d'analytique média.

Fournissez un aperçu concis et informatif du corpus d'articles filtrés.

Incluez :
- Les thèmes principaux
- Les entités clés
- La période couverte
- Les points saillants

Basez-vous UNIQUEMENT sur les données fournies."""

SYSTEM_PROMPT_ENTITY = """Vous êtes un analyste IA spécialisé dans l'analyse d'entités pour un tableau de bord d'analytique média.

Analysez les personnes, lieux et organisations mentionnés dans les articles filtrés.

Concentrez-vous sur :
- Les fréquences de mention
- Les co-occurrences
- Le contexte des mentions
- Les relations entre entités

Basez-vous UNIQUEMENT sur les données fournies."""

# --- Context Template ---

CONTEXT_TEMPLATE = """
## Aperçu du Dataset Filtré

- **Total d'articles** : {total_articles}
- **Période** : du {start_date} au {end_date}
- **Filtres appliqués** :
  - Mots-clés sélectionnés : {selected_keywords}
  - Lieux sélectionnés : {selected_locations}

---

## Top Mots-Clés (fréquence)
{top_keywords}

## Top Lieux
{top_locations}

## Top Personnalités
{top_persons}

## Top Organisations
{top_organizations}

---

## Échantillon d'Articles (les plus récents)
{sample_articles}
"""

# --- Query Type Detection ---

def detect_query_type(query: str) -> str:
    """
    Detects the type of query based on keywords.
    Returns one of: 'trend', 'sentiment', 'summary', 'entity', 'general'
    """
    query_lower = query.lower()

    # Trend analysis keywords
    if any(kw in query_lower for kw in ['tendance', 'évolution', 'croissance', 'changement', 'progression', 'temporel', 'temps']):
        return 'trend'

    # Sentiment analysis keywords
    if any(kw in query_lower for kw in ['sentiment', 'opinion', 'perception', 'ressenti', 'positif', 'négatif', 'ton']):
        return 'sentiment'

    # Summary keywords
    if any(kw in query_lower for kw in ['résumé', 'synthèse', 'aperçu', 'global', 'général', 'vue d\'ensemble']):
        return 'summary'

    # Entity analysis keywords
    if any(kw in query_lower for kw in ['qui', 'où', 'quelle organisation', 'personnalité', 'personne', 'lieu', 'pays', 'ville']):
        return 'entity'

    return 'general'


def build_system_prompt(query_type: str) -> str:
    """
    Selects the appropriate system prompt based on query type.
    """
    prompts = {
        'trend': SYSTEM_PROMPT_TREND,
        'sentiment': SYSTEM_PROMPT_SENTIMENT,
        'summary': SYSTEM_PROMPT_SUMMARY,
        'entity': SYSTEM_PROMPT_ENTITY,
        'general': SYSTEM_PROMPT_BASE
    }
    return prompts.get(query_type, SYSTEM_PROMPT_BASE)


# --- Helper Functions for Formatting ---

def format_entity_list(series: pd.Series, entity_type: str, top_n: int = 10) -> str:
    """
    Formats a series of entity counts as a bullet list.

    Args:
        series: Pandas Series with entity counts
        entity_type: Name of the entity type (for display)
        top_n: Number of top entities to include

    Returns:
        Formatted string with bullet points
    """
    if series.empty:
        return f"- Aucun {entity_type} trouvé"

    top_entities = series.head(top_n)
    lines = [f"- {entity} : {count}" for entity, count in top_entities.items()]
    return '\n'.join(lines)


def format_article_sample(row: pd.Series, include_content: bool = False) -> str:
    """
    Formats a single article row as a structured block.

    Args:
        row: Pandas Series representing one article
        include_content: Whether to include full article content (can be long)

    Returns:
        Formatted article string
    """
    date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])

    # Format entities
    kws = ', '.join(row['kws'][:5]) if row['kws'] else 'Aucun'
    locs = ', '.join(row['loc'][:3]) if row['loc'] else 'Aucun'
    orgs = ', '.join(row['org'][:3]) if row['org'] else 'Aucune'
    pers = ', '.join(row['per'][:3]) if row['per'] else 'Aucune'

    article_text = f"""
### {row['title']}
- **Date** : {date_str}
- **Mots-clés** : {kws}
- **Lieux** : {locs}
- **Organisations** : {orgs}
- **Personnalités** : {pers}
"""

    if include_content and row['content']:
        # Truncate content to avoid token overflow
        content_preview = row['content'][:300] + '...' if len(row['content']) > 300 else row['content']
        article_text += f"- **Aperçu** : {content_preview}\n"

    return article_text


def format_article_samples(df: pd.DataFrame, max_articles: int = 15) -> str:
    """
    Formats multiple articles as a concatenated string.

    Args:
        df: DataFrame of articles (should be sorted by date descending)
        max_articles: Maximum number of articles to include

    Returns:
        Formatted string of article samples
    """
    if df.empty:
        return "- Aucun article dans la sélection filtrée"

    # Take most recent articles
    sample_df = df.head(max_articles)

    articles = [format_article_sample(row, include_content=False) for _, row in sample_df.iterrows()]
    return '\n'.join(articles)


def format_filter_info(selected_keywords, selected_locations) -> tuple:
    """
    Formats filter information for display in context.

    Returns:
        Tuple of (keywords_str, locations_str)
    """
    kws_str = ', '.join(selected_keywords) if selected_keywords else 'Aucun'
    locs_str = ', '.join(selected_locations) if selected_locations else 'Aucun'
    return kws_str, locs_str
