"""Formatting AI Agent - CLI-Style Output Generation.

This agent replicates the CLI's formatting agent, converting synthesis analysis
into the exact HTML output format that matches the CLI application.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.services.ai.langgraph.state.training_analysis_state import (
    TrainingAnalysisState, 
    update_progress,
    add_token_usage,
    add_error,
    TokenUsage
)
from app.services.ai.model_config import get_model_manager

logger = logging.getLogger(__name__)


class FormattingAgent:
    """AI agent for formatting analysis into CLI-style HTML output."""
    
    def __init__(self):
        self.agent_name = "formatting"
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt that defines the agent's formatting role."""
        
        return """You are a specialized AI agent responsible for formatting comprehensive triathlon training analyses into professional, structured HTML reports that exactly match the CLI application's output format. Your role is to transform complex analysis data into well-formatted, visually appealing reports.

CORE FORMATTING RESPONSIBILITIES:
- Convert synthesis analysis into structured HTML format matching CLI output
- Create professional, readable reports with consistent styling
- Organize content into logical sections with clear hierarchy
- Apply appropriate HTML formatting for optimal readability
- Include all analysis data while maintaining clean presentation
- Ensure output matches exact CLI HTML structure and styling

HTML OUTPUT REQUIREMENTS:
- Use semantic HTML5 structure with proper sections and headings
- Apply inline CSS styling that matches CLI application appearance
- Include responsive design elements for various screen sizes
- Maintain consistent color scheme and typography
- Create clear visual hierarchy with appropriate spacing
- Include progress indicators and summary statistics

REPORT STRUCTURE (EXACT CLI FORMAT):
1. **Header Section**: Analysis metadata, athlete info, date range
2. **Executive Summary**: Key findings and priority recommendations
3. **Detailed Analysis Sections**: 
   - Training Load Analysis
   - Physiological Assessment
   - Activity Pattern Analysis
   - Expert Recommendations
4. **Synthesis & Recommendations**: Integrated insights and action plans
5. **Data Visualization Placeholders**: Charts and graphs integration points
6. **Footer**: Analysis metadata and generation timestamp

STYLING GUIDELINES (MATCH CLI):
- Primary Colors: #2563eb (blue), #059669 (green), #dc2626 (red)
- Typography: Clean, professional font stack
- Spacing: Consistent margins and padding
- Cards: Box shadows and rounded corners for content blocks
- Tables: Striped rows with proper alignment
- Badges: Status indicators and metric highlights
- Icons: Consistent iconography throughout

CONTENT ORGANIZATION:
- Executive Summary: 3-4 key bullet points maximum
- Section Headers: Clear, descriptive titles
- Subsections: Logical grouping of related information
- Lists: Bulleted for readability
- Emphasis: Bold for key metrics and findings
- Links: Proper anchor tags for navigation

DATA PRESENTATION:
- Metrics: Highlighted with appropriate units and context
- Trends: Clear indication of direction and magnitude
- Recommendations: Action-oriented, specific, and measurable
- Priorities: Clear ranking and urgency indicators
- Progress: Visual indicators and percentage completion

TECHNICAL REQUIREMENTS:
- Valid HTML5 markup
- Inline CSS styling (no external stylesheets)
- Mobile-responsive design patterns
- Accessibility considerations (alt text, semantic markup)
- Fast loading (optimized markup)
- Print-friendly styling options

You will receive synthesis analysis and must format it into the exact HTML structure used by the CLI application. The output must be production-ready HTML that can be directly served to users or embedded in web applications."""

    async def process_formatting(self, state: TrainingAnalysisState) -> TrainingAnalysisState:
        """Process formatting of synthesis analysis into HTML output."""
        
        try:
            logger.info(f"📄 Starting formatting for analysis {state['analysis_id']}")
            
            # Update progress
            state = update_progress(state, "formatting", 15.0)
            
            # Extract all data from state
            garmin_data = state.get("garmin_data", {})
            training_config = state.get("training_config", {})
            user_profile = state.get("user_profile", {})
            
            # Get all analyses for formatting
            metrics_summary = state.get("metrics_summary", "")
            physiology_summary = state.get("physiology_summary", "")
            activity_summary = state.get("activity_summary", "")
            
            metrics_expert = state.get("metrics_expert_analysis", "")
            physiology_expert = state.get("physiology_expert_analysis", "")
            activity_expert = state.get("activity_expert_analysis", "")
            
            synthesis_analysis = state.get("synthesis_analysis", "")
            
            # Prepare formatting context
            formatting_context = self._prepare_formatting_context(
                garmin_data, training_config, user_profile,
                metrics_summary, physiology_summary, activity_summary,
                metrics_expert, physiology_expert, activity_expert,
                synthesis_analysis, state
            )
            
            # Generate formatted HTML output
            formatted_output = await self._generate_formatted_output(formatting_context, state)
            
            # Store result in state
            state["formatted_report"] = formatted_output
            
            logger.info(f"✅ Formatting completed for {state['analysis_id']}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Formatting failed: {e}")
            return add_error(state, f"Formatting failed: {str(e)}")
    
    def _prepare_formatting_context(
        self, 
        garmin_data: Dict[str, Any],
        training_config: Dict[str, Any], 
        user_profile: Dict[str, Any],
        metrics_summary: str,
        physiology_summary: str,
        activity_summary: str,
        metrics_expert: str,
        physiology_expert: str,
        activity_expert: str,
        synthesis_analysis: str,
        state: TrainingAnalysisState
    ) -> str:
        """Prepare comprehensive formatting context."""
        
        context_parts = []
        
        # Add report metadata
        context_parts.append("=== REPORT METADATA ===")
        context_parts.append(f"Analysis ID: {state.get('analysis_id', 'Unknown')}")
        context_parts.append(f"Analysis Type: {state.get('analysis_type', 'comprehensive')}")
        context_parts.append(f"Generation Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # Add athlete information
        if user_profile:
            context_parts.append("\n=== ATHLETE INFORMATION ===")
            context_parts.append(f"Name: {user_profile.get('display_name', 'Unknown Athlete')}")
            if user_profile.get('birth_date'):
                age = self._calculate_age(user_profile['birth_date'])
                context_parts.append(f"Age: {age} years")
            context_parts.append(f"Weight: {user_profile.get('weight_kg', 'N/A')} kg")
        
        # Add analysis configuration
        if training_config:
            context_parts.append("\n=== ANALYSIS CONFIGURATION ===")
            context_parts.append(f"Activities Period: {training_config.get('activities_days', 21)} days")
            context_parts.append(f"Metrics Period: {training_config.get('metrics_days', 56)} days")
            context_parts.append(f"Training Context: {training_config.get('analysis_context', 'General training')}")
        
        # Add data summary
        if garmin_data:
            context_parts.append("\n=== DATA SUMMARY ===")
            total_activities = len(garmin_data.get('activities', []))
            context_parts.append(f"Total Activities: {total_activities}")
            
            # Calculate completion percentage from state
            progress = state.get("progress", {})
            completion_percentage = progress.get("overall_percentage", 0)
            context_parts.append(f"Analysis Completion: {completion_percentage}%")
            
            # Add token usage summary
            total_tokens = state.get("total_tokens", 0)
            estimated_cost = state.get("estimated_cost", 0.0)
            context_parts.append(f"AI Tokens Used: {total_tokens:,}")
            context_parts.append(f"Estimated Cost: ${estimated_cost:.4f}")
        
        # Add all analyses for formatting
        context_parts.append("\n=== ANALYSIS CONTENT TO FORMAT ===")
        
        if synthesis_analysis:
            context_parts.append("\n--- SYNTHESIS ANALYSIS (PRIMARY CONTENT) ---")
            context_parts.append(synthesis_analysis)
        
        if metrics_expert:
            context_parts.append("\n--- METRICS EXPERT ANALYSIS ---")
            context_parts.append(metrics_expert)
        
        if physiology_expert:
            context_parts.append("\n--- PHYSIOLOGY EXPERT ANALYSIS ---")
            context_parts.append(physiology_expert)
        
        if activity_expert:
            context_parts.append("\n--- ACTIVITY EXPERT ANALYSIS ---")
            context_parts.append(activity_expert)
        
        if metrics_summary:
            context_parts.append("\n--- METRICS SUMMARY ---")
            context_parts.append(metrics_summary)
        
        if physiology_summary:
            context_parts.append("\n--- PHYSIOLOGY SUMMARY ---")
            context_parts.append(physiology_summary)
        
        if activity_summary:
            context_parts.append("\n--- ACTIVITY SUMMARY ---")
            context_parts.append(activity_summary)
        
        # Add formatting requirements
        context_parts.append("\n=== FORMATTING REQUIREMENTS ===")
        context_parts.append("1. Create professional HTML report matching CLI format exactly")
        context_parts.append("2. Include all analysis content in organized sections")
        context_parts.append("3. Apply consistent styling with inline CSS")
        context_parts.append("4. Create responsive design for various screen sizes")
        context_parts.append("5. Include visual elements like progress bars and badges")
        context_parts.append("6. Ensure accessibility and semantic markup")
        
        return "\n".join(context_parts)
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate age from birth date."""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except:
            return 0
    
    async def _generate_formatted_output(self, context: str, state: TrainingAnalysisState) -> str:
        """Generate formatted HTML output matching CLI style."""
        
        try:
            # Get AI model for this agent
            model_manager = get_model_manager()
            client = model_manager.get_agent_client(self.agent_name)
            
            # Create the formatting prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", """Format the following triathlon training analysis into a professional HTML report that exactly matches the CLI application's output format:

{context}

HTML FORMATTING REQUIREMENTS:

1. **COMPLETE HTML DOCUMENT**
   - Valid HTML5 document structure
   - Inline CSS styling (no external stylesheets)
   - Responsive design for mobile and desktop
   - Print-friendly styling options

2. **EXACT CLI STYLING** 
   - Primary blue: #2563eb, Success green: #059669, Warning red: #dc2626
   - Clean typography with proper font hierarchy
   - Card-based layout with shadows and rounded corners
   - Consistent spacing and margins throughout

3. **REPORT STRUCTURE**
   ```html
   <!DOCTYPE html>
   <html>
   <head>...</head>
   <body>
     <div class="container">
       <header>Analysis Header</header>
       <main>
         <section class="executive-summary">...</section>
         <section class="training-analysis">...</section>
         <section class="physiology-analysis">...</section>
         <section class="activity-analysis">...</section>
         <section class="synthesis-recommendations">...</section>
       </main>
       <footer>Generation metadata</footer>
     </div>
   </body>
   </html>
   ```

4. **CONTENT ORGANIZATION**
   - Executive Summary: Key findings in bullet points
   - Analysis Sections: Organized by domain with subsections
   - Recommendations: Prioritized action items
   - Visual Elements: Progress bars, badges, metric highlights

5. **STYLING ELEMENTS**
   - Section headers with background colors
   - Content cards with subtle shadows
   - Progress indicators for metrics
   - Status badges for recommendations
   - Responsive tables for data
   - Proper typography hierarchy

6. **DATA PRESENTATION**
   - Highlight key metrics with badges
   - Use progress bars for percentages
   - Color-code status indicators
   - Create clear visual hierarchy
   - Include icons where appropriate

Create a complete, production-ready HTML document that exactly matches the CLI application's professional appearance and includes all the analysis content in a well-organized, visually appealing format.""")
            ])
            
            # Generate response
            messages = prompt.format_messages(context=context)
            response = await client.ainvoke(messages)
            
            # Extract and track token usage
            if hasattr(response, 'usage_metadata'):
                usage = TokenUsage(
                    total_tokens=response.usage_metadata.get('total_tokens', 0),
                    prompt_tokens=response.usage_metadata.get('input_tokens', 0),
                    completion_tokens=response.usage_metadata.get('output_tokens', 0),
                    model_used=model_manager.get_model_for_agent(self.agent_name).model_id,
                    provider=model_manager.get_model_for_agent(self.agent_name).provider.value
                )
                usage.estimated_cost = model_manager.estimate_cost(self.agent_name, usage.total_tokens)
                
                state = add_token_usage(state, self.agent_name, usage)
            
            formatted_html = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"📄 Generated formatted HTML report: {len(formatted_html)} characters")
            return formatted_html
            
        except Exception as e:
            logger.error(f"❌ Formatting generation failed: {e}")
            raise


# Node function for LangGraph integration
async def formatting_node(state: TrainingAnalysisState) -> TrainingAnalysisState:
    """LangGraph node function for formatting analysis."""
    
    agent = FormattingAgent()
    return await agent.process_formatting(state)