-- Training Zone Table Migration
-- Add training zones table to support multi-discipline training zones
-- Run this SQL in pgAdmin to add the TrainingZone functionality

-- Create training zone table
CREATE TABLE IF NOT EXISTS trainingzone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    training_config_id UUID NOT NULL,
    discipline VARCHAR(20) NOT NULL,
    metric VARCHAR(100) NOT NULL,
    value VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add foreign key constraint to trainingconfig table
ALTER TABLE trainingzone 
ADD CONSTRAINT trainingzone_training_config_id_fkey 
FOREIGN KEY (training_config_id) 
REFERENCES trainingconfig(id) 
ON DELETE CASCADE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trainingzone_config_id ON trainingzone(training_config_id);
CREATE INDEX IF NOT EXISTS idx_trainingzone_discipline ON trainingzone(discipline);

-- Add check constraint for valid disciplines
ALTER TABLE trainingzone 
ADD CONSTRAINT ck_trainingzone_discipline 
CHECK (discipline IN ('Running', 'Cycling', 'Swimming'));

-- Add trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_trainingzone_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_trainingzone_updated_at
    BEFORE UPDATE ON trainingzone
    FOR EACH ROW
    EXECUTE FUNCTION update_trainingzone_updated_at();

-- Verify the table was created successfully
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'trainingzone' 
ORDER BY ordinal_position;

-- Show foreign key relationships
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'trainingzone';

COMMENT ON TABLE trainingzone IS 'Stores training zones for different disciplines (Running, Cycling, Swimming) linked to training configurations';
COMMENT ON COLUMN trainingzone.discipline IS 'Training discipline: Running, Cycling, or Swimming';
COMMENT ON COLUMN trainingzone.metric IS 'Zone description like "LTHR ≈ 171 bpm / 4:35 min/km"';
COMMENT ON COLUMN trainingzone.value IS 'Zone value like "171 bpm", "213W", "1:30/100m"';