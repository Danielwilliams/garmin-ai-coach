# 🗄️ Garmin AI Coach Database Schema Documentation

## Overview

The Garmin AI Coach web application uses a PostgreSQL database with a well-structured relational schema designed to support user management, training configuration, AI analysis workflows, and file management.

## Database Configuration

- **Database Engine**: PostgreSQL with AsyncPG driver
- **Connection Pool**: Size 5 with max overflow 10 (Railway optimized)
- **Primary Keys**: UUID4 for all tables
- **Timestamps**: All tables include timezone-aware `created_at` and `updated_at`
- **Environment**: Uses Railway DATABASE_URL with automatic asyncpg conversion

## Schema Structure

### Core Entities

```
User (Central entity)
├── GarminAccount (1:1) - Garmin Connect integration
├── TrainingConfig (1:Many) - Training profile configurations  
    ├── Competition (1:Many) - Target races and events
    └── Analysis (1:Many) - AI analysis sessions
        ├── AnalysisResult (1:Many) - Individual analysis components
        └── AnalysisFile (1:Many) - Generated files and reports
```

## Foreign Key Relationships

| Child Table | Foreign Key Column | Parent Table | Parent Column | Constraint Name |
|-------------|-------------------|--------------|---------------|-----------------|
| **analysis** | `user_id` | **user** | `id` | `analysis_user_id_fkey` |
| **analysis** | `training_config_id` | **trainingconfig** | `id` | `analysis_training_config_id_fkey` |
| **analysisfile** | `analysis_id` | **analysis** | `id` | `analysisfile_analysis_id_fkey` |
| **analysisresult** | `analysis_id` | **analysis** | `id` | `analysisresult_analysis_id_fkey` |
| **competition** | `training_config_id` | **trainingconfig** | `id` | `competition_training_config_id_fkey` |
| **garminaccount** | `user_id` | **user** | `id` | `garminaccount_user_id_fkey` |
| **trainingconfig** | `user_id` | **user** | `id` | `trainingconfig_user_id_fkey` |

## Table Definitions

### 1. User Table

**Purpose**: Central user management and authentication

**Key Fields**:
- `id` (UUID, PK) - Unique user identifier
- `email` (String, Unique, Indexed) - Login email and primary identifier
- `full_name` (String) - User's full name
- `hashed_password` (String) - Argon2 hashed password
- `is_active` (Boolean) - Account active status
- `is_verified` (Boolean) - Email verification status
- `athlete_context` (Text) - Analysis context for AI coaching
- `planning_context` (Text) - Planning context for AI coaching

**Relationships**: 
- 1:1 with GarminAccount
- 1:Many with TrainingConfig
- 1:Many with Analysis

### 2. GarminAccount Table

**Purpose**: Garmin Connect integration and credential management

**Key Fields**:
- `id` (UUID, PK) - Unique account identifier
- `user_id` (UUID, FK) - References User.id
- `email` (String) - Garmin Connect login email
- `encrypted_password` (String) - Encrypted Garmin password
- `is_connected` (Boolean) - Connection status
- `last_sync` (DateTime) - Last successful data sync
- `sync_error` (Text) - Latest sync error message
- `activities_days` (String) - Days of activity data to extract
- `metrics_days` (String) - Days of metrics data to extract

**Security**: Passwords are encrypted before storage

### 3. TrainingConfig Table

**Purpose**: Training profile configurations and AI analysis settings

**Key Fields**:
- `id` (UUID, PK) - Unique configuration identifier
- `user_id` (UUID, FK) - References User.id
- `name` (String) - Configuration name
- `is_active` (Boolean) - Active configuration flag
- `analysis_context` (Text) - Context for AI analysis
- `planning_context` (Text) - Context for AI planning
- `activities_days` (Integer) - Days of activity data to analyze
- `metrics_days` (Integer) - Days of metrics data to analyze
- `ai_mode` (String) - AI analysis mode: development/standard/cost_effective
- `enable_plotting` (Boolean) - Generate analysis plots
- `hitl_enabled` (Boolean) - Human-in-the-loop enabled
- `skip_synthesis` (Boolean) - Skip final synthesis step
- `output_directory` (String) - Output directory path

**AI Modes**:
- `development`: Most comprehensive analysis (highest cost)
- `standard`: Balanced analysis for most users
- `cost_effective`: Budget-optimized analysis

### 4. Competition Table

**Purpose**: Target races and events for training periodization

**Key Fields**:
- `id` (UUID, PK) - Unique competition identifier
- `training_config_id` (UUID, FK) - References TrainingConfig.id
- `name` (String) - Race/event name
- `date` (String) - Race date (YYYY-MM-DD or text format)
- `race_type` (String) - Type of race (Marathon, Olympic Tri, etc.)
- `priority` (String) - Priority level: A/B/C
- `target_time` (String) - Target finish time (HH:MM:SS)
- `bikereg_id` (Integer) - BikeReg event ID for integration
- `runreg_url` (String) - RunReg event URL for integration

