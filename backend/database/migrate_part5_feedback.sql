-- SQL Migration for Part 5 — Recommendation Feedback & Personalization
-- Adds timestamp tracking columns to funding_recommendations

ALTER TABLE funding_recommendations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE funding_recommendations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
