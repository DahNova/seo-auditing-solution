"""
Issue Migration Utility

This module provides utilities to migrate from the old distributed issue system
to the new centralized Italian issue registry with granular format prioritization.
"""

from typing import Dict, List, Optional, Tuple
import logging
from app.core.issue_registry import IssueRegistry, IssueDefinition, IssueFormat, IssueSeverity

logger = logging.getLogger(__name__)


class IssueMigrationUtility:
    """
    Utility class for migrating from legacy issue management to centralized registry
    """
    
    # Mapping of old issue types to new Italian issue types
    MIGRATION_MAP = {
        # Legacy English -> New Italian
        "missing_title": "title_mancante",
        "title_too_short": "title_troppo_corto",
        "title_too_long": "title_troppo_lungo",
        "missing_meta_description": "meta_description_mancante",
        "meta_desc_too_short": "meta_description_troppo_corta",
        "meta_desc_too_long": "meta_description_troppo_lunga",
        "missing_h1": "h1_mancante",
        "multiple_h1": "h1_multipli",
        "empty_h1": "h1_vuoto",
        "h1_too_short": "h1_troppo_corto",
        "h1_too_long": "h1_troppo_lungo",
        "duplicate_h1_title": "h1_duplicato_title",
        "h1_too_similar_title": "h1_troppo_simile_title",
        "broken_heading_hierarchy": "gerarchia_heading_rotta",
        "excessive_headings": "heading_eccessivi",
        "missing_canonical": "canonical_mancante",
        "missing_schema": "schema_markup_mancante",
        "missing_schema_markup": "schema_markup_mancante",
        "contenuto_scarso": "contenuto_scarso",  # Already Italian
        "contenuto_insufficiente": "contenuto_insufficiente",  # Already Italian
        "poor_readability": "leggibilita_scarsa",
        "keyword_stuffing": "keyword_stuffing",  # Keep as is
        "duplicate_content": "contenuto_duplicato",
        "outdated_content": "contenuto_datato",
        "no_clear_keywords": "parole_chiave_non_chiare",
        "long_sentences": "frasi_troppo_lunghe",
        "no_headings": "nessun_heading",
        "missing_internal_links": "link_interni_mancanti",
        "images_missing_alt": "immagine_senza_alt",
        "image_missing_alt": "immagine_senza_alt",
        "image_without_alt": "immagine_senza_alt",
        "etichette_form_mancanti": "etichette_form_mancanti",  # Already Italian
        "missing_accessibility_features": "funzionalita_accessibilita_mancanti",
        "keyboard_navigation_issues": "problemi_navigazione_tastiera",
        "non_accessible_clickables": "elementi_cliccabili_non_accessibili",
        "vague_link_text": "testo_link_vago",
        "poor_color_contrast": "contrasto_colore_scarso",
        "missing_language_declaration": "dichiarazione_lingua_mancante",
        "blocking_css_resource": "risorsa_css_bloccante",
        "blocking_js_resource": "risorsa_js_bloccante",
        "too_many_images": "troppe_immagini",
        "large_image": "immagine_grande",
        "image_oversized": "immagine_sovradimensionata",
        "slow_ttfb": "ttfb_lento",
        "large_html": "html_grande",
        "no_compression": "compressione_mancante",
        "layout_shift_risk": "rischio_layout_shift",
        "slow_response": "risposta_lenta",
        "missing_viewport": "viewport_mancante",
        "ottimizzazione_mobile_scarsa": "ottimizzazione_mobile_scarsa",  # Already Italian
        "missing_og_tags": "tag_og_mancanti",
        "poor_social_meta": "meta_social_scarsa",
        "http_error_5xx": "errore_http_5xx",
        "http_error_4xx": "errore_http_4xx",
        "url_structure_issue": "struttura_url_problematica",
        
        # Additional legacy mappings
        "canonical_mancante": "canonical_mancante",  # Already Italian
        "h1_mancante": "h1_mancante",  # Already Italian
        "image_bad_filename": "immagine_nome_file_non_seo",
        "pdf_bad_filename": "pdf_nome_file_non_seo",
        "pdf_accessibility": "pdf_accessibilita"
    }
    
    @classmethod
    def migrate_issue_type(cls, old_issue_type: str) -> str:
        """
        Migrate an old issue type to the new Italian centralized format
        
        Args:
            old_issue_type: The old issue type identifier
            
        Returns:
            The new Italian issue type identifier
        """
        new_type = cls.MIGRATION_MAP.get(old_issue_type, old_issue_type)
        
        # Check if the new type exists in the registry
        if not IssueRegistry.get_issue(new_type):
            logger.warning(f"Issue type '{new_type}' not found in registry. Using original: '{old_issue_type}'")
            return old_issue_type
        
        return new_type
    
    @classmethod
    def get_preferred_issue_type(cls, issue_type: str) -> str:
        """
        Get the preferred (granular) version of an issue type
        
        Args:
            issue_type: The issue type to check
            
        Returns:
            The preferred issue type (granular over legacy)
        """
        # First migrate to new format if needed
        migrated_type = cls.migrate_issue_type(issue_type)
        
        # Check if it's a deprecated issue
        issue_def = IssueRegistry.get_issue(migrated_type)
        if issue_def and issue_def.deprecated and issue_def.replaces:
            return issue_def.replaces
        
        # Check if there's a granular version available
        if issue_def and issue_def.format_type == IssueFormat.LEGACY:
            # Look for granular replacement
            granular_issues = IssueRegistry.get_granular_issues()
            for granular_type, granular_def in granular_issues.items():
                if granular_def.replaces == migrated_type:
                    return granular_type
        
        return migrated_type
    
    @classmethod
    def validate_issue_type(cls, issue_type: str) -> bool:
        """
        Validate if an issue type exists in the registry
        
        Args:
            issue_type: The issue type to validate
            
        Returns:
            True if the issue type exists, False otherwise
        """
        return IssueRegistry.get_issue(issue_type) is not None
    
    @classmethod
    def get_issue_display_name(cls, issue_type: str) -> str:
        """
        Get the Italian display name for an issue type
        
        Args:
            issue_type: The issue type identifier
            
        Returns:
            The Italian display name
        """
        # Migrate to new format first
        migrated_type = cls.migrate_issue_type(issue_type)
        
        # Get from registry
        issue_def = IssueRegistry.get_issue(migrated_type)
        if issue_def:
            return issue_def.name_it
        
        # Fallback to formatted version of the type
        return issue_type.replace('_', ' ').title()
    
    @classmethod
    def get_issue_severity(cls, issue_type: str) -> IssueSeverity:
        """
        Get the severity for an issue type
        
        Args:
            issue_type: The issue type identifier
            
        Returns:
            The severity enum value
        """
        # Migrate to new format first
        migrated_type = cls.migrate_issue_type(issue_type)
        
        # Get from registry
        issue_def = IssueRegistry.get_issue(migrated_type)
        if issue_def:
            return issue_def.severity
        
        # Fallback to medium severity
        return IssueSeverity.MEDIUM
    
    @classmethod
    def get_issue_recommendations(cls, issue_type: str) -> List[str]:
        """
        Get recommendations for an issue type
        
        Args:
            issue_type: The issue type identifier
            
        Returns:
            List of Italian recommendations
        """
        # Migrate to new format first
        migrated_type = cls.migrate_issue_type(issue_type)
        
        # Get from registry
        issue_def = IssueRegistry.get_issue(migrated_type)
        if issue_def:
            return issue_def.recommendations
        
        # Fallback to generic recommendation
        return ["Risolvi questo problema SEO"]
    
    @classmethod
    def should_escalate_severity(cls, issue_type: str, context: Dict) -> Optional[IssueSeverity]:
        """
        Check if an issue should have escalated severity based on context
        
        Args:
            issue_type: The issue type identifier
            context: Context data for escalation rules
            
        Returns:
            Escalated severity if applicable, None otherwise
        """
        # Migrate to new format first
        migrated_type = cls.migrate_issue_type(issue_type)
        
        # Use registry escalation logic
        return IssueRegistry.should_escalate(migrated_type, context)
    
    @classmethod
    def get_migration_report(cls) -> Dict:
        """
        Generate a migration report showing the mapping between old and new issue types
        
        Returns:
            Dictionary with migration statistics and mappings
        """
        report = {
            "total_mappings": len(cls.MIGRATION_MAP),
            "granular_issues": len(IssueRegistry.get_granular_issues()),
            "legacy_issues": len(IssueRegistry.get_legacy_issues()),
            "deprecated_issues": len([i for i in IssueRegistry.get_all_issues().values() if i.deprecated]),
            "mappings": cls.MIGRATION_MAP,
            "unmapped_registry_issues": []
        }
        
        # Find registry issues not in migration map
        registry_issues = set(IssueRegistry.get_all_issues().keys())
        mapped_issues = set(cls.MIGRATION_MAP.values())
        unmapped = registry_issues - mapped_issues
        report["unmapped_registry_issues"] = list(unmapped)
        
        return report
    
    @classmethod
    def create_analyzer_factory(cls, old_analyzer_method):
        """
        Create a factory that wraps old analyzer methods to use new issue types
        
        Args:
            old_analyzer_method: The old analyzer method to wrap
            
        Returns:
            Wrapped method that uses centralized registry
        """
        def wrapped_method(*args, **kwargs):
            # Call the original method
            result = old_analyzer_method(*args, **kwargs)
            
            # If result is a list of issues, migrate their types
            if isinstance(result, list):
                for issue in result:
                    if hasattr(issue, 'type'):
                        issue.type = cls.migrate_issue_type(issue.type)
            
            # If result is a single issue, migrate its type
            elif hasattr(result, 'type'):
                result.type = cls.migrate_issue_type(result.type)
            
            return result
        
        return wrapped_method
    
    @classmethod
    def validate_analyzer_consistency(cls, analyzer_class) -> List[str]:
        """
        Validate that an analyzer class uses consistent issue types
        
        Args:
            analyzer_class: The analyzer class to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check for hardcoded issue types in the class
        import inspect
        source = inspect.getsource(analyzer_class)
        
        # Look for potential hardcoded issue types
        for old_type, new_type in cls.MIGRATION_MAP.items():
            if f"'{old_type}'" in source or f'"{old_type}"' in source:
                warnings.append(f"Found hardcoded legacy issue type '{old_type}' - should use '{new_type}'")
        
        return warnings


# Convenience functions for common operations
def migrate_issue_type(old_type: str) -> str:
    """Convenience function to migrate an issue type"""
    return IssueMigrationUtility.migrate_issue_type(old_type)


def get_preferred_issue_type(issue_type: str) -> str:
    """Convenience function to get preferred issue type"""
    return IssueMigrationUtility.get_preferred_issue_type(issue_type)


def get_issue_display_name(issue_type: str) -> str:
    """Convenience function to get issue display name"""
    return IssueMigrationUtility.get_issue_display_name(issue_type)


def get_issue_severity(issue_type: str) -> IssueSeverity:
    """Convenience function to get issue severity"""
    return IssueMigrationUtility.get_issue_severity(issue_type)


def get_issue_recommendations(issue_type: str) -> List[str]:
    """Convenience function to get issue recommendations"""
    return IssueMigrationUtility.get_issue_recommendations(issue_type)