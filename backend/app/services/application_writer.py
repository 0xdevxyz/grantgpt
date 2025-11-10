"""
Application Writer Service - AI-powered grant application generation
"""
from typing import Dict, Any, List
from app.core.config import settings
from app.services.openrouter_client import openrouter_client


class ApplicationWriter:
    """Service for generating grant application content using OpenRouter"""
    
    def __init__(self):
        self.client = openrouter_client
        self.temperature = 0.7
        self.max_tokens = 4000
    
    async def generate_project_description(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str,
        rag_examples: List[str] = None
    ) -> str:
        """
        Generate project description section (3-5 pages)
        
        Args:
            project_info: Project details from user
            grant_guidelines: Specific grant guidelines
            rag_examples: Similar successful applications
            
        Returns:
            Generated project description text
        """
        system_prompt = self._build_system_prompt("project_description")
        user_prompt = self._build_project_description_prompt(
            project_info,
            grant_guidelines,
            rag_examples
        )
        
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_market_analysis(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str
    ) -> str:
        """Generate market analysis section (2-3 pages)"""
        system_prompt = self._build_system_prompt("market_analysis")
        user_prompt = f"""
Erstelle eine Marktanalyse für folgendes Projekt:

Projekt: {project_info.get('title', 'Unbekannt')}
Beschreibung: {project_info.get('description', '')}
Zielgruppe: {project_info.get('target_audience', '')}
Markt: {project_info.get('market_analysis', '')}

Struktur:
1. TAM/SAM/SOM-Analyse (Total/Serviceable/Obtainable Market)
2. Wettbewerber-Analyse
3. Marktpotenzial und Trends
4. Marktposition nach Projekt

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_technical_feasibility(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str
    ) -> str:
        """Generate technical feasibility section (3-4 pages)"""
        system_prompt = self._build_system_prompt("technical_feasibility")
        user_prompt = f"""
Erstelle eine technische Machbarkeitsanalyse:

Projekt: {project_info.get('title', '')}
Technologie: {project_info.get('technology', '')}
Innovation: {project_info.get('innovation', '')}

Struktur:
1. Technologie-Stack und Architektur
2. Entwicklungs-Roadmap
3. Technische Risiken und Mitigation
4. Innovationsgrad (wichtig!)

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_work_plan(
        self,
        project_info: Dict[str, Any],
        timeline_months: int,
        grant_guidelines: str
    ) -> str:
        """Generate work plan section (2-3 pages)"""
        system_prompt = self._build_system_prompt("work_plan")
        user_prompt = f"""
Erstelle einen detaillierten Arbeitsplan:

Projekt: {project_info.get('title', '')}
Dauer: {timeline_months} Monate
Beschreibung: {project_info.get('description', '')}

Struktur:
1. Meilensteine (M1-M{min(timeline_months // 3, 6)})
2. Aufgaben pro Meilenstein
3. Ressourcenplanung
4. Gantt-Chart (textbasiert)

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_financial_plan(
        self,
        budget_info: Dict[str, Any],
        grant_guidelines: str
    ) -> str:
        """Generate financial plan section (2 pages)"""
        system_prompt = self._build_system_prompt("financial_plan")
        user_prompt = f"""
Erstelle einen Finanzplan:

Gesamtbudget: {budget_info.get('total_budget', 0):,.2f} €
Fördersumme: {budget_info.get('requested_funding', 0):,.2f} €
Eigenanteil: {budget_info.get('own_contribution', 0):,.2f} €
Budget-Breakdown: {budget_info.get('breakdown', {})}

Struktur:
1. Kostenplan (detailliert)
2. Finanzierungsplan
3. Break-Even-Analyse
4. Liquiditäts-Planung

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_risk_management(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str
    ) -> str:
        """Generate risk management section (1-2 pages)"""
        system_prompt = self._build_system_prompt("risk_management")
        user_prompt = f"""
Erstelle ein Risikomanagement:

Projekt: {project_info.get('title', '')}
Technologie: {project_info.get('technology', '')}
Markt: {project_info.get('market_analysis', '')}

Struktur:
1. Technische Risiken und Mitigation
2. Marktrisiken und Mitigation
3. Finanzielle Risiken und Mitigation
4. Ressourcen-Risiken und Mitigation

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    async def generate_utilization_plan(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str
    ) -> str:
        """Generate utilization plan section (2-3 pages)"""
        system_prompt = self._build_system_prompt("utilization_plan")
        user_prompt = f"""
Erstelle einen Verwertungsplan:

Projekt: {project_info.get('title', '')}
Beschreibung: {project_info.get('description', '')}
Business-Model: {project_info.get('business_model', '')}
Zielgruppe: {project_info.get('target_audience', '')}

Struktur:
1. Go-to-Market-Strategie
2. Pricing und Erlösmodell
3. Skalierungs-Plan
4. Langfristige Vision

Richtlinien: {grant_guidelines}
"""
        return await self._generate_content(system_prompt, user_prompt)
    
    def _build_system_prompt(self, section_type: str) -> str:
        """Build system prompt for specific section"""
        base = """Du bist ein erfahrener Fördermittel-Berater mit 20 Jahren Erfahrung.
Deine Aufgabe: Schreibe überzeugende, professionelle Antragsabschnitte.

Wichtig:
- Wissenschaftlich und sachlich (keine Marketing-Sprache!)
- Konkrete Zahlen und Fakten
- Betone Innovation und technisches Risiko
- Referenziere relevante Studien/Technologien
- Deutsche Sprache, professionell
"""
        
        section_specific = {
            "project_description": "Fokus: Problemstellung, Innovation, Alleinstellungsmerkmal",
            "market_analysis": "Fokus: TAM/SAM/SOM, Wettbewerb, Marktpotenzial",
            "technical_feasibility": "Fokus: Technologie, Architektur, Risiken",
            "work_plan": "Fokus: Meilensteine, Aufgaben, Timeline",
            "financial_plan": "Fokus: Kosten, Finanzierung, Break-Even",
            "risk_management": "Fokus: Risiken identifizieren und mitigieren",
            "utilization_plan": "Fokus: Verwertung, Go-to-Market, Skalierung"
        }
        
        return base + "\n" + section_specific.get(section_type, "")
    
    def _build_project_description_prompt(
        self,
        project_info: Dict[str, Any],
        grant_guidelines: str,
        rag_examples: List[str] = None
    ) -> str:
        """Build detailed prompt for project description"""
        prompt = f"""
Schreibe die Projektbeschreibung für folgendes Projekt:

Titel: {project_info.get('title', 'Unbekannt')}
Beschreibung: {project_info.get('description', '')}
Innovation: {project_info.get('innovation', '')}
Technologie: {project_info.get('technology', '')}
Ziele: {', '.join(project_info.get('goals', []))}

Struktur:
1. Ausgangssituation & Problemstellung (1 Seite)
2. Projektziel & angestrebte Lösung (1,5 Seiten)
3. Innovation & Alleinstellungsmerkmal (1,5 Seiten)
4. Nutzen für Zielgruppe & Marktpotenzial (1 Seite)

Richtlinien: {grant_guidelines}
"""
        
        if rag_examples:
            prompt += "\n\nReferenz (erfolgreiche Anträge):\n"
            prompt += "\n---\n".join(rag_examples[:2])  # Max 2 examples
        
        return prompt
    
    async def _generate_content(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        """
        Call OpenRouter API to generate content
        
        Args:
            system_prompt: System instructions
            user_prompt: User request
            
        Returns:
            Generated text content
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            return await self.client.chat_completion(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            raise


# Singleton instance
application_writer = ApplicationWriter()

