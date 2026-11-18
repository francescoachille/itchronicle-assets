-- ============================================================================
-- ITChronicle Privacy Engineering Toolkit: pg-gdpr-masker.sql
-- Compliance: GDPR Art. 32 (Pseudonymization & Security of Processing)
-- Engine: PostgreSQL 14+ with pgcrypto extension
-- Purpose: Deterministic HMAC-SHA256 PII masking preserving Foreign Keys
-- ============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Create isolated schema for GDPR masking utilities
CREATE SCHEMA IF NOT EXISTS gdpr_mask;

-- 2. Deterministic HMAC-SHA256 token generator (requires session secret salt)
-- Usage before running: SET app.gdpr_salt = 'YOUR_32_BYTE_HIGH_ENTROPY_SECRET';
CREATE OR REPLACE FUNCTION gdpr_mask.hmac_token(input_val TEXT, prefix TEXT DEFAULT 'anon')
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    secret_salt TEXT;
    digest_hex  TEXT;
BEGIN
    secret_salt := current_setting('app.gdpr_salt', true);
    IF secret_salt IS NULL OR length(secret_salt) < 16 THEN
        RAISE EXCEPTION 'SECURITY ERROR: app.gdpr_salt must be set (min 16 chars) before masking.';
    END IF;

    digest_hex := encode(hmac(lower(trim(input_val)), secret_salt, 'sha256'), 'hex');
    RETURN prefix || '_' || substring(digest_hex FROM 1 FOR 16);
END;
$$;

-- 3. Deterministic Email Pseudonymizer (preserves uniqueness & JOIN integrity)
CREATE OR REPLACE FUNCTION gdpr_mask.mask_email(real_email TEXT)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT gdpr_mask.hmac_token(real_email, 'usr') || '@staging.invalid';
$$;

-- 4. Deterministic Tax ID / National ID / Phone Pseudonymizer
CREATE OR REPLACE FUNCTION gdpr_mask.mask_identifier(real_id TEXT, id_prefix TEXT DEFAULT 'ID')
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT upper(gdpr_mask.hmac_token(real_id, id_prefix));
$$;

-- 5. IPv4 / IPv6 Subnet Anonymizer (zeroes host bits / hashes full address)
CREATE OR REPLACE FUNCTION gdpr_mask.mask_ip(real_ip INET)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT '10.255.' ||
           get_byte(decode(substring(encode(hmac(host(real_ip), current_setting('app.gdpr_salt'), 'sha256'), 'hex') FROM 1 FOR 4), 'hex'), 0)::TEXT || '.' ||
           get_byte(decode(substring(encode(hmac(host(real_ip), current_setting('app.gdpr_salt'), 'sha256'), 'hex') FROM 1 FOR 4), 'hex'), 1)::TEXT;
$$;

-- 6. Example Staging Execution Procedure (Customize target tables/columns)
CREATE OR REPLACE PROCEDURE gdpr_mask.run_staging_pseudonymization()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Safety guard: abort if database name looks like production
    IF current_database() ~* '(prod|production|live|master)' THEN
        RAISE EXCEPTION 'ABORTED: Refusing to run PII masking on production database "%"', current_database();
    END IF;

    -- Example target table: public.customers
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'customers') THEN
        UPDATE public.customers
        SET
            email       = gdpr_mask.mask_email(email),
            full_name   = 'Staging User ' || substring(gdpr_mask.hmac_token(email, 'u') FROM 5 FOR 8),
            tax_code    = CASE WHEN tax_code IS NOT NULL THEN gdpr_mask.mask_identifier(tax_code, 'TAX') ELSE NULL END,
            phone       = CASE WHEN phone IS NOT NULL THEN '+39000' || substring(abs(('x' || substring(gdpr_mask.hmac_token(phone, 'p') FROM 5 FOR 8))::bit(32)::int)::text FROM 1 FOR 7) ELSE NULL END,
            last_ip     = CASE WHEN last_ip IS NOT NULL THEN gdpr_mask.mask_ip(last_ip)::inet ELSE NULL END;
    END IF;

    RAISE NOTICE 'GDPR Art. 32 deterministic pseudonymization completed on database: %', current_database();
END;
$$;

COMMIT;
