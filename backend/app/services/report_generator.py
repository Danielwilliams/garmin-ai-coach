"""Report generation service for creating HTML reports from analysis data."""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import markdown
from pathlib import Path

class ReportGenerator:
    """Service for generating HTML reports from analysis data."""
    
    def __init__(self):
        # Set up Jinja2 environment for templating
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Set up output directories
        self.base_output_dir = Path(os.getenv("REPORTS_OUTPUT_DIR", "./storage/reports"))
        self.plots_dir = Path(os.getenv("PLOTS_OUTPUT_DIR", "./storage/plots"))
        self.exports_dir = Path(os.getenv("EXPORTS_OUTPUT_DIR", "./storage/exports"))
        
        # Create directories
        for dir_path in [self.base_output_dir, self.plots_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_analysis_report(
        self, 
        analysis_data: Dict[str, Any], 
        results_data: list, 
        user_name: str = "Athlete"
    ) -> Dict[str, str]:
        """Generate a comprehensive HTML analysis report."""
        
        # Prepare template data
        template_data = {
            "analysis": analysis_data,
            "results": results_data,
            "user_name": user_name,
            "generated_at": datetime.utcnow(),
            "report_title": f"{analysis_data.get('analysis_type', 'Training')} Analysis Report",
            "training_config_name": analysis_data.get('training_config_name', 'Training Profile')
        }
        
        # Process content with markdown
        template_data = self._process_markdown_content(template_data)
        
        # Generate HTML report
        try:
            template = self.jinja_env.get_template("analysis_report.html")
        except:
            # Fall back to embedded template if file doesn't exist
            template = self.jinja_env.from_string(self._get_default_template())
        
        html_content = template.render(**template_data)
        
        # Generate unique filename
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_report_{timestamp}_{report_id}.html"
        
        # Save report
        report_path = self.base_output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            "filename": filename,
            "file_path": str(report_path),
            "file_size": len(html_content.encode('utf-8')),
            "mime_type": "text/html"
        }
    
    def generate_weekly_plan_export(
        self, 
        weekly_plan_data: Dict[str, Any], 
        analysis_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a weekly training plan export."""
        
        # Generate CSV format
        csv_content = self._weekly_plan_to_csv(weekly_plan_data)
        
        # Generate filename
        plan_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        filename = f"weekly_plan_{timestamp}_{plan_id}.csv"
        
        # Save CSV
        export_path = self.exports_dir / filename
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        return {
            "filename": filename,
            "file_path": str(export_path),
            "file_size": len(csv_content.encode('utf-8')),
            "mime_type": "text/csv"
        }
    
    def generate_data_export(
        self, 
        analysis_data: Dict[str, Any], 
        results_data: list,
        export_format: str = "json"
    ) -> Dict[str, str]:
        """Generate data export in JSON or CSV format."""
        
        export_data = {
            "analysis_metadata": {
                "id": analysis_data.get("id"),
                "analysis_type": analysis_data.get("analysis_type"),
                "status": analysis_data.get("status"),
                "created_at": analysis_data.get("created_at"),
                "total_tokens": analysis_data.get("total_tokens"),
                "estimated_cost": analysis_data.get("estimated_cost")
            },
            "summary": analysis_data.get("summary"),
            "recommendations": analysis_data.get("recommendations"),
            "weekly_plan": analysis_data.get("weekly_plan"),
            "data_summary": analysis_data.get("data_summary"),
            "results": [
                {
                    "node_name": result.get("node_name"),
                    "result_type": result.get("result_type"),
                    "title": result.get("title"),
                    "content": result.get("content"),
                    "data": result.get("data"),
                    "tokens_used": result.get("tokens_used")
                }
                for result in results_data
            ]
        }
        
        # Generate filename
        export_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_data_{timestamp}_{export_id}.{export_format}"
        
        # Save file
        export_path = self.exports_dir / filename
        
        if export_format == "json":
            content = json.dumps(export_data, indent=2, default=str)
            mime_type = "application/json"
        else:
            # CSV format (simplified)
            content = self._analysis_to_csv(export_data)
            mime_type = "text/csv"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "filename": filename,
            "file_path": str(export_path),
            "file_size": len(content.encode('utf-8')),
            "mime_type": mime_type
        }
    
    def _process_markdown_content(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert markdown content to HTML."""
        
        # Process analysis summary
        if template_data["analysis"].get("summary"):
            template_data["analysis"]["summary_html"] = markdown.markdown(
                template_data["analysis"]["summary"],
                extensions=['extra', 'codehilite']
            )
        
        # Process recommendations
        if template_data["analysis"].get("recommendations"):
            template_data["analysis"]["recommendations_html"] = markdown.markdown(
                template_data["analysis"]["recommendations"],
                extensions=['extra', 'codehilite']
            )
        
        # Process result content
        for result in template_data["results"]:
            if result.get("content"):
                result["content_html"] = markdown.markdown(
                    result["content"],
                    extensions=['extra', 'codehilite']
                )
        
        return template_data
    
    def _weekly_plan_to_csv(self, weekly_plan: Dict[str, Any]) -> str:
        """Convert weekly plan to CSV format."""
        
        csv_lines = ["Day,Type,Duration,Intensity,Description"]
        
        if "week_structure" in weekly_plan:
            for day, details in weekly_plan["week_structure"].items():
                csv_lines.append(
                    f"{day.capitalize()},"
                    f"{details.get('type', '')},"
                    f"{details.get('duration', '')},"
                    f"{details.get('intensity', '')},"
                    f"{details.get('description', '')}"
                )
        
        return "\n".join(csv_lines)
    
    def _analysis_to_csv(self, export_data: Dict[str, Any]) -> str:
        """Convert analysis data to CSV format (simplified)."""
        
        csv_lines = ["Category,Type,Title,Content"]
        
        # Add metadata
        metadata = export_data["analysis_metadata"]
        csv_lines.append(f"Metadata,Analysis Type,{metadata.get('analysis_type', '')},{metadata.get('status', '')}")
        csv_lines.append(f"Metadata,Tokens,{metadata.get('total_tokens', '')},'Cost: {metadata.get('estimated_cost', '')}'")
        
        # Add results
        for result in export_data["results"]:
            content = result.get("content", "").replace('"', '""')  # Escape quotes
            csv_lines.append(f"Result,{result.get('result_type', '')},{result.get('title', '')},\"{content}\"")
        
        return "\n".join(csv_lines)
    
    def _get_default_template(self) -> str:
        """Return a default HTML template if no template file exists."""
        
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report_title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8fafc;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .section h2 {
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metadata-item {
            background: #f7fafc;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .metadata-label {
            font-weight: 600;
            color: #4a5568;
            font-size: 0.9em;
        }
        .metadata-value {
            font-size: 1.1em;
            margin-top: 5px;
        }
        .content {
            line-height: 1.8;
        }
        .content h3 {
            color: #2d3748;
            margin-top: 25px;
        }
        .content ul, .content ol {
            margin-left: 20px;
        }
        .content li {
            margin-bottom: 8px;
        }
        .result-item {
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .result-header {
            background: #f7fafc;
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
        }
        .result-title {
            font-weight: 600;
            color: #2d3748;
        }
        .result-meta {
            font-size: 0.9em;
            color: #718096;
            margin-top: 5px;
        }
        .result-content {
            padding: 20px;
        }
        .weekly-plan {
            display: grid;
            gap: 15px;
        }
        .plan-day {
            background: #f7fafc;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #48bb78;
        }
        .day-name {
            font-weight: 600;
            color: #2d3748;
            text-transform: capitalize;
        }
        .day-details {
            margin-top: 8px;
            color: #4a5568;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            .metadata {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_title }}</h1>
        <p>{{ training_config_name }} • Generated on {{ generated_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
    </div>

    <div class="section">
        <h2>Analysis Overview</h2>
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">Analysis Type</div>
                <div class="metadata-value">{{ analysis.analysis_type | title }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Status</div>
                <div class="metadata-value">{{ analysis.status | title }}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Progress</div>
                <div class="metadata-value">{{ analysis.progress_percentage }}%</div>
            </div>
            {% if analysis.total_tokens %}
            <div class="metadata-item">
                <div class="metadata-label">AI Tokens Used</div>
                <div class="metadata-value">{{ "{:,}".format(analysis.total_tokens) }}</div>
            </div>
            {% endif %}
            {% if analysis.estimated_cost %}
            <div class="metadata-item">
                <div class="metadata-label">Estimated Cost</div>
                <div class="metadata-value">{{ analysis.estimated_cost }}</div>
            </div>
            {% endif %}
        </div>
    </div>

    {% if analysis.summary_html %}
    <div class="section">
        <h2>Analysis Summary</h2>
        <div class="content">
            {{ analysis.summary_html | safe }}
        </div>
    </div>
    {% endif %}

    {% if analysis.recommendations_html %}
    <div class="section">
        <h2>Recommendations</h2>
        <div class="content">
            {{ analysis.recommendations_html | safe }}
        </div>
    </div>
    {% endif %}

    {% if analysis.weekly_plan %}
    <div class="section">
        <h2>Weekly Training Plan</h2>
        {% if analysis.weekly_plan.week_structure %}
        <div class="weekly-plan">
            {% for day, details in analysis.weekly_plan.week_structure.items() %}
            <div class="plan-day">
                <div class="day-name">{{ day }}</div>
                <div class="day-details">
                    <strong>{{ details.type | title }}</strong> • 
                    {{ details.duration }} • 
                    {{ details.intensity }}
                    {% if details.description %}
                    <br>{{ details.description }}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if analysis.weekly_plan.weekly_volume %}
        <p><strong>Weekly Volume:</strong> {{ analysis.weekly_plan.weekly_volume }}</p>
        {% endif %}
        
        {% if analysis.weekly_plan.intensity_distribution %}
        <p><strong>Intensity Distribution:</strong>
        {% for zone, percentage in analysis.weekly_plan.intensity_distribution.items() %}
            {{ zone | upper }}: {{ percentage }}{% if not loop.last %}, {% endif %}
        {% endfor %}
        </p>
        {% endif %}
    </div>
    {% endif %}

    {% if results %}
    <div class="section">
        <h2>Detailed Results</h2>
        {% for result in results %}
        <div class="result-item">
            <div class="result-header">
                <div class="result-title">{{ result.title }}</div>
                <div class="result-meta">
                    {{ result.node_name | title }} • {{ result.result_type | title }}
                    {% if result.tokens_used %} • {{ result.tokens_used }} tokens{% endif %}
                    {% if result.processing_time %} • {{ result.processing_time }}s{% endif %}
                </div>
            </div>
            {% if result.content_html %}
            <div class="result-content">
                {{ result.content_html | safe }}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>Generated by Garmin AI Coach • {{ user_name }}</p>
    </div>
</body>
</html>"""

# Global instance
report_generator = ReportGenerator()