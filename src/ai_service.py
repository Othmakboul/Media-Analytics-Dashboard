"""
Groq AI Service Module
Handles Groq API integration, context preparation, and response generation.
"""

import os
import pandas as pd
import tiktoken
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from .ai_prompts import (
    build_system_prompt,
    detect_query_type,
    CONTEXT_TEMPLATE,
    format_entity_list,
    format_article_samples,
    format_filter_info
)
from .data_processing import explode_entities


class GroqAIService:
    """
    Service class for Groq AI integration.
    Manages API communication, context preparation, and response generation.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the Groq AI service.

        Args:
            model: Groq model to use (default: llama-3.3-70b-versatile for good reasoning)
        """
        # Load environment variables
        load_dotenv()

        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your_groq_api_key_here':
            raise ValueError(
                "GROQ_API_KEY n'est pas configurée. "
                "Veuillez ajouter votre clé API dans le fichier .env"
            )

        self.client = Groq(api_key=api_key)
        self.model = model
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding, close enough

    def count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a text string.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def prepare_data_context(
        self,
        df: pd.DataFrame,
        filters: Dict[str, Any],
        max_articles: int = 15
    ) -> str:
        """
        Prepares a structured context from the filtered dataframe.

        Args:
            df: Filtered DataFrame
            filters: Dictionary with filter info (start_date, end_date, keywords, locations)
            max_articles: Maximum number of article samples to include

        Returns:
            Formatted context string
        """
        if df.empty:
            return "Aucun article ne correspond aux filtres actuels."

        # Extract metadata
        total_articles = len(df)
        start_date = df['date'].min().strftime('%Y-%m-%d')
        end_date = df['date'].max().strftime('%Y-%m-%d')

        # Format filter information
        selected_kws = filters.get('keywords', [])
        selected_locs = filters.get('locations', [])
        kws_str, locs_str = format_filter_info(selected_kws, selected_locs)

        # Get top entities using explode_entities
        top_keywords = explode_entities(df, 'kws').value_counts()
        top_locations = explode_entities(df, 'loc').value_counts()
        top_persons = explode_entities(df, 'per').value_counts()
        top_organizations = explode_entities(df, 'org').value_counts()

        # Format entity lists
        kws_formatted = format_entity_list(top_keywords, 'mots-clés', top_n=10)
        locs_formatted = format_entity_list(top_locations, 'lieux', top_n=10)
        pers_formatted = format_entity_list(top_persons, 'personnalités', top_n=10)
        orgs_formatted = format_entity_list(top_organizations, 'organisations', top_n=10)

        # Sort by date descending and format article samples
        df_sorted = df.sort_values('date', ascending=False)
        articles_formatted = format_article_samples(df_sorted, max_articles=max_articles)

        # Build complete context using template
        context = CONTEXT_TEMPLATE.format(
            total_articles=total_articles,
            start_date=start_date,
            end_date=end_date,
            selected_keywords=kws_str,
            selected_locations=locs_str,
            top_keywords=kws_formatted,
            top_locations=locs_formatted,
            top_persons=pers_formatted,
            top_organizations=orgs_formatted,
            sample_articles=articles_formatted
        )

        return context

    def truncate_context(self, context: str, max_tokens: int = 6000) -> str:
        """
        Truncates context if it exceeds max tokens.
        Uses a simple truncation strategy: keep beginning and end, remove middle.

        Args:
            context: The context string
            max_tokens: Maximum allowed tokens

        Returns:
            Truncated context if necessary
        """
        token_count = self.count_tokens(context)

        if token_count <= max_tokens:
            return context

        # Simple truncation: keep essential parts
        lines = context.split('\n')

        # Keep first 60% and last 20% of lines (metadata + some samples)
        keep_start = int(len(lines) * 0.6)
        keep_end = int(len(lines) * 0.2)

        truncated_lines = lines[:keep_start] + [
            "\n[... Contenu tronqué pour respecter les limites de tokens ...]\n"
        ] + lines[-keep_end:]

        truncated_context = '\n'.join(truncated_lines)

        # Verify truncation worked
        if self.count_tokens(truncated_context) > max_tokens:
            # More aggressive truncation
            truncated_context = context[:int(len(context) * 0.5)] + "\n[... Tronqué ...]"

        return truncated_context

    def generate_response(
        self,
        user_query: str,
        data_context: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates an AI response using Groq API.

        Args:
            user_query: The user's question
            data_context: Prepared data context
            query_type: Optional explicit query type (auto-detected if None)

        Returns:
            Dictionary with 'success' (bool), 'message' (str), and optional 'error' (str)
        """
        try:
            # Detect query type if not provided
            if query_type is None:
                query_type = detect_query_type(user_query)

            # Build appropriate system prompt
            system_prompt = build_system_prompt(query_type)

            # Truncate context if needed
            truncated_context = self.truncate_context(data_context, max_tokens=6000)

            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"{truncated_context}\n\n---\n\n**Question de l'utilisateur** : {user_query}"
                }
            ]

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )

            # Extract response content
            ai_message = response.choices[0].message.content

            return {
                'success': True,
                'message': ai_message,
                'query_type': query_type
            }

        except Exception as e:
            error_msg = str(e)

            # Handle specific error types
            if 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                return {
                    'success': False,
                    'message': "Clé API Groq invalide. Veuillez vérifier votre fichier .env",
                    'error': error_msg
                }
            elif 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                return {
                    'success': False,
                    'message': "Trop de requêtes. Veuillez réessayer dans quelques secondes",
                    'error': error_msg
                }
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return {
                    'success': False,
                    'message': "Erreur de connexion. Vérifiez votre connexion Internet",
                    'error': error_msg
                }
            else:
                return {
                    'success': False,
                    'message': f"Erreur inattendue : {error_msg}",
                    'error': error_msg
                }


# Singleton instance (optional, for caching)
_ai_service_instance = None


def get_ai_service() -> GroqAIService:
    """
    Returns a singleton instance of GroqAIService.
    Useful for maintaining state across callback calls.
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = GroqAIService()
    return _ai_service_instance
