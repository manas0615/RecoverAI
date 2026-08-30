-- Add plan_snapshot column to recovery_actions table for storing the original approved plan
ALTER TABLE recovery_actions ADD COLUMN plan_snapshot TEXT;
