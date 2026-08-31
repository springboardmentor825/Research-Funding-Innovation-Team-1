-- Safe ALTER TABLE script for funding_opportunities table

ALTER TABLE funding_opportunities 
  MODIFY COLUMN research_domains TEXT NULL,
  MODIFY COLUMN technology_areas TEXT NULL,
  MODIFY COLUMN keywords TEXT NULL,
  MODIFY COLUMN eligibility TEXT NULL,
  MODIFY COLUMN geographic_scope VARCHAR(255) NULL,
  ALTER COLUMN status SET DEFAULT 'active';

-- Normalize existing status values from 'open' to 'active'
UPDATE funding_opportunities SET status = 'active' WHERE status = 'open';
