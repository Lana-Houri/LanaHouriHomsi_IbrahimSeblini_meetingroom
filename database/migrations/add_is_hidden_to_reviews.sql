-- Migration: Add is_hidden column to Reviews table
-- This column was added to support hiding reviews from regular users

-- Add is_hidden column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'reviews' 
        AND column_name = 'is_hidden'
    ) THEN
        ALTER TABLE Reviews 
        ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE;
        
        -- Update existing reviews to have is_hidden = FALSE
        UPDATE Reviews SET is_hidden = FALSE WHERE is_hidden IS NULL;
        
        RAISE NOTICE 'Column is_hidden added to Reviews table';
    ELSE
        RAISE NOTICE 'Column is_hidden already exists in Reviews table';
    END IF;
END $$;

