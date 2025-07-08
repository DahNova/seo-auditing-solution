"""
Centralized SEO Issue Registry

This module provides a single source of truth for all SEO issues monitored by the platform.
All issues are defined in Italian with granular format prioritization.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class IssueCategory(Enum):
    """Categories of SEO issues"""
    TECHNICAL_SEO = "technical_seo"
    ON_PAGE = "on_page"
    CONTENT = "content"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    MOBILE = "mobile"
    SOCIAL = "social"
    SECURITY = "security"


class IssueSeverity(Enum):
    """Severity levels for SEO issues"""
    CRITICAL = "critical"  # -10.0 points
    HIGH = "high"         # -6.0 points
    MEDIUM = "medium"     # -3.0 points
    LOW = "low"          # -1.0 points


class IssueFormat(Enum):
    """Format types for issue detection"""
    GRANULAR = "granular"    # Individual resource-level issues (preferred)
    LEGACY = "legacy"        # Aggregate issues (deprecated)
    CONSOLIDATED = "consolidated"  # Multiple resources grouped


@dataclass
class IssueDefinition:
    """Definition of an SEO issue"""
    issue_type: str
    name_it: str
    description_it: str
    category: IssueCategory
    severity: IssueSeverity
    format_type: IssueFormat
    icon: str
    recommendations: List[str]
    escalation_rules: Optional[Dict[str, Any]] = None
    deprecated: bool = False
    replaces: Optional[str] = None  # For legacy issues being replaced


class IssueRegistry:
    """
    Centralized registry for all SEO issues.
    Prioritizes granular issues over legacy ones.
    """

    # Main issue registry with Italian names and granular prioritization
    ISSUES: Dict[str, IssueDefinition] = {
        
        # =============================================
        # TECHNICAL SEO ISSUES (Granular Format)
        # =============================================
        
        "title_mancante": IssueDefinition(
            issue_type="title_mancante",
            name_it="Title Tag Mancante",
            description_it="La pagina non ha un tag title definito",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.CRITICAL,
            format_type=IssueFormat.GRANULAR,
            icon="bi-tag",
            recommendations=[
                "Aggiungi un tag title unico e descrittivo",
                "Mantieni il title tra 50-60 caratteri",
                "Includi la parola chiave principale"
            ]
        ),
        
        "title_troppo_corto": IssueDefinition(
            issue_type="title_troppo_corto",
            name_it="Title Troppo Corto",
            description_it="Il tag title è troppo corto per essere efficace",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-tag",
            recommendations=[
                "Espandi il title ad almeno 50 caratteri",
                "Aggiungi informazioni descrittive rilevanti",
                "Includi modificatori di parole chiave"
            ],
            escalation_rules={"min_length": 10, "escalate_to": "high"}
        ),
        
        "title_troppo_lungo": IssueDefinition(
            issue_type="title_troppo_lungo",
            name_it="Title Troppo Lungo",
            description_it="Il tag title supera i 60 caratteri e potrebbe essere troncato",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-tag",
            recommendations=[
                "Riduci il title a massimo 60 caratteri",
                "Mantieni le parole chiave principali all'inizio",
                "Rimuovi parole non essenziali"
            ]
        ),
        
        "meta_description_mancante": IssueDefinition(
            issue_type="meta_description_mancante",
            name_it="Meta Description Mancante",
            description_it="La pagina non ha una meta description definita",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-card-text",
            recommendations=[
                "Aggiungi una meta description unica e coinvolgente",
                "Mantieni la lunghezza tra 140-155 caratteri",
                "Includi una call-to-action chiara"
            ]
        ),
        
        "meta_description_troppo_corta": IssueDefinition(
            issue_type="meta_description_troppo_corta",
            name_it="Meta Description Troppo Corta",
            description_it="La meta description è troppo corta per essere efficace",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-card-text",
            recommendations=[
                "Espandi la meta description ad almeno 140 caratteri",
                "Aggiungi dettagli persuasivi sul contenuto",
                "Includi benefici chiave per l'utente"
            ]
        ),
        
        "meta_description_troppo_lunga": IssueDefinition(
            issue_type="meta_description_troppo_lunga",
            name_it="Meta Description Troppo Lunga",
            description_it="La meta description supera i 155 caratteri e potrebbe essere troncata",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-card-text",
            recommendations=[
                "Riduci la meta description a massimo 155 caratteri",
                "Mantieni le informazioni più importanti all'inizio",
                "Assicurati che sia ancora persuasiva"
            ]
        ),
        
        "h1_mancante": IssueDefinition(
            issue_type="h1_mancante",
            name_it="H1 Mancante",
            description_it="La pagina non ha un tag H1 definito",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Aggiungi un H1 unico e descrittivo",
                "Mantieni l'H1 tra 10-70 caratteri",
                "Differenzia l'H1 dal title tag"
            ]
        ),
        
        "h1_multipli": IssueDefinition(
            issue_type="h1_multipli",
            name_it="H1 Multipli",
            description_it="La pagina ha più di un tag H1",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Mantieni un solo H1 per pagina",
                "Converti gli H1 aggiuntivi in H2 o H3",
                "Assicurati che l'H1 principale sia il più importante"
            ]
        ),
        
        "h1_vuoto": IssueDefinition(
            issue_type="h1_vuoto",
            name_it="H1 Vuoto",
            description_it="Il tag H1 è presente ma vuoto",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Aggiungi contenuto significativo nell'H1",
                "Includi la parola chiave principale",
                "Rendi l'H1 descrittivo del contenuto della pagina"
            ]
        ),
        
        "h1_troppo_corto": IssueDefinition(
            issue_type="h1_troppo_corto",
            name_it="H1 Troppo Corto",
            description_it="L'H1 è troppo corto per essere efficace",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Espandi l'H1 ad almeno 10 caratteri",
                "Aggiungi parole chiave rilevanti",
                "Rendi l'H1 più descrittivo"
            ]
        ),
        
        "h1_troppo_lungo": IssueDefinition(
            issue_type="h1_troppo_lungo",
            name_it="H1 Troppo Lungo",
            description_it="L'H1 supera i 70 caratteri e potrebbe essere troppo lungo",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Riduci l'H1 a massimo 70 caratteri",
                "Mantieni le parole chiave principali",
                "Sii più conciso e diretto"
            ]
        ),
        
        "h1_duplicato_title": IssueDefinition(
            issue_type="h1_duplicato_title",
            name_it="H1 Identico al Title",
            description_it="L'H1 è identico al tag title",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Differenzia l'H1 dal title tag",
                "Usa variazioni delle parole chiave",
                "Ottimizza per diverse intenzioni di ricerca"
            ]
        ),
        
        "h1_troppo_simile_title": IssueDefinition(
            issue_type="h1_troppo_simile_title",
            name_it="H1 Troppo Simile al Title",
            description_it="L'H1 è molto simile al tag title",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.LOW,
            format_type=IssueFormat.GRANULAR,
            icon="bi-type-h1",
            recommendations=[
                "Diversifica maggiormente H1 e title",
                "Usa sinonimi e variazioni",
                "Ottimizza per parole chiave correlate"
            ]
        ),
        
        "gerarchia_heading_rotta": IssueDefinition(
            issue_type="gerarchia_heading_rotta",
            name_it="Gerarchia Heading Rotta",
            description_it="La gerarchia degli heading non è corretta (es. H2 senza H1)",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-list-ol",
            recommendations=[
                "Correggi la gerarchia degli heading",
                "Inizia sempre con H1, poi H2, H3, etc.",
                "Non saltare livelli di heading"
            ]
        ),
        
        "heading_eccessivi": IssueDefinition(
            issue_type="heading_eccessivi",
            name_it="Heading Eccessivi",
            description_it="La pagina ha troppi tag heading (più di 15)",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.LOW,
            format_type=IssueFormat.GRANULAR,
            icon="bi-list-ol",
            recommendations=[
                "Riduci il numero di heading",
                "Usa heading solo per strutturare il contenuto",
                "Considera l'uso di testo in grassetto invece di heading"
            ]
        ),
        
        "canonical_mancante": IssueDefinition(
            issue_type="canonical_mancante",
            name_it="Canonical Mancante",
            description_it="La pagina non ha un tag canonical definito",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-link",
            recommendations=[
                "Aggiungi un tag canonical appropriato",
                "Usa URL assoluti per il canonical",
                "Assicurati che punti alla versione preferita della pagina"
            ]
        ),
        
        "schema_markup_mancante": IssueDefinition(
            issue_type="schema_markup_mancante",
            name_it="Schema Markup Mancante",
            description_it="La pagina non ha markup schema strutturato",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-code-square",
            recommendations=[
                "Aggiungi markup schema appropriato",
                "Usa JSON-LD per implementare schema",
                "Implementa schema per il tipo di contenuto della pagina"
            ]
        ),
        
        # =============================================
        # CONTENT QUALITY ISSUES (Granular Format)
        # =============================================
        
        "contenuto_scarso": IssueDefinition(
            issue_type="contenuto_scarso",
            name_it="Contenuto Scarso",
            description_it="La pagina ha contenuto insufficiente (meno di 500 parole)",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-file-text",
            recommendations=[
                "Espandi il contenuto ad almeno 500 parole",
                "Aggiungi informazioni di valore per l'utente",
                "Includi dettagli e approfondimenti"
            ],
            escalation_rules={"min_words": 50, "escalate_to": "high"}
        ),
        
        "contenuto_insufficiente": IssueDefinition(
            issue_type="contenuto_insufficiente",
            name_it="Contenuto Insufficiente",
            description_it="La pagina ha contenuto estremamente limitato",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-file-text",
            recommendations=[
                "Aggiungi contenuto sostanziale alla pagina",
                "Fornisci informazioni utili e complete",
                "Evita pagine con contenuto minimo"
            ]
        ),
        
        "leggibilita_scarsa": IssueDefinition(
            issue_type="leggibilita_scarsa",
            name_it="Leggibilità Scarsa",
            description_it="Il contenuto ha un punteggio di leggibilità troppo basso",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-eye",
            recommendations=[
                "Semplifica il linguaggio utilizzato",
                "Usa frasi più brevi e chiare",
                "Struttura il contenuto con paragrafi e sottotitoli"
            ]
        ),
        
        "keyword_stuffing": IssueDefinition(
            issue_type="keyword_stuffing",
            name_it="Keyword Stuffing",
            description_it="Densità delle parole chiave troppo alta (oltre 3%)",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-exclamation-triangle",
            recommendations=[
                "Riduci la densità delle parole chiave",
                "Usa sinonimi e variazioni naturali",
                "Scrivi per gli utenti, non per i motori di ricerca"
            ]
        ),
        
        "contenuto_duplicato": IssueDefinition(
            issue_type="contenuto_duplicato",
            name_it="Contenuto Duplicato",
            description_it="Il contenuto è duplicato o molto simile ad altre pagine",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-files",
            recommendations=[
                "Crea contenuto unico e originale",
                "Differenzia il contenuto da altre pagine",
                "Usa canonical tag se appropriato"
            ]
        ),
        
        "contenuto_datato": IssueDefinition(
            issue_type="contenuto_datato",
            name_it="Contenuto Datato",
            description_it="Il contenuto contiene riferimenti a date passate senza aggiornamenti",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.LOW,
            format_type=IssueFormat.GRANULAR,
            icon="bi-calendar-x",
            recommendations=[
                "Aggiorna le date e informazioni obsolete",
                "Mantieni il contenuto fresco e attuale",
                "Rivedi regolarmente le informazioni temporali"
            ]
        ),
        
        "parole_chiave_non_chiare": IssueDefinition(
            issue_type="parole_chiave_non_chiare",
            name_it="Parole Chiave Non Chiare",
            description_it="Non sono identificabili parole chiave primarie chiare",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-search",
            recommendations=[
                "Identifica e ottimizza per parole chiave specifiche",
                "Concentrati su 1-2 parole chiave primarie",
                "Usa le parole chiave strategicamente nel contenuto"
            ]
        ),
        
        "frasi_troppo_lunghe": IssueDefinition(
            issue_type="frasi_troppo_lunghe",
            name_it="Frasi Troppo Lunghe",
            description_it="Le frasi hanno una lunghezza media superiore a 25 parole",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.LOW,
            format_type=IssueFormat.GRANULAR,
            icon="bi-text-paragraph",
            recommendations=[
                "Dividi le frasi lunghe in frasi più brevi",
                "Usa punteggiatura per migliorare la leggibilità",
                "Semplifica la struttura delle frasi"
            ]
        ),
        
        "nessun_heading": IssueDefinition(
            issue_type="nessun_heading",
            name_it="Nessun Heading",
            description_it="La pagina non ha alcuna struttura di heading",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-list-ol",
            recommendations=[
                "Aggiungi heading per strutturare il contenuto",
                "Usa H1, H2, H3 per organizzare le informazioni",
                "Migliora la scansionabilità del contenuto"
            ]
        ),
        
        "link_interni_mancanti": IssueDefinition(
            issue_type="link_interni_mancanti",
            name_it="Link Interni Mancanti",
            description_it="La pagina non ha link interni ad altre pagine del sito",
            category=IssueCategory.CONTENT,
            severity=IssueSeverity.LOW,
            format_type=IssueFormat.GRANULAR,
            icon="bi-link-45deg",
            recommendations=[
                "Aggiungi link interni rilevanti",
                "Collega a pagine correlate del sito",
                "Migliora l'architettura informativa"
            ]
        ),
        
        # =============================================
        # ACCESSIBILITY ISSUES (Granular Format)
        # =============================================
        
        "immagine_senza_alt": IssueDefinition(
            issue_type="immagine_senza_alt",
            name_it="Immagine Senza Alt",
            description_it="L'immagine non ha testo alternativo definito",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-image",
            recommendations=[
                "Aggiungi testo alt descrittivo e significativo",
                "Descrivi il contenuto e il contesto dell'immagine",
                "Usa alt vuoto per immagini decorative"
            ]
        ),
        
        "etichette_form_mancanti": IssueDefinition(
            issue_type="etichette_form_mancanti",
            name_it="Etichette Form Mancanti",
            description_it="I campi del form non hanno etichette appropriate",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-ui-checks",
            recommendations=[
                "Aggiungi etichette label ai campi del form",
                "Usa attributi for per collegare label e input",
                "Assicurati che ogni campo sia identificabile"
            ]
        ),
        
        "funzionalita_accessibilita_mancanti": IssueDefinition(
            issue_type="funzionalita_accessibilita_mancanti",
            name_it="Funzionalità Accessibilità Mancanti",
            description_it="La pagina manca di funzionalità di accessibilità importanti",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-universal-access",
            recommendations=[
                "Implementa attributi ARIA appropriati",
                "Assicurati che la pagina sia navigabile da tastiera",
                "Migliora il supporto per screen reader"
            ]
        ),
        
        "problemi_navigazione_tastiera": IssueDefinition(
            issue_type="problemi_navigazione_tastiera",
            name_it="Problemi Navigazione Tastiera",
            description_it="La pagina ha problemi di navigazione da tastiera",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-keyboard",
            recommendations=[
                "Assicurati che tutti gli elementi siano raggiungibili da tastiera",
                "Implementa un ordine di tab logico",
                "Fornisci indicatori di focus visibili"
            ]
        ),
        
        "elementi_cliccabili_non_accessibili": IssueDefinition(
            issue_type="elementi_cliccabili_non_accessibili",
            name_it="Elementi Cliccabili Non Accessibili",
            description_it="Gli elementi cliccabili non sono accessibili",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-cursor",
            recommendations=[
                "Usa elementi button o link appropriati",
                "Evita onclick su elementi non interattivi",
                "Assicurati che gli elementi siano accessibili da tastiera"
            ]
        ),
        
        "testo_link_vago": IssueDefinition(
            issue_type="testo_link_vago",
            name_it="Testo Link Vago",
            description_it="I link hanno testo non descrittivo (es. 'clicca qui')",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-link",
            recommendations=[
                "Usa testo di link descrittivo e significativo",
                "Evita testi generici come 'clicca qui'",
                "Descrivi la destinazione o l'azione del link"
            ]
        ),
        
        "contrasto_colore_scarso": IssueDefinition(
            issue_type="contrasto_colore_scarso",
            name_it="Contrasto Colore Scarso",
            description_it="Il rapporto di contrasto dei colori è insufficiente",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-palette",
            recommendations=[
                "Migliora il contrasto tra testo e sfondo",
                "Usa colori che rispettano le linee guida WCAG",
                "Testa il contrasto con strumenti di accessibilità"
            ]
        ),
        
        "dichiarazione_lingua_mancante": IssueDefinition(
            issue_type="dichiarazione_lingua_mancante",
            name_it="Dichiarazione Lingua Mancante",
            description_it="Il tag HTML non ha l'attributo lang definito",
            category=IssueCategory.ACCESSIBILITY,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-translate",
            recommendations=[
                "Aggiungi l'attributo lang al tag HTML",
                "Specifica la lingua principale del contenuto",
                "Usa codici lingua standard (es. lang='it')"
            ]
        ),
        
        # =============================================
        # PERFORMANCE ISSUES (Granular Format)
        # =============================================
        
        "risorsa_css_bloccante": IssueDefinition(
            issue_type="risorsa_css_bloccante",
            name_it="Risorsa CSS Bloccante",
            description_it="File CSS che blocca il rendering della pagina",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.CONSOLIDATED,
            icon="bi-filetype-css",
            recommendations=[
                "Usa preload per CSS critico",
                "Implementa CSS critico inline",
                "Carica CSS non critico in modo asincrono"
            ]
        ),
        
        "risorsa_js_bloccante": IssueDefinition(
            issue_type="risorsa_js_bloccante",
            name_it="Risorsa JS Bloccante",
            description_it="File JavaScript che blocca il rendering della pagina",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.CONSOLIDATED,
            icon="bi-filetype-js",
            recommendations=[
                "Usa async per script non critici",
                "Usa defer per script che dipendono dal DOM",
                "Sposta gli script non critici in fondo alla pagina"
            ],
            escalation_rules={"location": "head", "escalate_to": "high"}
        ),
        
        "troppe_immagini": IssueDefinition(
            issue_type="troppe_immagini",
            name_it="Troppe Immagini",
            description_it="Immagini che necessitano di ottimizzazione",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-images",
            recommendations=[
                "Comprimi le immagini mantenendo la qualità",
                "Usa formati moderni come WebP",
                "Implementa lazy loading per immagini below-the-fold"
            ]
        ),
        
        "immagine_grande": IssueDefinition(
            issue_type="immagine_grande",
            name_it="Immagine Grande",
            description_it="File immagine con dimensioni eccessive",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-image",
            recommendations=[
                "Riduci le dimensioni del file immagine",
                "Ottimizza la compressione",
                "Usa immagini responsive con srcset"
            ],
            escalation_rules={"file_size": "2MB", "escalate_to": "high"}
        ),
        
        "immagine_sovradimensionata": IssueDefinition(
            issue_type="immagine_sovradimensionata",
            name_it="Immagine Sovradimensionata",
            description_it="Immagine con dimensioni eccessive",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-image",
            recommendations=[
                "Ridimensiona l'immagine alle dimensioni necessarie",
                "Usa immagini responsive",
                "Considera l'uso di CDN per ottimizzazione automatica"
            ],
            escalation_rules={"file_size": "2MB", "escalate_to": "high"}
        ),
        
        "ttfb_lento": IssueDefinition(
            issue_type="ttfb_lento",
            name_it="TTFB Lento",
            description_it="Time to First Byte superiore a 600ms",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-speedometer",
            recommendations=[
                "Ottimizza le prestazioni del server",
                "Implementa caching efficace",
                "Usa una CDN per ridurre la latenza"
            ]
        ),
        
        "html_grande": IssueDefinition(
            issue_type="html_grande",
            name_it="HTML Grande",
            description_it="Dimensione HTML superiore a 100KB",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-file-code",
            recommendations=[
                "Minimizza l'HTML",
                "Rimuovi codice non necessario",
                "Usa compressione gzip/brotli"
            ],
            escalation_rules={"file_size": "2MB", "escalate_to": "high"}
        ),
        
        "compressione_mancante": IssueDefinition(
            issue_type="compressione_mancante",
            name_it="Compressione Mancante",
            description_it="Manca la compressione gzip/brotli",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-archive",
            recommendations=[
                "Abilita la compressione gzip o brotli",
                "Configura il server per compressione automatica",
                "Verifica che tutti i file di testo siano compressi"
            ]
        ),
        
        "rischio_layout_shift": IssueDefinition(
            issue_type="rischio_layout_shift",
            name_it="Rischio Layout Shift",
            description_it="Potenziale rischio di Cumulative Layout Shift",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-arrows-move",
            recommendations=[
                "Specifica dimensioni per immagini e video",
                "Evita inserimento dinamico di contenuto",
                "Usa skeleton loading per contenuto dinamico"
            ]
        ),
        
        "risposta_lenta": IssueDefinition(
            issue_type="risposta_lenta",
            name_it="Risposta Lenta",
            description_it="Tempo di risposta del server lento",
            category=IssueCategory.PERFORMANCE,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-hourglass",
            recommendations=[
                "Ottimizza le query del database",
                "Implementa caching server-side",
                "Considera l'upgrade dell'hosting"
            ]
        ),
        
        # =============================================
        # MOBILE & SOCIAL ISSUES (Granular Format)
        # =============================================
        
        "viewport_mancante": IssueDefinition(
            issue_type="viewport_mancante",
            name_it="Viewport Mancante",
            description_it="Manca il meta tag viewport per mobile",
            category=IssueCategory.MOBILE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-phone",
            recommendations=[
                "Aggiungi meta tag viewport",
                "Usa viewport responsive standard",
                "Testa la visualizzazione su dispositivi mobili"
            ]
        ),
        
        "ottimizzazione_mobile_scarsa": IssueDefinition(
            issue_type="ottimizzazione_mobile_scarsa",
            name_it="Ottimizzazione Mobile Scarsa",
            description_it="La pagina non è ottimizzata per dispositivi mobili",
            category=IssueCategory.MOBILE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-phone",
            recommendations=[
                "Implementa design responsive",
                "Ottimizza per touch interface",
                "Testa l'usabilità mobile"
            ]
        ),
        
        "tag_og_mancanti": IssueDefinition(
            issue_type="tag_og_mancanti",
            name_it="Tag Open Graph Mancanti",
            description_it="Mancano i meta tag Open Graph per social media",
            category=IssueCategory.SOCIAL,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-share",
            recommendations=[
                "Aggiungi meta tag Open Graph",
                "Includi og:title, og:description, og:image",
                "Ottimizza per condivisione social"
            ]
        ),
        
        "meta_social_scarsa": IssueDefinition(
            issue_type="meta_social_scarsa",
            name_it="Meta Social Scarsa",
            description_it="Ottimizzazione incompleta per social media",
            category=IssueCategory.SOCIAL,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-share",
            recommendations=[
                "Completa i meta tag social",
                "Aggiungi Twitter Card",
                "Ottimizza immagini per social sharing"
            ]
        ),
        
        # =============================================
        # HTTP & SECURITY ISSUES (Granular Format)
        # =============================================
        
        "errore_http_5xx": IssueDefinition(
            issue_type="errore_http_5xx",
            name_it="Errore Server 5xx",
            description_it="Errore server (500-599)",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.CRITICAL,
            format_type=IssueFormat.GRANULAR,
            icon="bi-exclamation-triangle",
            recommendations=[
                "Correggi l'errore server",
                "Verifica i log del server",
                "Contatta il supporto tecnico se necessario"
            ]
        ),
        
        "errore_http_4xx": IssueDefinition(
            issue_type="errore_http_4xx",
            name_it="Errore Client 4xx",
            description_it="Errore client (400-499)",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.GRANULAR,
            icon="bi-exclamation-triangle",
            recommendations=[
                "Correggi l'errore client",
                "Verifica URL e parametri",
                "Implementa redirect se necessario"
            ]
        ),
        
        "struttura_url_problematica": IssueDefinition(
            issue_type="struttura_url_problematica",
            name_it="Struttura URL Problematica",
            description_it="URL non SEO-friendly",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.GRANULAR,
            icon="bi-link",
            recommendations=[
                "Usa URL descrittivi e leggibili",
                "Evita parametri URL complessi",
                "Implementa URL rewriting"
            ]
        ),
        
        # =============================================
        # LEGACY ISSUES (Deprecated - Being Replaced)
        # =============================================
        
        "missing_title": IssueDefinition(
            issue_type="missing_title",
            name_it="Title Mancante (Legacy)",
            description_it="DEPRECATED: Usa title_mancante",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.CRITICAL,
            format_type=IssueFormat.LEGACY,
            icon="bi-tag",
            recommendations=["Migra a title_mancante"],
            deprecated=True,
            replaces="title_mancante"
        ),
        
        "missing_h1": IssueDefinition(
            issue_type="missing_h1",
            name_it="H1 Mancante (Legacy)",
            description_it="DEPRECATED: Usa h1_mancante",
            category=IssueCategory.ON_PAGE,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.LEGACY,
            icon="bi-type-h1",
            recommendations=["Migra a h1_mancante"],
            deprecated=True,
            replaces="h1_mancante"
        ),
        
        "missing_canonical": IssueDefinition(
            issue_type="missing_canonical",
            name_it="Canonical Mancante (Legacy)",
            description_it="DEPRECATED: Usa canonical_mancante",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.HIGH,
            format_type=IssueFormat.LEGACY,
            icon="bi-link",
            recommendations=["Migra a canonical_mancante"],
            deprecated=True,
            replaces="canonical_mancante"
        ),
        
        "missing_schema": IssueDefinition(
            issue_type="missing_schema",
            name_it="Schema Mancante (Legacy)",
            description_it="DEPRECATED: Usa schema_markup_mancante",
            category=IssueCategory.TECHNICAL_SEO,
            severity=IssueSeverity.MEDIUM,
            format_type=IssueFormat.LEGACY,
            icon="bi-code-square",
            recommendations=["Migra a schema_markup_mancante"],
            deprecated=True,
            replaces="schema_markup_mancante"
        )
    }

    @classmethod
    def get_issue(cls, issue_type: str) -> Optional[IssueDefinition]:
        """Get issue definition by type"""
        return cls.ISSUES.get(issue_type)

    @classmethod
    def get_all_issues(cls) -> Dict[str, IssueDefinition]:
        """Get all issue definitions"""
        return cls.ISSUES.copy()

    @classmethod
    def get_active_issues(cls) -> Dict[str, IssueDefinition]:
        """Get only active (non-deprecated) issues"""
        return {k: v for k, v in cls.ISSUES.items() if not v.deprecated}

    @classmethod
    def get_granular_issues(cls) -> Dict[str, IssueDefinition]:
        """Get only granular format issues (preferred)"""
        return {k: v for k, v in cls.ISSUES.items() 
                if v.format_type == IssueFormat.GRANULAR and not v.deprecated}

    @classmethod
    def get_legacy_issues(cls) -> Dict[str, IssueDefinition]:
        """Get only legacy format issues (deprecated)"""
        return {k: v for k, v in cls.ISSUES.items() 
                if v.format_type == IssueFormat.LEGACY}

    @classmethod
    def get_issues_by_category(cls, category: IssueCategory) -> Dict[str, IssueDefinition]:
        """Get issues by category"""
        return {k: v for k, v in cls.ISSUES.items() 
                if v.category == category and not v.deprecated}

    @classmethod
    def get_issues_by_severity(cls, severity: IssueSeverity) -> Dict[str, IssueDefinition]:
        """Get issues by severity"""
        return {k: v for k, v in cls.ISSUES.items() 
                if v.severity == severity and not v.deprecated}

    @classmethod
    def get_severity_score(cls, severity: IssueSeverity) -> float:
        """Get numerical score for severity"""
        severity_scores = {
            IssueSeverity.CRITICAL: -10.0,
            IssueSeverity.HIGH: -6.0,
            IssueSeverity.MEDIUM: -3.0,
            IssueSeverity.LOW: -1.0
        }
        return severity_scores.get(severity, -1.0)

    @classmethod
    def is_deprecated(cls, issue_type: str) -> bool:
        """Check if issue type is deprecated"""
        issue = cls.get_issue(issue_type)
        return issue.deprecated if issue else False

    @classmethod
    def get_replacement(cls, issue_type: str) -> Optional[str]:
        """Get replacement for deprecated issue type"""
        issue = cls.get_issue(issue_type)
        return issue.replaces if issue and issue.deprecated else None

    @classmethod
    def should_escalate(cls, issue_type: str, context: Dict[str, Any]) -> Optional[IssueSeverity]:
        """Check if issue should be escalated based on context"""
        issue = cls.get_issue(issue_type)
        if not issue or not issue.escalation_rules:
            return None
        
        rules = issue.escalation_rules
        
        # Check escalation conditions
        if "min_length" in rules and context.get("length", 0) < rules["min_length"]:
            return IssueSeverity(rules["escalate_to"])
        
        if "min_words" in rules and context.get("word_count", 0) < rules["min_words"]:
            return IssueSeverity(rules["escalate_to"])
        
        if "file_size" in rules and context.get("file_size", 0) > cls._parse_size(rules["file_size"]):
            return IssueSeverity(rules["escalate_to"])
        
        if "location" in rules and context.get("location") == rules["location"]:
            return IssueSeverity(rules["escalate_to"])
        
        return None

    @classmethod
    def _parse_size(cls, size_str: str) -> int:
        """Parse size string to bytes"""
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        return int(size_str)