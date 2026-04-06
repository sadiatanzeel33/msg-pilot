-- Msg-Pilot Database Schema (PostgreSQL)
-- Tables are auto-created by SQLAlchemy on startup.
-- This file is for reference / manual setup.

CREATE TYPE userrole AS ENUM ('admin', 'user');
CREATE TYPE campaignstatus AS ENUM ('draft', 'scheduled', 'running', 'paused', 'completed', 'stopped');
CREATE TYPE messagestatus AS ENUM ('pending', 'sent', 'failed', 'skipped');

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(512) NOT NULL,
    role userrole DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    daily_send_count INTEGER DEFAULT 0,
    daily_send_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tags
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL
);

-- Contacts
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    group_name VARCHAR(100),
    custom_message VARCHAR(4096),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_contacts_user ON contacts(user_id);
CREATE INDEX idx_contacts_phone ON contacts(phone);

-- Contact-Tag junction
CREATE TABLE contact_tags (
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (contact_id, tag_id)
);

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    message_template TEXT NOT NULL,
    status campaignstatus DEFAULT 'draft',
    min_delay INTEGER DEFAULT 8,
    max_delay INTEGER DEFAULT 25,
    daily_limit INTEGER DEFAULT 500,
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_campaigns_user ON campaigns(user_id);

-- Campaign Contacts (delivery queue)
CREATE TABLE campaign_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    personalized_message TEXT,
    status messagestatus DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMPTZ
);
CREATE INDEX idx_cc_campaign ON campaign_contacts(campaign_id);

-- Campaign Media
CREATE TABLE campaign_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    file_path VARCHAR(512) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL
);

-- Activity Logs
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    action VARCHAR(100) NOT NULL,
    detail TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_logs_user ON activity_logs(user_id);
