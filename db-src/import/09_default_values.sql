-- Lignes fixes : la devise unique (ADR 0002 §2.2) et l'analyste fictif 0 (ADR 0002 §2.1)
INSERT INTO payments.currencies (currency_id, currency)
VALUES ('USD', 'US dollar')
ON CONFLICT (currency_id) DO NOTHING;

INSERT INTO payments.analysts (analyst_id, role)
VALUES (0, 'init')
ON CONFLICT (analyst_id) DO NOTHING;