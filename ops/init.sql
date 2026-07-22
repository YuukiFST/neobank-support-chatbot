-- NeoBank Support Chatbot — Postgres schema
-- Phase 1: Foundation tables

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    document VARCHAR(14) NOT NULL UNIQUE,  -- CPF mask: XXX.XXX.XXX-XX
    address_cep VARCHAR(9),
    language VARCHAR(5) DEFAULT 'pt',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Accounts
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('pix', 'transfer', 'card', 'fee')),
    amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'settled' CHECK (status IN ('pending', 'settled', 'failed')),
    risk_flag BOOLEAN DEFAULT FALSE,
    description TEXT,
    reference VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cards
CREATE TABLE IF NOT EXISTS cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    kind VARCHAR(10) NOT NULL CHECK (kind IN ('credit', 'debit')),
    state VARCHAR(10) NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'blocked')),
    limit_amount DECIMAL(15,2) DEFAULT 0.00,
    last_four VARCHAR(4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID NOT NULL REFERENCES cards(id),
    month VARCHAR(7) NOT NULL,  -- YYYY-MM
    total DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(10) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'paid')),
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Investments
CREATE TABLE IF NOT EXISTS investments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    product VARCHAR(20) NOT NULL CHECK (product IN ('cdb', 'savings')),
    principal DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sessions (LangGraph checkpointer state)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    language VARCHAR(5) DEFAULT 'pt',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_active TIMESTAMPTZ DEFAULT NOW()
);

-- Handoffs (escalation payloads)
CREATE TABLE IF NOT EXISTS handoffs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    payload JSONB NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'claimed', 'resolved')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session metrics (FinOps)
CREATE TABLE IF NOT EXISTS session_metrics (
    session_id UUID PRIMARY KEY REFERENCES sessions(id),
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost_brl_equiv DECIMAL(10,6) DEFAULT 0.00,
    latency_p95_ms INTEGER DEFAULT 0,
    turns INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer facts (long-term memory)
CREATE TABLE IF NOT EXISTS customer_facts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    fact TEXT NOT NULL,
    source_session_id UUID REFERENCES sessions(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LangGraph checkpointer state table
CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id VARCHAR(255) PRIMARY KEY,
    thread_id VARCHAR(255) NOT NULL,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_cards_account ON cards(account_id);
CREATE INDEX IF NOT EXISTS idx_invoices_card ON invoices(card_id);
CREATE INDEX IF NOT EXISTS idx_investments_customer ON investments(customer_id);
CREATE INDEX IF NOT EXISTS idx_sessions_customer ON sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_handoffs_status ON handoffs(status);
CREATE INDEX IF NOT EXISTS idx_customer_facts_customer ON customer_facts(customer_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread ON checkpoints(thread_id);

-- Seed data
\i /docker-entrypoint-initdb.d/customers.sql
