CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    category TEXT NOT NULL,
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 4),
    size_score INTEGER CHECK (size_score BETWEEN 1 AND 3),
    business_impact INTEGER CHECK (business_impact BETWEEN 1 AND 4),
    resource_type INTEGER CHECK (resource_type BETWEEN 1 AND 3),
    risk_level INTEGER CHECK (risk_level BETWEEN 1 AND 3),
    total_score INTEGER GENERATED ALWAYS AS (
        priority_level + size_score + business_impact + resource_type + risk_level
    ) STORED,
    project_tier INTEGER GENERATED ALWAYS AS (
        CASE 
            WHEN (priority_level + size_score + business_impact + resource_type + risk_level) >= 16 THEN 1
            WHEN (priority_level + size_score + business_impact + resource_type + risk_level) >= 11 THEN 2
            ELSE 3
        END
    ) STORED,
    project_phase TEXT CHECK (project_phase IN ('Planning', 'In Progress', 'On Hold', 'Completed')),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
); 
