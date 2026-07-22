-- NeoBank seed data — synthetic customers, accounts, transactions, cards, invoices, investments

-- Customers
INSERT INTO customers (id, name, document, address_cep, language) VALUES
('11111111-1111-1111-1111-111111111111', 'Maria Silva', '123.456.789-00', '01310-100', 'pt'),
('22222222-2222-2222-2222-222222222222', 'John Smith', '987.654.321-00', '10080-000', 'pt'),
('33333333-3333-3333-3333-333333333333', 'Ana Costa', '456.789.123-00', '20040-020', 'pt'),
('44444444-4444-4444-4444-444444444444', 'Carlos Pereira', '321.654.987-00', '30130-000', 'pt');

-- Accounts
INSERT INTO accounts (id, customer_id, balance) VALUES
('aaaa1111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 5250.75),
('aaaa2222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 12300.00),
('aaaa3333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 890.50),
('aaaa4444-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444444', 31000.00);

-- Transactions
INSERT INTO transactions (account_id, type, amount, status, risk_flag, description, reference, created_at) VALUES
-- Maria's transactions
('aaaa1111-1111-1111-1111-111111111111', 'pix', 150.00, 'settled', false, 'PIX to João', 'PIX-001', '2025-01-15 10:30:00'),
('aaaa1111-1111-1111-1111-111111111111', 'card', 89.90, 'settled', false, 'Netflix subscription', 'CARD-002', '2025-01-14 08:00:00'),
('aaaa1111-1111-1111-1111-111111111111', 'transfer', 500.00, 'settled', false, 'Transfer to savings', 'TRF-003', '2025-01-13 14:00:00'),
('aaaa1111-1111-1111-1111-111111111111', 'fee', 12.90, 'settled', false, 'Monthly fee', 'FEE-004', '2025-01-01 00:00:00'),
('aaaa1111-1111-1111-1111-111111111111', 'pix', 2500.00, 'settled', true, 'Suspicious large transfer', 'PIX-005', '2025-01-10 02:30:00'),
-- John's transactions
('aaaa2222-2222-2222-2222-222222222222', 'pix', 300.00, 'settled', false, 'Rent payment', 'PIX-101', '2025-01-15 09:00:00'),
('aaaa2222-2222-2222-2222-222222222222', 'card', 45.50, 'settled', false, 'Uber ride', 'CARD-102', '2025-01-14 18:30:00'),
('aaaa2222-2222-2222-2222-222222222222', 'transfer', 2000.00, 'settled', false, 'Wire to US account', 'TRF-103', '2025-01-12 11:00:00'),
-- Ana's transactions (fraud scenario)
('aaaa3333-3333-3333-3333-333333333333', 'card', 890.00, 'settled', true, 'Unknown purchase — suspected fraud', 'CARD-201', '2025-01-15 03:00:00'),
('aaaa3333-3333-3333-3333-333333333333', 'card', 450.00, 'settled', true, 'Another suspicious charge', 'CARD-202', '2025-01-14 04:15:00'),
('aaaa3333-3333-3333-3333-333333333333', 'pix', 25.00, 'settled', false, 'Lunch payment', 'PIX-203', '2025-01-13 12:00:00');

-- Cards
INSERT INTO cards (account_id, kind, state, limit_amount, last_four) VALUES
('aaaa1111-1111-1111-1111-111111111111', 'credit', 'active', 5000.00, '4532'),
('aaaa1111-1111-1111-1111-111111111111', 'debit', 'active', 0.00, '7890'),
('aaaa2222-2222-2222-2222-222222222222', 'credit', 'active', 10000.00, '5678'),
('aaaa3333-3333-3333-3333-333333333333', 'credit', 'active', 2000.00, '3456'),
('aaaa4444-4444-4444-4444-444444444444', 'credit', 'active', 20000.00, '1234');

-- Invoices
INSERT INTO invoices (card_id, month, total, status, due_date) VALUES
-- Maria's card invoice
((SELECT id FROM cards WHERE account_id = 'aaaa1111-1111-1111-1111-111111111111' AND kind = 'credit'), '2025-01', 456.78, 'open', '2025-02-10'),
((SELECT id FROM cards WHERE account_id = 'aaaa1111-1111-1111-1111-111111111111' AND kind = 'credit'), '2024-12', 320.50, 'paid', '2025-01-10'),
-- John's card invoice
((SELECT id FROM cards WHERE account_id = 'aaaa2222-2222-2222-2222-222222222222' AND kind = 'credit'), '2025-01', 1200.00, 'open', '2025-02-15'),
-- Ana's card invoice (fraud charges)
((SELECT id FROM cards WHERE account_id = 'aaaa3333-3333-3333-3333-333333333333' AND kind = 'credit'), '2025-01', 1365.00, 'open', '2025-02-05');

-- Investments
INSERT INTO investments (customer_id, product, principal) VALUES
('11111111-1111-1111-1111-111111111111', 'cdb', 10000.00),
('11111111-1111-1111-1111-111111111111', 'savings', 5000.00),
('22222222-2222-2222-2222-222222222222', 'cdb', 25000.00),
('44444444-4444-4444-4444-444444444444', 'savings', 50000.00);

-- Customer facts (long-term memory)
INSERT INTO customer_facts (customer_id, fact, source_session_id) VALUES
('11111111-1111-1111-1111-111111111111', 'Customer prefers Portuguese and uses PIX frequently', NULL),
('33333333-3333-3333-3333-333333333333', 'Customer reported fraud on 2025-01-15 — two suspicious card charges', NULL);
