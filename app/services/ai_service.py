from typing import Dict, Any, List
import json
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from pathlib import Path
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from ..config import get_settings
from ..schemas import AIExtractedData
from ..models import DocType, Correspondent
from .doctype_manager import add_document_type_if_not_exists
from .ai_client_factory import AIClientFactory

class AIService:
    def __init__(self, db_session: Session = None):
        self.settings = get_settings(db_session)
        self.client = AIClientFactory.create_client(db_session)
        self.db_session = db_session
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._last_request_time = 0
        self._min_request_interval = 0.1  # Minimum 100ms between requests
        
        # Reload settings to ensure we have the latest from database
        if db_session:
            self.settings = get_settings(db_session)
        
        # Get configured models from settings
        self.chat_model = self._get_configured_model('chat')
        self.analysis_model = self._get_configured_model('analysis')
        
        # Default document types that should always be available
        self.default_document_types = [
            "rechnung",
            "anschreiben", 
            "angebot",
            "anmeldung",
            "bescheinigung",
            "entgeltabrechnung",
            "kündigung",
            "vertrag",
            "bericht",
            "quittung",
            "mahnung",
            "gutschrift",
            "bestellung",
            "lieferschein",
            "protokoll",
            "sonstiges"
        ]
    
    def _build_completion_params(self, model: str, messages: list, max_tokens: int = 1000, temperature: float = None) -> dict:
        """Build completion parameters intelligently based on provider and model"""
        params = {
            "model": model,
            "messages": messages
        }
        
        # Determine if we should use max_completion_tokens or max_tokens
        # Azure OpenAI and o1 models use max_completion_tokens
        use_completion_tokens = False
        
        if self.settings.ai_provider.lower() == "azure":
            # Azure always uses max_completion_tokens for newer models
            use_completion_tokens = True
        elif model.startswith("o1"):
            # o1 models always use max_completion_tokens
            use_completion_tokens = True
        elif "gpt-4" in model or "gpt-3.5" in model:
            # Standard OpenAI models use max_tokens
            use_completion_tokens = False
        else:
            # For unknown models, try to be smart
            # If it's Azure, default to max_completion_tokens
            use_completion_tokens = self.settings.ai_provider.lower() == "azure"
        
        if use_completion_tokens:
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
        
        # Handle temperature
        # Azure models may not support custom temperature values
        if temperature is not None and self.settings.ai_provider.lower() != "azure":
            params["temperature"] = temperature
        
        return params
    
    def _get_configured_model(self, model_type: str) -> str:
        """Get configured model from settings or database, falling back to defaults"""
        try:
            # Try to get from database settings first
            if self.db_session:
                from ..models import Settings as SettingsModel
                setting = self.db_session.query(SettingsModel).filter(
                    SettingsModel.key == f"{model_type}_model"
                ).first()
                if setting and setting.value:
                    logger.info(f"Using configured {model_type} model: {setting.value}")
                    return setting.value
            
            # Fall back to configuration file
            if model_type == 'chat':
                model = self.settings.chat_model
            elif model_type == 'analysis':
                model = self.settings.analysis_model
            else:
                model = "gpt-4o-mini"  # Default fallback
            
            logger.info(f"Using {model_type} model from config: {model}")
            return model
            
        except Exception as e:
            logger.warning(f"Could not get configured {model_type} model: {e}")
            return "gpt-4o-mini"  # Safe fallback
    
    def _get_configured_embedding_model(self) -> str:
        """Get configured embedding model from settings or database"""
        try:
            # Try to get from database settings first
            if self.db_session:
                from ..models import Settings as SettingsModel
                setting = self.db_session.query(SettingsModel).filter(
                    SettingsModel.key == "embedding_model"
                ).first()
                if setting and setting.value:
                    logger.info(f"Using configured embedding model: {setting.value}")
                    return setting.value
            
            # Fall back to configuration file
            model = self.settings.embedding_model
            logger.info(f"Using embedding model from config: {model}")
            return model
            
        except Exception as e:
            logger.warning(f"Could not get configured embedding model: {e}")
            return "text-embedding-ada-002"  # Safe fallback
    
    def _get_available_document_types(self) -> List[str]:
        """Get all available document types from database plus defaults"""
        document_types = set(self.default_document_types)
        
        if self.db_session:
            try:
                # Load existing document types from database
                db_types = self.db_session.query(DocType).all()
                for doc_type in db_types:
                    document_types.add(doc_type.name.lower())
            except Exception as e:
                logger.warning(f"Could not load document types from database: {e}")
        
        # Always ensure "sonstiges" is included as fallback
        document_types.add("sonstiges")
        
        return sorted(list(document_types))
    
    def _make_ai_request_with_retry(self, request_func, max_retries=None):
        """Make an AI request with timeout and retry logic"""
        if max_retries is None:
            max_retries = self.settings.ai_max_retries
        
        # Rate limiting - ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                self._last_request_time = time.time()
                
                # Execute request with timeout using ThreadPoolExecutor
                future = self.executor.submit(request_func)
                
                try:
                    response = future.result(timeout=self.settings.ai_request_timeout)
                    logger.debug(f"AI request succeeded on attempt {attempt + 1}")
                    return response
                    
                except FutureTimeoutError:
                    logger.warning(f"AI request timed out after {self.settings.ai_request_timeout}s (attempt {attempt + 1})")
                    future.cancel()  # Try to cancel the request
                    last_exception = TimeoutError(f"AI request timed out after {self.settings.ai_request_timeout} seconds")
                    
                except Exception as e:
                    logger.warning(f"AI request failed on attempt {attempt + 1}: {e}")
                    last_exception = e
                
            except Exception as e:
                logger.warning(f"Failed to submit AI request on attempt {attempt + 1}: {e}")
                last_exception = e
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                wait_time = min(2 ** attempt, 8)  # Max 8 second wait
                logger.info(f"Retrying AI request in {wait_time} seconds...")
                time.sleep(wait_time)
        
        # All retries failed
        error_msg = f"AI request failed after {max_retries + 1} attempts"
        if last_exception:
            error_msg += f": {last_exception}"
        
        logger.error(error_msg)
        raise Exception(error_msg) from last_exception
    
    def _get_existing_correspondents(self) -> List[str]:
        """Get existing correspondent names for AI guidance"""
        correspondents = []
        
        if self.db_session:
            try:
                db_correspondents = self.db_session.query(Correspondent).limit(50).all()
                correspondents = [c.name for c in db_correspondents]
            except Exception as e:
                logger.warning(f"Could not load correspondents from database: {e}")
        
        return correspondents
        
    def _validate_and_fix_title(self, title: str, document_type: str, sender: str, date: str) -> str:
        """Validate and potentially fix the generated title to match naming convention"""
        import re
        
        # Expected pattern: YYYY-MM-DD_documenttype_Sender_Description_Word_Three
        expected_pattern = r'^\d{4}-\d{2}-\d{2}_[a-zA-Z]+_[a-zA-Z0-9]+_\w+_\w+.*$'
        
        if re.match(expected_pattern, title):
            return title
        
        # If title doesn't match pattern, reconstruct it
        logger.warning(f"Title '{title}' doesn't match pattern, reconstructing...")
        
        # Extract date part
        date_part = date if date else datetime.now().strftime("%Y-%m-%d")
        
        # Clean sender (remove spaces, make CamelCase)
        clean_sender = ''.join(word.capitalize() for word in re.findall(r'\w+', sender))
        
        # Extract description from original title or create generic one
        title_parts = title.split('_')
        if len(title_parts) >= 3:
            description_parts = title_parts[3:]
        else:
            description_parts = ["Dokument", "Import", "System"]
        
        # Ensure we have at least 3 description words
        while len(description_parts) < 3:
            description_parts.append("Teil")
        
        description = '_'.join(description_parts[:3])
        
        reconstructed_title = f"{date_part}_{document_type}_{clean_sender}_{description}"
        logger.info(f"Reconstructed title: {reconstructed_title}")
        
        return reconstructed_title
    
    def extract_document_metadata(self, text: str, filename: str) -> AIExtractedData:
        """Extract structured metadata from document text using OpenAI with structured outputs"""
        
        # Get dynamic document types and existing correspondents
        available_document_types = self._get_available_document_types()
        existing_correspondents = self._get_existing_correspondents()
        
        # Define the structured output schema
        schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Dokumentname nach Konvention: {YYYY-MM-DD}_{dokumenttyp}_{SenderOhneSpaces}_{DreiWortBeschreibung}. Beispiel: 2025-06-01_rechnung_MustermannGmbH_Baugenehmigung_Haus_neubau"
                },
                "document_type": {
                    "type": "string",
                    "enum": available_document_types,
                    "description": f"Art des Dokuments aus der verfügbaren Liste: {', '.join(available_document_types)}. Verwende 'sonstiges' falls nichts passt."
                },
                "date": {
                    "type": ["string", "null"],
                    "description": "Relevantes Datum im Dokument im Format YYYY-MM-DD (bevorzugt das Ausstellungsdatum)."
                },
                "sender": {
                    "type": "string",
                    "description": f"Absender oder Herausgeber des Dokuments. Firmenname oder Person ohne Leerzeichen in CamelCase. {('Bestehende Absender als Orientierung: ' + ', '.join(existing_correspondents[:10]) + '...' if existing_correspondents else 'Beispiele: MustermannGmbH, MaxMustermann, StadtBerlin')}"
                },
                "tax_relevant": {
                    "type": "boolean",
                    "description": "Ist das Dokument steuerlich relevant? (true = ja, false = nein)"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 2,
                    "maxItems": 10,
                    "description": "Relevante Stichwörter die den Inhalt beschreiben. Minimum 2, Maximum 10 Tags. Beispiele: Bau, Steuer, Vertrag, Privat, Geschäftlich"
                },
                "summary": {
                    "type": "string",
                    "description": "Eine kurze Zusammenfassung des Dokuments in einem-zwei Sätze."
                }
            },
            "required": [
                "title",
                "document_type",
                "date",
                "sender",
                "tax_relevant",
                "tags",
                "summary"
            ],
            "additionalProperties": False
        }
        
        prompt = f"""
        Analysiere den folgenden Dokumenttext und extrahiere die Metadaten gemäß dem Schema.
        
        WICHTIGE NAMING-KONVENTION für den Titel:
        Format: {{YYYY-MM-DD}}_{{dokumenttyp}}_{{SenderOhneSpaces}}_{{DreiWortBeschreibung}}
        
        Beispiele guter Titel:
        - 2025-01-15_rechnung_MustermannGmbH_Stromrechnung_Januar_2025
        - 2024-12-01_vertrag_StadtBerlin_Mietvertrag_Wohnung_Zentrum
        - 2025-02-10_angebot_AutohausMeier_Werkstatt_Service_Inspektion
        
        Regeln:
        - Datum im Format YYYY-MM-DD (bevorzugt Ausstellungsdatum)
        - Dokumenttyp aus der verfügbaren Liste wählen: {', '.join(available_document_types)}
        - Sender ohne Leerzeichen in CamelCase (z.B. MaxMustermann, BerlinStadt, ABCGmbH)
        {f'- Bestehende Absender als Orientierung: {", ".join(existing_correspondents[:100])}{"..." if len(existing_correspondents) > 10 else ""}' if existing_correspondents else ''}
        - 3-Wort-Beschreibung die den Inhalt präzise beschreibt
        - Alle Teile mit Unterstrichen verbinden
        - Deutsche Begriffe verwenden
        
        Originaler Dateiname: {filename}
        
        Dokumenttext:
        {text[:self.settings.ai_text_limit]}
        """
        
        try:
            model_to_use = self.analysis_model
            
            if model_to_use.startswith("o1"):
                model_to_use = "gpt-4o-mini"
                
            # For Azure, use deployment name instead of model name
            if self.settings.ai_provider.lower() == "azure":
                model_param = AIClientFactory.get_chat_model(self.settings)
            else:
                model_param = model_to_use
            
            # Check if we can use JSON schema format
            use_json_schema = True
            if self.settings.ai_provider.lower() == "azure":
                # Only use JSON schema for Azure with API version 2024-08-01-preview or later
                api_version = getattr(self.settings, 'azure_openai_api_version', '2024-06-01')
                if api_version < '2024-08-01':
                    use_json_schema = False
            
            # Build the request parameters using intelligent helper
            messages = [
                {
                    "role": "system", 
                    "content": "Du bist ein präziser Dokumenten-Metadaten-Extraktor. Du analysierst deutsche Dokumente und extrahierst strukturierte Metadaten nach dem vorgegebenen Schema. Folge immer genau der Namenskonvention für Titel."
                },
                {"role": "user", "content": prompt}
            ]
            
            request_params = self._build_completion_params(
                model=model_param,
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            # Add response format if supported
            if use_json_schema:
                request_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "document_metadata",
                        "strict": True,
                        "schema": schema
                    }
                }
            
            response = self._make_ai_request_with_retry(
                lambda: self.client.chat.completions.create(**request_params)
            )
            
            response_text = response.choices[0].message.content
            
            # Parse the structured JSON response
            try:
                metadata = json.loads(response_text)
                
                # Validate and fix the title if necessary
                validated_title = self._validate_and_fix_title(
                    metadata.get("title", ""),
                    metadata.get("document_type", "sonstiges"),
                    metadata.get("sender", "UnknownSender"),
                    metadata.get("date")
                )
                
                # Ensure the document type exists in database
                doctype_name = metadata.get("document_type", "sonstiges")
                if self.db_session and doctype_name not in self.default_document_types:
                    try:
                        add_document_type_if_not_exists(
                            self.db_session, 
                            doctype_name,
                            f"Automatically added document type: {doctype_name}"
                        )
                    except Exception as e:
                        logger.warning(f"Could not add new document type {doctype_name}: {e}")
                
                # Convert to our internal AIExtractedData format
                return AIExtractedData(
                    title=validated_title,
                    summary=metadata.get("summary"),
                    document_date=metadata.get("date"),
                    correspondent_name=metadata.get("sender"),
                    doctype_name=doctype_name,
                    tag_names=metadata.get("tags", []),
                    is_tax_relevant=metadata.get("tax_relevant", False)
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from OpenAI: {response_text}, error: {e}")
                raise ValueError("AI returned invalid JSON")
                
        except Exception as e:
            logger.error(f"Failed to extract metadata using AI: {e}")
            raise
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using OpenAI"""
        try:
            # Get configured embedding model based on provider
            if self.settings.ai_provider.lower() == "azure":
                embedding_model = AIClientFactory.get_embeddings_model(self.settings)
            else:
                embedding_model = self._get_configured_embedding_model()
            
            response = self._make_ai_request_with_retry(
                lambda: self.client.embeddings.create(
                    model=embedding_model,
                    input=text[:8000]  # Limit text length for embeddings
                )
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def answer_question(self, question: str, context_documents: List[str], document_titles: List[str] = None, document_ids: List[str] = None) -> str:
        """Answer a question based on document context using RAG"""
        
        # Prepare context from documents with document references
        context_parts = []
        document_references = []
        
        for i, doc in enumerate(context_documents):
            doc_num = i + 1
            title = document_titles[i] if document_titles and i < len(document_titles) else f"Document {doc_num}"
            doc_id = document_ids[i] if document_ids and i < len(document_ids) else None
            
            # Create document reference for AI to use
            if doc_id:
                doc_ref = f"[Doc{doc_num}: {title}]"
                document_references.append(f"Doc{doc_num} ({title}) - ID: {doc_id}")
            else:
                doc_ref = f"[Doc{doc_num}: {title}]"
                document_references.append(f"Doc{doc_num} ({title})")
            
            context_parts.append(f"{doc_ref}:\n{doc}")
        
        context = "\n\n".join(context_parts)
        references_list = "\n".join(document_references)
        
        prompt = f"""
        You are a helpful assistant that answers questions based on the provided document context.
        
        IMPORTANT INSTRUCTIONS:
        - Always use Markdown formatting in your response
        - ALWAYS cite your sources using the exact document references provided below
        - When referencing a document, use the format: [Doc1], [Doc2], etc.
        - Include relevant quotes with citation: "quoted text" ([Doc1])
        - Structure your answer with headers (##), bullet points, and formatting as appropriate
        - If information is not available in the documents, clearly state this
        
        AVAILABLE DOCUMENT REFERENCES:
        {references_list}
        
        CONTEXT DOCUMENTS:
        {context[:self.settings.ai_context_limit]}
        
        QUESTION: {question}
        
        Please provide a comprehensive answer in Markdown format with proper source citations.
        """
        
        # Log the prompt to file
        self._log_rag_prompt(question, prompt, document_titles, document_ids)
        
        try:
            # Handle different model capabilities
            model_to_use = self.chat_model
            
            # o1 models don't support system messages, so we need to format differently
            if model_to_use.startswith("o1"):
                # For o1 models, include instructions in the user message
                enhanced_prompt = f"""You are a knowledgeable assistant that answers questions based only on the provided document context. Provide comprehensive and accurate answers.

{prompt}"""
                messages = [{"role": "user", "content": enhanced_prompt}]
            else:
                # For other models, use system message
                messages = [
                    {"role": "system", "content": "You are a knowledgeable assistant that answers questions based only on the provided document context. Provide comprehensive and accurate answers."},
                    {"role": "user", "content": prompt}
                ]
            
            # Handle different model parameter requirements
            # For Azure, use deployment name instead of model name
            if self.settings.ai_provider.lower() == "azure":
                model_param = AIClientFactory.get_chat_model(self.settings)
            else:
                model_param = model_to_use
                
            # Use intelligent parameter building
            completion_params = self._build_completion_params(
                model=model_param,
                messages=messages,
                max_tokens=5000,
                temperature=0.3
            )
            
            response = self._make_ai_request_with_retry(
                lambda: self.client.chat.completions.create(**completion_params)
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated RAG answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate RAG answer: {e}")
            raise
    
    def suggest_improvements(self, extracted_data: AIExtractedData, text: str) -> Dict[str, Any]:
        """Suggest improvements or alternatives for extracted metadata"""
        
        prompt = f"""
        Review the following extracted metadata and suggest improvements or alternatives:
        
        Extracted data:
        - Title: {extracted_data.title}
        - Summary: {extracted_data.summary}
        - Date: {extracted_data.document_date}
        - Correspondent: {extracted_data.correspondent_name}
        - Document type: {extracted_data.doctype_name}
        - Tags: {', '.join(extracted_data.tag_names)}
        - Tax relevant: {extracted_data.is_tax_relevant}
        
        Document text (first 1000 chars): {text[:1000]}
        
        Please suggest:
        1. Alternative titles (2-3 options)
        2. Additional relevant tags
        3. Confidence score (0-1) for each extracted field
        4. Any corrections or improvements
        
        Return as JSON with structure:
        {{
            "alternative_titles": ["title1", "title2"],
            "additional_tags": ["tag1", "tag2"],
            "confidence_scores": {{
                "title": 0.9,
                "summary": 0.8,
                "date": 0.7,
                "correspondent": 0.9,
                "doctype": 0.95,
                "is_tax_relevant": 0.85
            }},
            "suggestions": ["suggestion1", "suggestion2"]
        }}
        """
        
        try:
            # Handle different model parameter requirements
            # For Azure, use deployment name instead of model name
            if self.settings.ai_provider.lower() == "azure":
                model_param = AIClientFactory.get_chat_model(self.settings)
            else:
                model_param = "gpt-3.5-turbo"
                
            # Use intelligent parameter building
            messages = [
                {"role": "system", "content": "You are a metadata quality expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            completion_params = self._build_completion_params(
                model=model_param,
                messages=messages,
                max_tokens=500,
                temperature=0.1
            )
            
            response = self._make_ai_request_with_retry(
                lambda: self.client.chat.completions.create(**completion_params)
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean and parse JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            suggestions = json.loads(response_text)
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate suggestions: {e}")
            return {
                "alternative_titles": [],
                "additional_tags": [],
                "confidence_scores": {},
                "suggestions": []
            }
    
    def _log_rag_prompt(self, question: str, prompt: str, document_titles: List[str] = None, document_ids: List[str] = None):
        """Log RAG prompts to file, keeping only the last 5"""
        try:
            # Create logs directory if it doesn't exist
            log_dir = Path(self.settings.logs_folder)
            log_dir.mkdir(exist_ok=True)
            
            # Define log file path
            log_file = log_dir / "rag_prompts.json"
            
            # Load existing prompts or create empty list
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    try:
                        prompts = json.load(f)
                    except json.JSONDecodeError:
                        prompts = []
            else:
                prompts = []
            
            # Create new log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "prompt": prompt,
                "document_titles": document_titles or [],
                "document_ids": document_ids or [],
                "prompt_length": len(prompt)
            }
            
            # Add new entry and keep only last 5
            prompts.append(log_entry)
            if len(prompts) > 5:
                prompts = prompts[-5:]
            
            # Write back to file
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2, ensure_ascii=False)
            
            logger.info(f"RAG prompt logged to {log_file} (Question: {question[:50]}...)")
            
        except Exception as e:
            logger.error(f"Failed to log RAG prompt: {e}")
            # Don't fail the main operation if logging fails
