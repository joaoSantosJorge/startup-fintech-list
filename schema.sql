CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE,
    website TEXT,
    all_locations TEXT,
    long_description TEXT,
    one_liner TEXT,
    team_size INTEGER,
    industry TEXT,
    subindustry TEXT,
    batch TEXT,
    status TEXT,
    stage TEXT,
    top_company INTEGER DEFAULT 0,
    is_hiring INTEGER DEFAULT 0,
    launched_at TEXT,
    yc_url TEXT
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS company_tags (
    company_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (company_id, tag_id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

CREATE TABLE IF NOT EXISTS company_industries (
    company_id INTEGER NOT NULL,
    industry_name TEXT NOT NULL,
    PRIMARY KEY (company_id, industry_name),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS company_regions (
    company_id INTEGER NOT NULL,
    region_name TEXT NOT NULL,
    PRIMARY KEY (company_id, region_name),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    company_id INTEGER PRIMARY KEY,
    urgency INTEGER CHECK(urgency BETWEEN 1 AND 10),
    market_size INTEGER CHECK(market_size BETWEEN 1 AND 10),
    pricing_potential INTEGER CHECK(pricing_potential BETWEEN 1 AND 10),
    acquisition_cost INTEGER CHECK(acquisition_cost BETWEEN 1 AND 10),
    delivery_cost INTEGER CHECK(delivery_cost BETWEEN 1 AND 10),
    uniqueness INTEGER CHECK(uniqueness BETWEEN 1 AND 10),
    speed_to_market INTEGER CHECK(speed_to_market BETWEEN 1 AND 10),
    upfront_investment INTEGER CHECK(upfront_investment BETWEEN 1 AND 10),
    upsell_potential INTEGER CHECK(upsell_potential BETWEEN 1 AND 10),
    evergreen_potential INTEGER CHECK(evergreen_potential BETWEEN 1 AND 10),
    total_score INTEGER GENERATED ALWAYS AS (
        urgency + market_size + pricing_potential + acquisition_cost +
        delivery_cost + uniqueness + speed_to_market + upfront_investment +
        upsell_potential + evergreen_potential
    ) STORED,
    replicability INTEGER CHECK(replicability BETWEEN 1 AND 10),
    niche_category TEXT,
    reasoning TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