**Priority System**:
- **A Priority**: Peak performance target races
- **B Priority**: Important races, not main focus
- **C Priority**: Training races and fun events

### 5. Analysis Table

**Purpose**: AI analysis session management and workflow tracking

**Key Fields**:
- `id` (UUID, PK) - Unique analysis identifier
- `user_id` (UUID, FK) - References User.id
- `training_config_id` (UUID, FK) - References TrainingConfig.id
- `status` (String) - Analysis status: pending/running/completed/failed
- `analysis_type` (String) - Type of analysis requested
- `workflow_id` (String) - LangGraph workflow identifier
- `current_node` (String) - Current processing node
- `progress_percentage` (Integer) - Analysis completion percentage
- `summary` (Text) - Analysis summary
- `recommendations` (Text) - AI recommendations
- `weekly_plan` (JSON) - Structured weekly training plan
- `start_date` (DateTime) - Analysis period start
- `end_date` (DateTime) - Analysis period end
- `data_summary` (JSON) - Processed data summary
- `total_tokens` (Integer) - AI tokens consumed
- `estimated_cost` (String) - Cost estimate for analysis
- `error_message` (Text) - Error details if failed
- `retry_count` (Integer) - Number of retry attempts

**LangGraph Integration**: Tracks multi-agent AI workflow progress

### 6. AnalysisResult Table

**Purpose**: Individual components and outputs from AI analysis

**Key Fields**:
- `id` (UUID, PK) - Unique result identifier
- `analysis_id` (UUID, FK) - References Analysis.id
- `node_name` (String) - LangGraph node that generated result
- `result_type` (String) - Type: summary/plan/plot/recommendation
- `title` (String) - Result title/description
- `content` (Text) - Text content
- `data` (JSON) - Structured data output
- `file_path` (String) - Path to generated files
- `tokens_used` (Integer) - AI tokens for this component
- `processing_time` (Integer) - Processing time in seconds

**Result Types**: Supports various AI output formats

### 7. AnalysisFile Table

**Purpose**: File management for analysis-generated content

**Key Fields**:
- `id` (UUID, PK) - Unique file identifier
- `analysis_id` (UUID, FK) - References Analysis.id
- `filename` (String) - Original filename
- `file_type` (String) - Type: plot/report/data
- `mime_type` (String) - MIME type for proper serving
- `file_size` (Integer) - File size in bytes
- `file_path` (String) - Storage path (local/S3)
- `is_public` (Boolean) - Public access flag
- `download_count` (Integer) - Usage tracking

**File Types**: Supports plots, reports, and data exports

## Data Flow Patterns

### 1. User Registration & Setup
```
User Creation → GarminAccount Setup → TrainingConfig Creation → Competition Addition
```

### 2. Analysis Workflow
```
TrainingConfig Selection → Analysis Creation → LangGraph Processing → Results Generation → File Storage
```

### 3. Training Profile Workflow (Web App)
```
User Login → Profile Wizard → TrainingConfig Creation → Competition Setup → Analysis Trigger
```

## Migration Considerations

### Current Schema vs. Web App Requirements

**✅ Well Aligned**:
- User management and authentication
- Training configuration structure
- Competition management with priorities
- Analysis workflow integration

**⚠️ Potential Extensions Needed**:
1. **Training Zones**: No dedicated table for storing training zones
   - Current: No zone storage
   - Web App Need: Multiple zones per discipline (Running/Cycling/Swimming)

2. **Athlete Profile**: Limited athlete-specific fields
   - Current: Basic name/email in User table
   - Web App Need: Dedicated athlete information

3. **External Race Integration**: Partially supported
   - Current: BikeReg ID and RunReg URL in Competition table
   - Web App Need: Enhanced external race management

### Recommended Schema Extensions

```sql
-- Add Training Zones table
CREATE TABLE training_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    training_config_id UUID REFERENCES trainingconfig(id),
    discipline VARCHAR(20) NOT NULL, -- Running, Cycling, Swimming
    metric_description TEXT NOT NULL,
    zone_value VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_training_zones_config_id ON training_zones(training_config_id);
CREATE INDEX idx_training_zones_discipline ON training_zones(discipline);
```

## Performance Considerations

### Indexes
- All foreign key columns are indexed
- User.email has unique index for fast auth lookups
- Consider composite indexes for common query patterns

### Query Patterns
- User → TrainingConfigs → Competitions (common dashboard pattern)
- Analysis → AnalysisResults + AnalysisFiles (results display)
- TrainingConfig → Analysis (analysis history)

## Security Considerations

1. **Password Storage**: Argon2 hashing with proper salting
2. **Credential Encryption**: Garmin passwords encrypted before storage
3. **Access Control**: User-based data isolation through foreign keys
4. **File Access**: Public/private flag on AnalysisFile for controlled access

## Development Notes

- All models inherit from base model with UUID PK and timestamps
- Async SQLAlchemy for non-blocking database operations
- Proper error handling for constraint violations
- Connection pooling optimized for Railway deployment
- Environment-based configuration for different deployment stages

---

*Database schema documentation maintained for development reference*