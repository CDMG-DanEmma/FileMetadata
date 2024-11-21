
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging
from PyQt6.QtCore import QObject, pyqtSignal

class SearchModel(QObject):
    searchCompleted = pyqtSignal(pd.DataFrame)
    searchStarted = pyqtSignal()
    searchError = pyqtSignal(str)

    def __init__(self, metadata_model):
        super().__init__()
        self.metadata_model = metadata_model
        self.search_history = []
        self.max_history = 50
        self.setup_search()

    def setup_search(self):
        """Initialize search functionality"""
        try:
            self.search_cache = {}
            self.last_search = None
            logging.info("Search model initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing search model: {str(e)}")

    def execute_search(self, search_params: Dict) -> None:
        """
        Execute search based on provided parameters
        
        Parameters:
        - search_params: Dictionary containing search criteria
            {
                'text': str,           # Free text search
                'filters': Dict,       # Metadata filters
                'date_range': tuple,   # (start_date, end_date)
                'sort_by': str,        # Field to sort by
                'sort_order': str      # 'asc' or 'desc'
            }
        """
        try:
            self.searchStarted.emit()
            
            # Check cache first
            cache_key = str(search_params)
            if cache_key in self.search_cache:
                self.searchCompleted.emit(self.search_cache[cache_key])
                return

            # Build search query
            query_result = self._build_search_query(search_params)
            
            # Apply filters
            filtered_results = self._apply_filters(query_result, search_params['filters'])
            
            # Sort results
            sorted_results = self._sort_results(
                filtered_results, 
                search_params.get('sort_by'),
                search_params.get('sort_order', 'asc')
            )

            # Cache results
            self.cache_results(cache_key, sorted_results)
            
            # Update search history
            self._update_search_history(search_params)
            
            self.searchCompleted.emit(sorted_results)

        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            logging.error(error_msg)
            self.searchError.emit(error_msg)

    def _build_search_query(self, search_params: Dict) -> pd.DataFrame:
        """Build and execute the main search query"""
        text_search = search_params.get('text', '').lower()
        
        if not text_search:
            return self.metadata_model.metadata_df.copy()
            
        # Search across all text columns
        mask = pd.Series(False, index=self.metadata_model.metadata_df.index)
        
        for column in self.metadata_model.metadata_df.select_dtypes(include=['object']):
            mask |= self.metadata_model.metadata_df[column].astype(str).str.lower().str.contains(text_search, na=False)
            
        return self.metadata_model.metadata_df[mask]

    def _apply_filters(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply metadata filters to results"""
        if not filters:
            return df
            
        filtered_df = df.copy()
        
        for field, value in filters.items():
            if value and value != "All":
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[field].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[field] == value]
                    
        return filtered_df

    def _sort_results(self, df: pd.DataFrame, sort_by: Optional[str], 
                     sort_order: str) -> pd.DataFrame:
        """Sort search results"""
        if sort_by and sort_by in df.columns:
            ascending = sort_order.lower() == 'asc'
            return df.sort_values(by=sort_by, ascending=ascending)
        return df

    def cache_results(self, cache_key: str, results: pd.DataFrame) -> None:
        """Cache search results"""
        self.search_cache[cache_key] = results
        
        # Limit cache size
        if len(self.search_cache) > 100:
            # Remove oldest entries
            oldest_keys = list(self.search_cache.keys())[:-50]
            for key in oldest_keys:
                del self.search_cache[key]

    def _update_search_history(self, search_params: Dict) -> None:
        """Update search history"""
        self.search_history.insert(0, {
            'params': search_params,
            'timestamp': datetime.now(),
            'results_count': len(self.search_cache[str(search_params)])
        })
        
        # Limit history size
        if len(self.search_history) > self.max_history:
            self.search_history.pop()

    def get_search_suggestions(self, partial_text: str) -> List[str]:
        """Get search suggestions based on partial text"""
        suggestions = []
        if len(partial_text) < 2:
            return suggestions

        # Check recent searches
        for search in self.search_history:
            if partial_text.lower() in search['params'].get('text', '').lower():
                suggestions.append(search['params']['text'])

        # Check metadata values
        for column in self.metadata_model.metadata_df.select_dtypes(include=['object']):
            column_values = self.metadata_model.metadata_df[column].astype(str)
            matches = column_values[
                column_values.str.lower().str.contains(partial_text.lower(), na=False)
            ].unique()
            suggestions.extend(matches)

        # Remove duplicates and limit suggestions
        return list(dict.fromkeys(suggestions))[:10]

    def get_popular_searches(self) -> List[Dict]:
        """Get most popular recent searches"""
        search_counts = {}
        
        for search in self.search_history:
            search_text = search['params'].get('text', '')
            if search_text:
                if search_text in search_counts:
                    search_counts[search_text]['count'] += 1
                else:
                    search_counts[search_text] = {
                        'text': search_text,
                        'count': 1,
                        'last_used': search['timestamp']
                    }

        # Sort by count and recency
        popular_searches = sorted(
            search_counts.values(),
            key=lambda x: (x['count'], x['last_used']),
            reverse=True
        )

        return popular_searches[:5]

    def clear_search_cache(self) -> None:
        """Clear search cache"""
        self.search_cache.clear()

    def clear_search_history(self) -> None:
        """Clear search history"""
        self.search_history.clear()

