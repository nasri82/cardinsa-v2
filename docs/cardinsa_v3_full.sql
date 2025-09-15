--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-09-03 11:15:52

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 16 (class 2615 OID 243961)
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- TOC entry 10518 (class 0 OID 0)
-- Dependencies: 16
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- TOC entry 9 (class 3079 OID 244179)
-- Name: cube; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS cube WITH SCHEMA public;


--
-- TOC entry 10519 (class 0 OID 0)
-- Dependencies: 9
-- Name: EXTENSION cube; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION cube IS 'data type for multidimensional cubes';


--
-- TOC entry 10 (class 3079 OID 244268)
-- Name: earthdistance; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS earthdistance WITH SCHEMA public;


--
-- TOC entry 10520 (class 0 OID 0)
-- Dependencies: 10
-- Name: EXTENSION earthdistance; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION earthdistance IS 'calculate great-circle distances on the surface of the Earth';


--
-- TOC entry 11 (class 3079 OID 244284)
-- Name: hypopg; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS hypopg WITH SCHEMA public;


--
-- TOC entry 10521 (class 0 OID 0)
-- Dependencies: 11
-- Name: EXTENSION hypopg; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION hypopg IS 'Hypothetical indexes for PostgreSQL';


--
-- TOC entry 2 (class 3079 OID 244306)
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- TOC entry 10522 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- TOC entry 3 (class 3079 OID 244337)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 10523 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- TOC entry 7 (class 3079 OID 244131)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 10524 (class 0 OID 0)
-- Dependencies: 7
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 5 (class 3079 OID 242881)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 10525 (class 0 OID 0)
-- Dependencies: 5
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 6 (class 3079 OID 243962)
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- TOC entry 10526 (class 0 OID 0)
-- Dependencies: 6
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- TOC entry 8 (class 3079 OID 244168)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 10527 (class 0 OID 0)
-- Dependencies: 8
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 4 (class 3079 OID 244418)
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- TOC entry 10528 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- TOC entry 2490 (class 1247 OID 244747)
-- Name: claimstatusenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.claimstatusenum AS ENUM (
    'pending',
    'approved',
    'rejected',
    'in_review',
    'completed',
    'cancelled',
    'under_investigation'
);


ALTER TYPE public.claimstatusenum OWNER TO postgres;

--
-- TOC entry 2493 (class 1247 OID 244762)
-- Name: claimtypeenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.claimtypeenum AS ENUM (
    'medical',
    'motor',
    'property',
    'life',
    'travel',
    'cyber',
    'disability'
);


ALTER TYPE public.claimtypeenum OWNER TO postgres;

--
-- TOC entry 2496 (class 1247 OID 244778)
-- Name: docstatusenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.docstatusenum AS ENUM (
    'pending',
    'approved',
    'rejected',
    'expired',
    'under_review'
);


ALTER TYPE public.docstatusenum OWNER TO postgres;

--
-- TOC entry 2499 (class 1247 OID 244790)
-- Name: notification_channel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.notification_channel AS ENUM (
    'email',
    'sms',
    'whatsapp',
    'push',
    'in_app',
    'voice_call'
);


ALTER TYPE public.notification_channel OWNER TO postgres;

--
-- TOC entry 2502 (class 1247 OID 244804)
-- Name: payment_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'refunded',
    'disputed',
    'cancelled'
);


ALTER TYPE public.payment_status OWNER TO postgres;

--
-- TOC entry 2505 (class 1247 OID 244820)
-- Name: policy_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.policy_status AS ENUM (
    'quoted',
    'bound',
    'active',
    'lapsed',
    'cancelled',
    'non_renewed',
    'suspended',
    'pending'
);


ALTER TYPE public.policy_status OWNER TO postgres;

--
-- TOC entry 2508 (class 1247 OID 244838)
-- Name: quotation_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.quotation_status AS ENUM (
    'draft',
    'pending_review',
    'quoted',
    'sent',
    'accepted',
    'rejected',
    'expired',
    'bound',
    'cancelled'
);


ALTER TYPE public.quotation_status OWNER TO postgres;

--
-- TOC entry 2511 (class 1247 OID 244858)
-- Name: risk_level; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.risk_level AS ENUM (
    'very_low',
    'low',
    'medium',
    'high',
    'very_high',
    'critical'
);


ALTER TYPE public.risk_level OWNER TO postgres;

--
-- TOC entry 2514 (class 1247 OID 244872)
-- Name: underwriting_decision; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.underwriting_decision AS ENUM (
    'accept',
    'decline',
    'refer',
    'counter_offer',
    'conditional_accept'
);


ALTER TYPE public.underwriting_decision OWNER TO postgres;

--
-- TOC entry 1724 (class 1255 OID 250040)
-- Name: apply_audit_triggers(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.apply_audit_triggers() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Apply to critical business tables
    DROP TRIGGER IF EXISTS audit_trigger_policies ON policies;
    CREATE TRIGGER audit_trigger_policies 
        AFTER INSERT OR UPDATE OR DELETE ON policies
        FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger();
    
    DROP TRIGGER IF EXISTS audit_trigger_claims ON claims;
    CREATE TRIGGER audit_trigger_claims 
        AFTER INSERT OR UPDATE OR DELETE ON claims
        FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger();
    
    DROP TRIGGER IF EXISTS audit_trigger_members ON members;
    CREATE TRIGGER audit_trigger_members 
        AFTER INSERT OR UPDATE OR DELETE ON members
        FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger();
    
    DROP TRIGGER IF EXISTS audit_trigger_quotations ON quotations;
    CREATE TRIGGER audit_trigger_quotations 
        AFTER INSERT OR UPDATE OR DELETE ON quotations
        FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger();
        
    DROP TRIGGER IF EXISTS audit_trigger_premium_invoices ON premium_invoices;
    CREATE TRIGGER audit_trigger_premium_invoices 
        AFTER INSERT OR UPDATE OR DELETE ON premium_invoices
        FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger();
END;
$$;


ALTER FUNCTION public.apply_audit_triggers() OWNER TO postgres;

--
-- TOC entry 1290 (class 1255 OID 250066)
-- Name: archive_old_records(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.archive_old_records() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Archive old audit logs (older than 2 years)
    WITH archived AS (
        DELETE FROM audit_logs 
        WHERE created_at < NOW() - INTERVAL '2 years'
        RETURNING *
    )
    SELECT COUNT(*) INTO archived_count FROM archived;
    
    RAISE NOTICE 'Archived % audit log records', archived_count;
    
    -- Archive old workflow logs
    DELETE FROM workflow_queue 
    WHERE status = 'completed' 
    AND completed_at < NOW() - INTERVAL '6 months';
    
    -- Update statistics
    ANALYZE;
END;
$$;


ALTER FUNCTION public.archive_old_records() OWNER TO postgres;

--
-- TOC entry 852 (class 1255 OID 250046)
-- Name: auto_approve_claim(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.auto_approve_claim(p_claim_id uuid) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    claim_record RECORD;
    policy_record RECORD;
    approval_threshold NUMERIC := 5000.00;
BEGIN
    -- Get claim details
    SELECT * INTO claim_record FROM claims WHERE id = p_claim_id;
    
    -- Get policy details
    SELECT * INTO policy_record FROM policies WHERE id = claim_record.policy_id;
    
    -- Auto-approval logic
    IF claim_record.claim_amount <= approval_threshold AND
       claim_record.fraud_score < 0.3 AND
       policy_record.status = 'active' THEN
        
        -- Update claim status
        UPDATE claims 
        SET status = 'approved', 
            approved_at = CURRENT_TIMESTAMP,
            approved_by = uuid_nil() -- System approval
        WHERE id = p_claim_id;
        
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$;


ALTER FUNCTION public.auto_approve_claim(p_claim_id uuid) OWNER TO postgres;

--
-- TOC entry 739 (class 1255 OID 250045)
-- Name: calculate_premium_adjustment(uuid, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_premium_adjustment(p_policy_id uuid, p_risk_factors jsonb) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    base_premium NUMERIC;
    adjustment_factor NUMERIC := 1.0;
    risk_score NUMERIC;
BEGIN
    -- Get base premium
    SELECT premium_amount INTO base_premium 
    FROM policies WHERE id = p_policy_id;
    
    -- Calculate risk adjustments based on factors
    IF p_risk_factors ? 'age' THEN
        risk_score := (p_risk_factors->>'age')::NUMERIC;
        IF risk_score > 65 THEN
            adjustment_factor := adjustment_factor * 1.2;
        ELSIF risk_score < 25 THEN
            adjustment_factor := adjustment_factor * 1.1;
        END IF;
    END IF;
    
    -- Add more risk factor calculations as needed
    
    RETURN base_premium * adjustment_factor;
END;
$$;


ALTER FUNCTION public.calculate_premium_adjustment(p_policy_id uuid, p_risk_factors jsonb) OWNER TO postgres;

--
-- TOC entry 1761 (class 1255 OID 248161)
-- Name: calculate_remaining_benefit(uuid, uuid, uuid, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_remaining_benefit(p_member_id uuid, p_policy_id uuid, p_benefit_schedule_id uuid, p_period_type character varying DEFAULT 'annual'::character varying) RETURNS TABLE(remaining_amount numeric, remaining_count integer)
    LANGUAGE plpgsql
    AS $$
DECLARE
    benefit_limit NUMERIC;
    benefit_count_limit INTEGER;
    utilized_amt NUMERIC;
    utilized_cnt INTEGER;
BEGIN
    -- Get benefit limits
    SELECT limit_amount INTO benefit_limit
    FROM plan_benefit_schedules 
    WHERE id = p_benefit_schedule_id;
    
    -- Get utilization
    SELECT COALESCE(mbu.utilized_amount, 0), COALESCE(mbu.utilized_count, 0)
    INTO utilized_amt, utilized_cnt
    FROM member_benefit_utilization mbu
    WHERE mbu.member_id = p_member_id 
      AND mbu.policy_id = p_policy_id 
      AND mbu.benefit_schedule_id = p_benefit_schedule_id
      AND mbu.period_type = p_period_type;
    
    RETURN QUERY SELECT 
        COALESCE(benefit_limit - utilized_amt, benefit_limit),
        COALESCE(benefit_count_limit - utilized_cnt, benefit_count_limit);
END;
$$;


ALTER FUNCTION public.calculate_remaining_benefit(p_member_id uuid, p_policy_id uuid, p_benefit_schedule_id uuid, p_period_type character varying) OWNER TO postgres;

--
-- TOC entry 1711 (class 1255 OID 250098)
-- Name: deploy_missing_enhancements(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.deploy_missing_enhancements() RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    result_msg TEXT := '';
BEGIN
    -- Apply audit triggers
    PERFORM apply_audit_triggers();
    result_msg := result_msg || 'Audit triggers applied. ';
    
    -- Archive old data
    PERFORM archive_old_records();
    result_msg := result_msg || 'Data archival completed. ';
    
    -- Update statistics
    ANALYZE;
    result_msg := result_msg || 'Database statistics updated. ';
    
    RETURN 'SUCCESS: ' || result_msg;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'ERROR: ' || SQLERRM;
END;
$$;


ALTER FUNCTION public.deploy_missing_enhancements() OWNER TO postgres;

--
-- TOC entry 1449 (class 1255 OID 247702)
-- Name: enhanced_audit_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.enhanced_audit_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Include user context, IP address, application name
    INSERT INTO audit_logs (
        table_name, record_id, action, performed_by,
        old_data, new_data, user_ip, application_name
    ) VALUES (
        TG_TABLE_NAME, 
        CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
        TG_OP, 
        current_setting('app.current_user_id', true)::uuid,
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' THEN row_to_json(NEW) 
             WHEN TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END,
        current_setting('app.user_ip', true),
        current_setting('application_name', true)
    );
    RETURN COALESCE(NEW, OLD);
END;
$$;


ALTER FUNCTION public.enhanced_audit_trigger() OWNER TO postgres;

--
-- TOC entry 1381 (class 1255 OID 250097)
-- Name: log_performance_metric(character varying, numeric, character varying, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.log_performance_metric(p_metric_name character varying, p_metric_value numeric, p_table_name character varying DEFAULT NULL::character varying, p_execution_time numeric DEFAULT NULL::numeric) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO performance_metrics (
        metric_name, metric_value, table_name, execution_time_ms
    ) VALUES (
        p_metric_name, p_metric_value, p_table_name, p_execution_time
    );
END;
$$;


ALTER FUNCTION public.log_performance_metric(p_metric_name character varying, p_metric_value numeric, p_table_name character varying, p_execution_time numeric) OWNER TO postgres;

--
-- TOC entry 1661 (class 1255 OID 247707)
-- Name: perform_maintenance(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.perform_maintenance() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update table statistics
    ANALYZE;
    
    -- Cleanup old audit logs (older than 2 years)
    DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '2 years';
    
    -- Vacuum analyze critical tables
    PERFORM pg_advisory_lock(12345);
    VACUUM ANALYZE members, policies, claims;
    PERFORM pg_advisory_unlock(12345);
END;
$$;


ALTER FUNCTION public.perform_maintenance() OWNER TO postgres;

--
-- TOC entry 1279 (class 1255 OID 247933)
-- Name: sync_company_name_to_policies(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_company_name_to_policies() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE policies SET company_name = NEW.name WHERE company_id = NEW.id;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_company_name_to_policies() OWNER TO postgres;

--
-- TOC entry 1427 (class 1255 OID 247931)
-- Name: sync_group_name_to_documents(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_group_name_to_documents() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE documents SET group_name = NEW.name WHERE group_id = NEW.id;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_group_name_to_documents() OWNER TO postgres;

--
-- TOC entry 1305 (class 1255 OID 247929)
-- Name: sync_member_name_to_claims(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_member_name_to_claims() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE claims SET member_name = NEW.full_name WHERE member_id = NEW.id;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_member_name_to_claims() OWNER TO postgres;

--
-- TOC entry 1362 (class 1255 OID 247935)
-- Name: sync_provider_name_to_claims(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_provider_name_to_claims() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE claims SET provider_name = NEW.name WHERE provider_id = NEW.id;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_provider_name_to_claims() OWNER TO postgres;

--
-- TOC entry 1089 (class 1255 OID 250047)
-- Name: trigger_workflow_automation(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.trigger_workflow_automation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Trigger workflows based on status changes
    
    -- Policy activation workflow
    IF TG_TABLE_NAME = 'policies' AND NEW.status = 'active' AND OLD.status != 'active' THEN
        INSERT INTO workflow_queue (entity_type, entity_id, workflow_type, priority)
        VALUES ('policy', NEW.id, 'activation', 'high');
    END IF;
    
    -- Claim processing workflow
    IF TG_TABLE_NAME = 'claims' AND NEW.status = 'submitted' THEN
        INSERT INTO workflow_queue (entity_type, entity_id, workflow_type, priority)
        VALUES ('claim', NEW.id, 'processing', 'medium');
    END IF;
    
    -- Quote expiration workflow
    IF TG_TABLE_NAME = 'quotations' AND NEW.quote_expires_at < NOW() THEN
        INSERT INTO workflow_queue (entity_type, entity_id, workflow_type, priority)
        VALUES ('quotation', NEW.id, 'expiration', 'low');
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.trigger_workflow_automation() OWNER TO postgres;

--
-- TOC entry 950 (class 1255 OID 248162)
-- Name: update_benefit_utilization(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_benefit_utilization() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- This would be called when claims are processed
    -- Implementation depends on your claims processing workflow
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_benefit_utilization() OWNER TO postgres;

--
-- TOC entry 1638 (class 1255 OID 250043)
-- Name: validate_claim_amounts(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_claim_amounts() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Validate claim amounts are positive
    IF NEW.claim_amount <= 0 THEN
        RAISE EXCEPTION 'Claim amount must be positive';
    END IF;
    
    -- Validate reserved amount
    IF NEW.reserved_amount IS NOT NULL AND NEW.reserved_amount < NEW.claim_amount THEN
        RAISE EXCEPTION 'Reserved amount cannot be less than claim amount';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validate_claim_amounts() OWNER TO postgres;

--
-- TOC entry 1619 (class 1255 OID 250044)
-- Name: validate_member_data(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_member_data() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
BEGIN
    -- Validate email format
    IF NEW.email IS NOT NULL AND NEW.email !~ '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$' THEN
        RAISE EXCEPTION 'Invalid email format: %', NEW.email;
    END IF;
    
    -- Validate phone number
    IF NEW.phone IS NOT NULL AND NOT validate_phone(NEW.phone) THEN
        RAISE EXCEPTION 'Invalid phone number format: %', NEW.phone;
    END IF;
    
    -- Validate age restrictions
    IF NEW.date_of_birth IS NOT NULL AND 
       EXTRACT(YEAR FROM age(NEW.date_of_birth)) > 150 THEN
        RAISE EXCEPTION 'Invalid date of birth: age cannot exceed 150 years';
    END IF;
    
    RETURN NEW;
END;
$_$;


ALTER FUNCTION public.validate_member_data() OWNER TO postgres;

--
-- TOC entry 1092 (class 1255 OID 247701)
-- Name: validate_phone(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_phone(phone_number text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN phone_number ~ '^[\+]?[0-9\-\(\)\s]+$';
END;
$_$;


ALTER FUNCTION public.validate_phone(phone_number text) OWNER TO postgres;

--
-- TOC entry 1411 (class 1255 OID 250042)
-- Name: validate_policy_dates(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_policy_dates() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Validate policy effective dates
    IF NEW.effective_date >= NEW.expiry_date THEN
        RAISE EXCEPTION 'Policy effective date must be before expiry date';
    END IF;
    
    -- Validate renewal dates
    IF NEW.renewal_date IS NOT NULL AND NEW.renewal_date <= NEW.effective_date THEN
        RAISE EXCEPTION 'Renewal date must be after effective date';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.validate_policy_dates() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 241 (class 1259 OID 244883)
-- Name: accounting_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounting_audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_type text,
    entry_id uuid,
    action text,
    user_id uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.accounting_audit_logs OWNER TO postgres;

--
-- TOC entry 362 (class 1259 OID 245884)
-- Name: members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.members (
    member_number character varying(30),
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    date_of_birth date,
    gender character varying(10),
    email character varying(100) NOT NULL,
    phone character varying(20),
    address text,
    city character varying(50),
    state character varying(50),
    country character varying(50),
    postal_code character varying(20),
    company_id uuid,
    group_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_at timestamp with time zone DEFAULT now(),
    geom public.geometry(Point,4326),
    full_name character varying,
    password_hash text,
    last_login_at timestamp without time zone,
    login_method character varying(50),
    national_id_number character varying(50),
    insurance_id_card_number character varying(50),
    preferred_language character varying(10) DEFAULT 'en'::character varying,
    dependents_count integer DEFAULT 0,
    full_name_ar character varying(255),
    address_ar text,
    city_ar character varying(255),
    state_ar character varying(255),
    country_ar character varying(255),
    source_channel character varying(100),
    referred_by character varying(100),
    is_test_account boolean DEFAULT false,
    last_password_change_at timestamp without time zone,
    password_reset_token character varying(255),
    reset_token_expires_at timestamp without time zone,
    two_fa_enabled boolean DEFAULT false,
    nationality character varying(100),
    deleted_at timestamp without time zone,
    metadata jsonb,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT chk_members_email_format CHECK (((email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))
);


ALTER TABLE public.members OWNER TO postgres;

--
-- TOC entry 533 (class 1259 OID 247721)
-- Name: active_members; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_members AS
 SELECT member_number,
    first_name,
    last_name,
    date_of_birth,
    gender,
    email,
    phone,
    address,
    city,
    state,
    country,
    postal_code,
    company_id,
    group_id,
    is_active,
    created_at,
    created_by,
    updated_at,
    geom,
    full_name,
    password_hash,
    last_login_at,
    login_method,
    national_id_number,
    insurance_id_card_number,
    preferred_language,
    dependents_count,
    full_name_ar,
    address_ar,
    city_ar,
    state_ar,
    country_ar,
    source_channel,
    referred_by,
    is_test_account,
    last_password_change_at,
    password_reset_token,
    reset_token_expires_at,
    two_fa_enabled,
    nationality,
    deleted_at,
    metadata,
    id
   FROM public.members
  WHERE (deleted_at IS NULL);


ALTER VIEW public.active_members OWNER TO postgres;

--
-- TOC entry 585 (class 1259 OID 249071)
-- Name: activity_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_log (
    id uuid NOT NULL,
    user_id uuid,
    activity text,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.activity_log OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 244890)
-- Name: actuarial_tables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.actuarial_tables (
    table_name character varying(100) NOT NULL,
    table_type character varying(50),
    version character varying(20) NOT NULL,
    effective_date date NOT NULL,
    expiry_date date,
    geographic_scope character varying(50),
    demographic_scope jsonb,
    table_data jsonb NOT NULL,
    data_source character varying(100),
    regulatory_approval character varying(50),
    approved_by uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.actuarial_tables OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 244898)
-- Name: age_brackets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.age_brackets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    bracket_name character varying(100) NOT NULL,
    min_age integer NOT NULL,
    max_age integer NOT NULL,
    base_rate numeric(15,2) NOT NULL,
    description text,
    insurance_type character varying(50) DEFAULT 'medical'::character varying,
    is_active boolean DEFAULT true,
    effective_from timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    effective_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT age_brackets_max_age_check CHECK ((max_age <= 120)),
    CONSTRAINT age_brackets_min_age_check CHECK ((min_age >= 0)),
    CONSTRAINT valid_age_range CHECK ((min_age <= max_age))
);


ALTER TABLE public.age_brackets OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 244912)
-- Name: agent_commissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_commissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    agent_id uuid NOT NULL,
    commission_rate numeric(5,2) NOT NULL,
    commission_amount numeric(15,2) NOT NULL,
    payment_status character varying(20) DEFAULT 'PENDING'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.agent_commissions OWNER TO postgres;

--
-- TOC entry 595 (class 1259 OID 249338)
-- Name: aggregate_covers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.aggregate_covers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    cover_name character varying(200) NOT NULL,
    cover_type character varying(50),
    attachment_point numeric(15,2) NOT NULL,
    limit_amount numeric(15,2) NOT NULL,
    premium numeric(15,2),
    premium_percentage numeric(8,4),
    cover_period_start date NOT NULL,
    cover_period_end date NOT NULL,
    reinstatements integer DEFAULT 0,
    reinstatement_premium_percentage numeric(8,4),
    subject_business text,
    exclusions text,
    geographical_scope text,
    currency character varying(3),
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.aggregate_covers OWNER TO postgres;

--
-- TOC entry 10529 (class 0 OID 0)
-- Dependencies: 595
-- Name: TABLE aggregate_covers; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.aggregate_covers IS 'Aggregate stop loss and excess covers for reinsurance';


--
-- TOC entry 246 (class 1259 OID 244932)
-- Name: ai_conversations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_conversations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    session_id character varying(100),
    model_id uuid,
    conversation_topic character varying(100),
    conversation_transcript jsonb,
    sentiment_progression jsonb,
    resolution_status character varying(30),
    customer_satisfaction_score integer,
    handoff_to_human boolean DEFAULT false,
    handoff_reason text,
    total_tokens_used integer,
    conversation_cost numeric(10,4),
    started_at timestamp with time zone DEFAULT now(),
    ended_at timestamp with time zone
);


ALTER TABLE public.ai_conversations OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 244940)
-- Name: ai_feature_usage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_feature_usage (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    module text,
    feature text,
    triggered_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ai_feature_usage OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 244947)
-- Name: ai_image_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_image_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid,
    image_url character varying(500) NOT NULL,
    analysis_type character varying(50),
    detected_objects jsonb,
    damage_assessment jsonb,
    confidence_score numeric(5,4),
    processing_time_ms integer,
    human_verification_required boolean DEFAULT false,
    verified_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ai_image_analysis OWNER TO postgres;

--
-- TOC entry 535 (class 1259 OID 247771)
-- Name: ai_ocr_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_ocr_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid,
    extracted_text text,
    confidence_score double precision,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ai_ocr_results OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 244955)
-- Name: ai_pricing_traces; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_pricing_traces (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid,
    model_version character varying(50),
    input_parameters jsonb,
    output_recommendation jsonb,
    confidence_score numeric(5,4),
    processing_time_ms integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ai_pricing_traces OWNER TO postgres;

--
-- TOC entry 568 (class 1259 OID 248831)
-- Name: ai_task_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_task_templates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_name character varying(200) NOT NULL,
    task_type character varying(50) NOT NULL,
    prompt_template text NOT NULL,
    model_parameters jsonb,
    expected_output_format jsonb,
    is_active boolean DEFAULT true,
    usage_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid NOT NULL
);


ALTER TABLE public.ai_task_templates OWNER TO postgres;

--
-- TOC entry 10530 (class 0 OID 0)
-- Dependencies: 568
-- Name: TABLE ai_task_templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.ai_task_templates IS 'Reusable AI task templates for automation workflows';


--
-- TOC entry 534 (class 1259 OID 247761)
-- Name: ai_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_type character varying(100) NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    input_source text,
    output_result text,
    error_log text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    related_entity_type character varying(100),
    related_entity_id uuid
);


ALTER TABLE public.ai_tasks OWNER TO postgres;

--
-- TOC entry 536 (class 1259 OID 247785)
-- Name: ai_utils; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_utils (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    content text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ai_utils OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 244962)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 244965)
-- Name: api_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.api_keys (
    key_name character varying(100) NOT NULL,
    api_key_hash character varying(255) NOT NULL,
    user_id uuid,
    permissions jsonb,
    rate_limit_per_hour integer DEFAULT 1000,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true,
    last_used timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.api_keys OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 244974)
-- Name: api_rate_limits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.api_rate_limits (
    api_key_id uuid,
    endpoint_pattern character varying(200),
    requests_per_second integer DEFAULT 10,
    requests_per_minute integer DEFAULT 600,
    requests_per_hour integer DEFAULT 36000,
    requests_per_day integer DEFAULT 864000,
    burst_limit integer DEFAULT 50,
    burst_window_seconds integer DEFAULT 60,
    current_second_count integer DEFAULT 0,
    current_minute_count integer DEFAULT 0,
    current_hour_count integer DEFAULT 0,
    current_day_count integer DEFAULT 0,
    second_reset_at timestamp with time zone DEFAULT now(),
    minute_reset_at timestamp with time zone DEFAULT now(),
    hour_reset_at timestamp with time zone DEFAULT now(),
    day_reset_at timestamp with time zone DEFAULT now(),
    violations_count integer DEFAULT 0,
    last_violation_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.api_rate_limits OWNER TO postgres;

--
-- TOC entry 583 (class 1259 OID 249051)
-- Name: app_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_versions (
    id uuid NOT NULL,
    platform character varying(50),
    version_number character varying(20),
    release_notes text,
    release_date date
);


ALTER TABLE public.app_versions OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 244995)
-- Name: ar_damage_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ar_damage_assessments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    claim_id uuid,
    app_id uuid,
    assessor_id uuid,
    session_id character varying(100),
    ar_session_data jsonb,
    captured_images jsonb,
    damage_measurements jsonb,
    repair_estimates jsonb,
    session_duration_minutes integer,
    accuracy_score numeric(3,2),
    quality_rating integer,
    session_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ar_damage_assessments OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 245002)
-- Name: ar_vr_applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ar_vr_applications (
    app_name character varying(100) NOT NULL,
    platform_type character varying(30),
    use_case character varying(50),
    supported_devices jsonb,
    minimum_specifications jsonb,
    app_version character varying(20),
    download_url character varying(500),
    features jsonb,
    pricing_model jsonb,
    is_production_ready boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ar_vr_applications OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 245010)
-- Name: archived_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.archived_policies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    original_policy_id uuid,
    policy_number character varying(50) NOT NULL,
    policy_data jsonb NOT NULL,
    related_data jsonb,
    archival_reason character varying(100),
    archived_by integer,
    archived_at timestamp with time zone DEFAULT now() NOT NULL,
    retention_period_years integer,
    legal_hold boolean DEFAULT false,
    legal_hold_reason text,
    destruction_date date,
    access_level character varying(30) DEFAULT 'restricted'::character varying,
    last_accessed timestamp with time zone,
    access_count integer DEFAULT 0,
    data_hash character varying(64),
    compression_ratio numeric(5,2),
    search_keywords text[],
    business_tags jsonb,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.archived_policies OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 245021)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    table_name text,
    record_id text,
    action text,
    performed_by uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    CONSTRAINT audit_logs_action_check CHECK ((action = ANY (ARRAY['insert'::text, 'update'::text, 'delete'::text])))
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- TOC entry 531 (class 1259 OID 247690)
-- Name: audit_logs_template; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs_template (
    table_name text,
    record_id text,
    action text,
    performed_by uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    CONSTRAINT audit_logs_action_check CHECK ((action = ANY (ARRAY['insert'::text, 'update'::text, 'delete'::text])))
);


ALTER TABLE public.audit_logs_template OWNER TO postgres;

--
-- TOC entry 586 (class 1259 OID 249084)
-- Name: audit_trail_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_trail_events (
    id uuid NOT NULL,
    entity_type character varying(50),
    entity_id uuid,
    action character varying(50),
    performed_by uuid,
    performed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text
);


ALTER TABLE public.audit_trail_events OWNER TO postgres;

--
-- TOC entry 590 (class 1259 OID 249209)
-- Name: automation_workflows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.automation_workflows (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_name character varying(200) NOT NULL,
    workflow_type character varying(50),
    process_steps jsonb,
    trigger_conditions jsonb,
    automation_level character varying(20),
    success_rate numeric(5,2),
    time_saved_minutes integer,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.automation_workflows OWNER TO postgres;

--
-- TOC entry 601 (class 1259 OID 250013)
-- Name: behavior_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.behavior_scores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    device_id uuid,
    score_type character varying(50),
    score_value numeric(5,2),
    score_period_start date,
    score_period_end date,
    contributing_factors jsonb,
    improvement_suggestions jsonb,
    discount_eligibility boolean DEFAULT false,
    discount_percentage numeric(5,2),
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.behavior_scores OWNER TO postgres;

--
-- TOC entry 554 (class 1259 OID 248443)
-- Name: benefit_alert_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_alert_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_benefit_usage_id uuid NOT NULL,
    member_id uuid NOT NULL,
    alert_type character varying(50) NOT NULL,
    threshold_percentage numeric(5,2),
    alert_message text NOT NULL,
    alert_message_ar text,
    delivery_channels character varying(100)[],
    sent_at timestamp with time zone DEFAULT now(),
    email_sent boolean DEFAULT false,
    sms_sent boolean DEFAULT false,
    push_sent boolean DEFAULT false,
    portal_notification_sent boolean DEFAULT false,
    member_acknowledged boolean DEFAULT false,
    acknowledged_at timestamp with time zone,
    member_response text,
    alert_status character varying(30) DEFAULT 'pending'::character varying,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    CONSTRAINT valid_alert_type CHECK (((alert_type)::text = ANY ((ARRAY['threshold_50'::character varying, 'threshold_80'::character varying, 'threshold_90'::character varying, 'exhausted'::character varying, 'renewal_reminder'::character varying, 'limit_increase_available'::character varying])::text[])))
);


ALTER TABLE public.benefit_alert_logs OWNER TO postgres;

--
-- TOC entry 10531 (class 0 OID 0)
-- Dependencies: 554
-- Name: TABLE benefit_alert_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_alert_logs IS 'Log of all benefit-related alerts sent to members';


--
-- TOC entry 542 (class 1259 OID 247968)
-- Name: benefit_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_categories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    name_ar character varying(200),
    description text,
    description_ar text,
    icon character varying(50),
    display_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.benefit_categories OWNER TO postgres;

--
-- TOC entry 10532 (class 0 OID 0)
-- Dependencies: 542
-- Name: TABLE benefit_categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_categories IS 'Categories for organizing insurance benefits (Medical, Dental, etc.)';


--
-- TOC entry 549 (class 1259 OID 248127)
-- Name: benefit_change_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_change_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    benefit_schedule_id uuid,
    change_type character varying(50) NOT NULL,
    table_name character varying(100) NOT NULL,
    record_id uuid,
    old_values jsonb,
    new_values jsonb,
    changed_fields text[],
    change_reason character varying(200),
    change_source character varying(50) DEFAULT 'manual'::character varying,
    changed_at timestamp with time zone DEFAULT now(),
    changed_by uuid NOT NULL,
    ip_address inet,
    user_agent text
);


ALTER TABLE public.benefit_change_log OWNER TO postgres;

--
-- TOC entry 10533 (class 0 OID 0)
-- Dependencies: 549
-- Name: TABLE benefit_change_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_change_log IS 'Audit log for all changes to benefit-related data';


--
-- TOC entry 545 (class 1259 OID 248035)
-- Name: benefit_conditions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_conditions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    benefit_schedule_id uuid NOT NULL,
    condition_type character varying(50) NOT NULL,
    condition_operator character varying(20),
    condition_value jsonb NOT NULL,
    condition_group character varying(50) DEFAULT 'default'::character varying,
    group_operator character varying(10) DEFAULT 'AND'::character varying,
    priority_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.benefit_conditions OWNER TO postgres;

--
-- TOC entry 10534 (class 0 OID 0)
-- Dependencies: 545
-- Name: TABLE benefit_conditions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_conditions IS 'Conditions that apply to specific benefits (age, gender, diagnosis, etc.)';


--
-- TOC entry 546 (class 1259 OID 248054)
-- Name: benefit_preapproval_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_preapproval_rules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    benefit_schedule_id uuid NOT NULL,
    provider_type character varying(100),
    service_category character varying(100),
    threshold_amount numeric(15,2),
    threshold_type character varying(20) DEFAULT 'amount'::character varying,
    always_required boolean DEFAULT false,
    auto_approve_below_threshold boolean DEFAULT false,
    approval_workflow character varying(100),
    effective_date date DEFAULT CURRENT_DATE,
    expiry_date date,
    notes text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.benefit_preapproval_rules OWNER TO postgres;

--
-- TOC entry 10535 (class 0 OID 0)
-- Dependencies: 546
-- Name: TABLE benefit_preapproval_rules; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_preapproval_rules IS 'Rules defining when preapproval is required for benefits';


--
-- TOC entry 544 (class 1259 OID 248018)
-- Name: benefit_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.benefit_translations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    benefit_schedule_id uuid NOT NULL,
    language_code character varying(5) NOT NULL,
    translated_name character varying(200),
    translated_description text,
    translated_disclaimer text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid
);


ALTER TABLE public.benefit_translations OWNER TO postgres;

--
-- TOC entry 10536 (class 0 OID 0)
-- Dependencies: 544
-- Name: TABLE benefit_translations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.benefit_translations IS 'Multilingual translations for benefit names and descriptions';


--
-- TOC entry 607 (class 1259 OID 250134)
-- Name: bi_dashboard_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bi_dashboard_cache (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    widget_id uuid,
    cache_key character varying(500),
    cached_data jsonb,
    cached_at timestamp without time zone DEFAULT now(),
    expires_at timestamp without time zone,
    is_valid boolean DEFAULT true
);


ALTER TABLE public.bi_dashboard_cache OWNER TO postgres;

--
-- TOC entry 605 (class 1259 OID 250107)
-- Name: bi_dashboards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bi_dashboards (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dashboard_name character varying(200) NOT NULL,
    dashboard_type character varying(50),
    layout_config jsonb,
    refresh_frequency character varying(20) DEFAULT 'hourly'::character varying,
    access_permissions jsonb,
    filters_config jsonb,
    data_sources jsonb,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.bi_dashboards OWNER TO postgres;

--
-- TOC entry 606 (class 1259 OID 250118)
-- Name: bi_widgets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bi_widgets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dashboard_id uuid,
    widget_name character varying(200),
    widget_type character varying(50),
    data_query text,
    visualization_config jsonb,
    position_config jsonb,
    refresh_interval integer DEFAULT 300,
    cache_duration integer DEFAULT 3600,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.bi_widgets OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 245029)
-- Name: billing_cycles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.billing_cycles (
    cycle_name character varying(50) NOT NULL,
    cycle_months integer NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.billing_cycles OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 245037)
-- Name: billing_statements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.billing_statements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type text,
    entity_id uuid,
    billing_period_start date,
    billing_period_end date,
    total_due numeric(14,2),
    status text DEFAULT 'draft'::text,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT billing_statements_entity_type_check CHECK ((entity_type = ANY (ARRAY['policy'::text, 'group'::text, 'company'::text]))),
    CONSTRAINT billing_statements_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'sent'::text, 'paid'::text, 'overdue'::text])))
);


ALTER TABLE public.billing_statements OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 245047)
-- Name: blockchain_networks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blockchain_networks (
    network_name character varying(50) NOT NULL,
    network_id uuid,
    rpc_endpoint character varying(200),
    explorer_url character varying(200),
    native_currency character varying(10),
    gas_price_gwei numeric(10,2),
    is_testnet boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.blockchain_networks OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 245054)
-- Name: blockchain_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blockchain_transactions (
    transaction_hash character varying(66) NOT NULL,
    smart_contract_id uuid,
    from_address character varying(42),
    to_address character varying(42),
    value numeric(28,18),
    gas_used bigint,
    gas_price_gwei numeric(10,2),
    transaction_fee numeric(28,18),
    block_number bigint,
    status character varying(30) DEFAULT 'pending'::character varying,
    transaction_data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    confirmed_at timestamp with time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.blockchain_transactions OWNER TO postgres;

--
-- TOC entry 596 (class 1259 OID 249354)
-- Name: bordereau_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bordereau_reports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    report_period_start date NOT NULL,
    report_period_end date NOT NULL,
    report_type character varying(50),
    total_premium numeric(15,2) DEFAULT 0,
    total_claims numeric(15,2) DEFAULT 0,
    ceded_premium numeric(15,2) DEFAULT 0,
    ceded_claims numeric(15,2) DEFAULT 0,
    commission numeric(15,2) DEFAULT 0,
    profit_commission numeric(15,2) DEFAULT 0,
    balance_due numeric(15,2),
    report_data jsonb,
    submission_date date,
    due_date date,
    status character varying(20) DEFAULT 'draft'::character varying,
    submitted_by uuid,
    acknowledged_by_reinsurer boolean DEFAULT false,
    acknowledgment_date date,
    disputes jsonb,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.bordereau_reports OWNER TO postgres;

--
-- TOC entry 10537 (class 0 OID 0)
-- Dependencies: 596
-- Name: TABLE bordereau_reports; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.bordereau_reports IS 'Detailed reporting to reinsurers on ceded business';


--
-- TOC entry 591 (class 1259 OID 249218)
-- Name: bot_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bot_executions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    execution_start timestamp without time zone,
    execution_end timestamp without time zone,
    status character varying(20),
    records_processed integer,
    errors_encountered jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.bot_executions OWNER TO postgres;

--
-- TOC entry 563 (class 1259 OID 248687)
-- Name: broker_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.broker_assignments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    broker_id uuid NOT NULL,
    company_id uuid,
    group_id uuid,
    policy_id uuid,
    assignment_type character varying(50) NOT NULL,
    effective_date date DEFAULT CURRENT_DATE,
    expiry_date date,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid
);


ALTER TABLE public.broker_assignments OWNER TO postgres;

--
-- TOC entry 562 (class 1259 OID 248664)
-- Name: brokers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brokers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    broker_code character varying(50) NOT NULL,
    broker_name character varying(200) NOT NULL,
    contact_person character varying(150),
    email character varying(150),
    phone character varying(50),
    address text,
    license_number character varying(100),
    license_expiry date,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.brokers OWNER TO postgres;

--
-- TOC entry 10538 (class 0 OID 0)
-- Dependencies: 562
-- Name: TABLE brokers; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.brokers IS 'Insurance broker/agent master data';


--
-- TOC entry 584 (class 1259 OID 249058)
-- Name: browser_fingerprints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.browser_fingerprints (
    id uuid NOT NULL,
    user_id uuid,
    fingerprint text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.browser_fingerprints OWNER TO postgres;

--
-- TOC entry 634 (class 1259 OID 250515)
-- Name: business_intelligence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_intelligence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    analysis_name character varying(200) NOT NULL,
    analysis_type character varying(50),
    analysis_period_start date,
    analysis_period_end date,
    data_sources jsonb,
    key_metrics jsonb,
    insights jsonb,
    recommendations jsonb,
    analysis_status character varying(30) DEFAULT 'completed'::character varying,
    analysis_method character varying(50),
    confidence_score numeric(3,2),
    business_impact_score numeric(3,2),
    stakeholders jsonb,
    refresh_frequency character varying(20) DEFAULT 'monthly'::character varying,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    real_time_metrics jsonb DEFAULT '{}'::jsonb,
    dashboard_subscriptions jsonb DEFAULT '{}'::jsonb,
    alert_configurations jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.business_intelligence OWNER TO postgres;

--
-- TOC entry 10539 (class 0 OID 0)
-- Dependencies: 634
-- Name: TABLE business_intelligence; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.business_intelligence IS 'Business intelligence and analytics data storage with intelligent module support';


--
-- TOC entry 10540 (class 0 OID 0)
-- Dependencies: 634
-- Name: COLUMN business_intelligence.real_time_metrics; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.business_intelligence.real_time_metrics IS 'Real-time KPIs and metrics configurations for live dashboards';


--
-- TOC entry 10541 (class 0 OID 0)
-- Dependencies: 634
-- Name: COLUMN business_intelligence.dashboard_subscriptions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.business_intelligence.dashboard_subscriptions IS 'User subscriptions and notification preferences for dashboard updates';


--
-- TOC entry 10542 (class 0 OID 0)
-- Dependencies: 634
-- Name: COLUMN business_intelligence.alert_configurations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.business_intelligence.alert_configurations IS 'Threshold-based alert configurations for business metrics';


--
-- TOC entry 261 (class 1259 OID 245062)
-- Name: business_processes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_processes (
    process_name character varying(100) NOT NULL,
    process_category character varying(50),
    version character varying(20) DEFAULT '1.0'::character varying,
    description text,
    process_definition jsonb,
    input_requirements jsonb,
    output_specifications jsonb,
    sla_hours integer,
    escalation_rules jsonb,
    is_active boolean DEFAULT true,
    created_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.business_processes OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 245071)
-- Name: campaign_performance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.campaign_performance (
    campaign_id uuid,
    reporting_date date DEFAULT CURRENT_DATE,
    impressions bigint DEFAULT 0,
    reach integer DEFAULT 0,
    frequency numeric(4,2) DEFAULT 0,
    clicks integer DEFAULT 0,
    click_through_rate numeric(6,4) DEFAULT 0,
    opens integer DEFAULT 0,
    open_rate numeric(6,4) DEFAULT 0,
    conversions integer DEFAULT 0,
    conversion_rate numeric(6,4) DEFAULT 0,
    revenue numeric(15,2) DEFAULT 0,
    cost_per_conversion numeric(15,2) DEFAULT 0,
    return_on_ad_spend numeric(8,4) DEFAULT 0,
    new_customers_acquired integer DEFAULT 0,
    customers_retained integer DEFAULT 0,
    customer_lifetime_value_impact numeric(15,2) DEFAULT 0,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.campaign_performance OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 245091)
-- Name: carbon_emission_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carbon_emission_sources (
    source_name character varying(100) NOT NULL,
    emission_scope integer,
    category character varying(100),
    calculation_methodology character varying(100),
    emission_factor numeric(10,6),
    unit_of_measure character varying(50),
    data_quality_rating character varying(20),
    update_frequency character varying(30),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.carbon_emission_sources OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 245096)
-- Name: carbon_emissions_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carbon_emissions_tracking (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid,
    emission_source_id uuid,
    measurement_period_start date NOT NULL,
    measurement_period_end date,
    activity_quantity numeric(15,4),
    emission_factor_used numeric(10,6),
    total_emissions_kgco2e numeric(15,4),
    verification_status character varying(30),
    offset_credits_applied numeric(15,4),
    net_emissions numeric(15,4),
    data_source character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.carbon_emissions_tracking OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 245101)
-- Name: cards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cards (
    card_number character varying(30) NOT NULL,
    policy_id uuid,
    member_id uuid,
    plan_id uuid,
    company_id uuid,
    effective_date date,
    expiry_date date,
    status character varying(20) DEFAULT 'active'::character varying,
    qr_code_data text,
    qr_code_url character varying(500),
    card_design_url character varying(500),
    enabled boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.cards OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 245127)
-- Name: catastrophe_detection_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.catastrophe_detection_models (
    model_name character varying(100) NOT NULL,
    detection_type character varying(50),
    input_data_types jsonb,
    model_architecture character varying(50),
    accuracy_metrics jsonb,
    false_positive_rate numeric(6,4),
    false_negative_rate numeric(6,4),
    processing_time_seconds integer,
    geographical_coverage public.geometry(MultiPolygon,4326),
    is_real_time boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.catastrophe_detection_models OWNER TO postgres;

--
-- TOC entry 594 (class 1259 OID 249328)
-- Name: catastrophe_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.catastrophe_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_name character varying(100) NOT NULL,
    vendor character varying(100),
    model_version character varying(50),
    peril_type character varying(50) NOT NULL,
    geographic_region character varying(100),
    model_resolution character varying(50),
    currency character varying(3),
    model_data jsonb,
    annual_aggregate_exceedance jsonb,
    occurrence_exceedance jsonb,
    calibration_date date,
    last_updated date,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.catastrophe_models OWNER TO postgres;

--
-- TOC entry 10543 (class 0 OID 0)
-- Dependencies: 594
-- Name: TABLE catastrophe_models; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.catastrophe_models IS 'CAT risk models for natural disasters and catastrophic events';


--
-- TOC entry 619 (class 1259 OID 250304)
-- Name: chaos_experiment_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chaos_experiment_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    experiment_id uuid,
    run_started_at timestamp without time zone,
    run_completed_at timestamp without time zone,
    run_status character varying(30),
    chaos_applied_successfully boolean,
    system_impact_metrics jsonb,
    resilience_score numeric(3,2),
    issues_discovered jsonb,
    recovery_time_seconds integer,
    success_criteria_met boolean,
    lessons_learned text,
    improvements_identified jsonb,
    follow_up_actions jsonb,
    executed_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.chaos_experiment_runs OWNER TO postgres;

--
-- TOC entry 618 (class 1259 OID 250293)
-- Name: chaos_experiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chaos_experiments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    experiment_name character varying(200) NOT NULL,
    experiment_type character varying(50),
    target_system character varying(100),
    chaos_action character varying(100),
    experiment_parameters jsonb,
    hypothesis text,
    success_criteria jsonb,
    blast_radius character varying(20) DEFAULT 'small'::character varying,
    rollback_plan text,
    safety_checks jsonb,
    schedule_config jsonb,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.chaos_experiments OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 245135)
-- Name: chat_contexts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_contexts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    session_id character varying(100),
    context_type character varying(50),
    context_summary text,
    key_entities jsonb,
    sentiment_history jsonb,
    intent_progression jsonb,
    short_term_memory jsonb,
    long_term_memory jsonb,
    episodic_memory jsonb,
    communication_style jsonb,
    knowledge_level character varying(20),
    interests_and_concerns jsonb,
    last_interaction timestamp with time zone,
    context_strength numeric(3,2),
    decay_rate numeric(5,4),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    user_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.chat_contexts OWNER TO postgres;

--
-- TOC entry 270 (class 1259 OID 245143)
-- Name: churn_predictions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.churn_predictions (
    member_id uuid,
    prediction_date date DEFAULT CURRENT_DATE,
    churn_probability numeric(5,4),
    risk_level public.risk_level,
    contributing_factors jsonb,
    recommended_actions jsonb,
    model_version character varying(20),
    prediction_horizon_days integer DEFAULT 90,
    confidence_score numeric(3,2),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.churn_predictions OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 245152)
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    name_en character varying(100) NOT NULL,
    country_id uuid,
    geom public.geometry(Point,4326),
    postal_code character varying,
    region_id uuid,
    is_active boolean DEFAULT true,
    name_ar character varying(255),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- TOC entry 555 (class 1259 OID 248470)
-- Name: claim_action_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_action_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    claim_id uuid NOT NULL,
    action_type character varying(50) NOT NULL,
    action_description text NOT NULL,
    previous_status character varying(50),
    new_status character varying(50),
    previous_amount numeric(15,2),
    new_amount numeric(15,2),
    amount_difference numeric(15,2),
    supporting_documents jsonb,
    internal_notes text,
    member_visible_notes text,
    reason_code character varying(50),
    requires_approval boolean DEFAULT false,
    approved_by uuid,
    approval_date timestamp with time zone,
    approval_notes text,
    triggered_by character varying(50) DEFAULT 'manual'::character varying,
    rule_id uuid,
    confidence_score numeric(5,4),
    action_taken_at timestamp with time zone DEFAULT now(),
    action_taken_by uuid NOT NULL,
    ip_address inet,
    user_agent text,
    CONSTRAINT valid_action_type CHECK (((action_type)::text = ANY ((ARRAY['status_change'::character varying, 'amount_adjustment'::character varying, 'document_added'::character varying, 'note_added'::character varying, 'approval_granted'::character varying, 'approval_denied'::character varying, 'reassignment'::character varying, 'escalation'::character varying, 'fraud_flag_added'::character varying, 'fraud_flag_removed'::character varying, 'payment_processed'::character varying])::text[])))
);


ALTER TABLE public.claim_action_logs OWNER TO postgres;

--
-- TOC entry 10544 (class 0 OID 0)
-- Dependencies: 555
-- Name: TABLE claim_action_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.claim_action_logs IS 'Detailed audit trail of all claim processing actions';


--
-- TOC entry 567 (class 1259 OID 248809)
-- Name: claim_approvers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_approvers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    claim_type character varying(50) NOT NULL,
    min_amount numeric(15,2) DEFAULT 0,
    max_amount numeric(15,2),
    approver_role character varying(50) NOT NULL,
    approval_level integer DEFAULT 1,
    created_at timestamp with time zone DEFAULT now(),
    is_active boolean DEFAULT true
);


ALTER TABLE public.claim_approvers OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 245159)
-- Name: claim_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_assessments (
    claim_id uuid,
    assessor_id uuid,
    assessment_type character varying(50),
    assessment_date date DEFAULT CURRENT_DATE,
    damage_description text,
    estimated_cost numeric(15,2),
    recommended_action character varying(100),
    photos jsonb,
    report_file_path character varying(500),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.claim_assessments OWNER TO postgres;

--
-- TOC entry 566 (class 1259 OID 248786)
-- Name: claim_checklists; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_checklists (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    claim_type character varying(50) NOT NULL,
    checklist_item text NOT NULL,
    is_mandatory boolean DEFAULT true,
    display_order integer DEFAULT 0,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    is_active boolean DEFAULT true
);


ALTER TABLE public.claim_checklists OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 245167)
-- Name: claim_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_documents (
    claim_id uuid,
    document_type character varying(50),
    file_name character varying(255),
    file_path character varying(500),
    file_size integer,
    mime_type character varying(100),
    uploaded_by uuid,
    is_verified boolean DEFAULT false,
    verification_notes text,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.claim_documents OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 245175)
-- Name: claim_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claim_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_id uuid NOT NULL,
    insurance_type character varying(50) NOT NULL,
    claim_date timestamp with time zone NOT NULL,
    claim_amount numeric(15,2) NOT NULL,
    claim_type character varying(50) NOT NULL,
    description text,
    status character varying(20) DEFAULT 'PENDING'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT claim_history_status_check CHECK (((status)::text = ANY (ARRAY[('PENDING'::character varying)::text, ('APPROVED'::character varying)::text, ('DENIED'::character varying)::text, ('PAID'::character varying)::text])))
);


ALTER TABLE public.claim_history OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 244918)
-- Name: claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.claims (
    claim_number character varying(30) NOT NULL,
    card_id uuid,
    policy_id uuid,
    claim_type public.claimtypeenum NOT NULL,
    status public.claimstatusenum DEFAULT 'pending'::public.claimstatusenum,
    incident_date date,
    reported_date date DEFAULT CURRENT_DATE,
    description text,
    amount numeric(15,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    location public.geometry(Point,4326),
    assigned_adjuster uuid,
    priority character varying(20) DEFAULT 'normal'::character varying,
    fraud_indicators jsonb,
    settlement_amount numeric(15,2),
    settlement_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    provider_id uuid,
    claim_source text DEFAULT 'TPA'::text,
    imported_at timestamp without time zone DEFAULT now(),
    import_batch_id uuid,
    member_id uuid,
    deleted_at timestamp without time zone,
    metadata jsonb,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT chk_claims_amount_positive CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.claims OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 245185)
-- Name: climate_risk_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.climate_risk_assessments (
    company_id uuid,
    scenario_id uuid,
    assessment_date date DEFAULT CURRENT_DATE,
    physical_risk_score numeric(5,2),
    transition_risk_score numeric(5,2),
    overall_climate_risk numeric(5,2),
    financial_impact_estimates jsonb,
    adaptation_strategies jsonb,
    stress_test_results jsonb,
    disclosure_requirements jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.climate_risk_assessments OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 245193)
-- Name: climate_scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.climate_scenarios (
    scenario_name character varying(100) NOT NULL,
    temperature_increase_celsius numeric(4,2),
    time_horizon_years integer,
    probability_percentage numeric(5,2),
    scenario_description text,
    source_organization character varying(100),
    last_updated date,
    scenario_data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.climate_scenarios OWNER TO postgres;

--
-- TOC entry 580 (class 1259 OID 249019)
-- Name: cms_pages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cms_pages (
    id uuid NOT NULL,
    slug character varying(100),
    title character varying(200),
    body text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.cms_pages OWNER TO postgres;

--
-- TOC entry 277 (class 1259 OID 245200)
-- Name: cohort_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cohort_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cohort_definition_id uuid,
    cohort_period date NOT NULL,
    analysis_period date,
    cohort_size integer,
    active_customers integer,
    retention_rate numeric(5,4),
    revenue_per_customer numeric(15,2),
    total_revenue numeric(15,2),
    cumulative_revenue numeric(15,2),
    average_order_value numeric(15,2),
    purchase_frequency numeric(8,4),
    customer_lifetime_value numeric(15,2),
    engagement_metrics jsonb,
    product_usage_patterns jsonb,
    channel_preferences jsonb,
    calculated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cohort_analysis OWNER TO postgres;

--
-- TOC entry 278 (class 1259 OID 245207)
-- Name: cohort_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cohort_definitions (
    cohort_name character varying(100) NOT NULL,
    cohort_type character varying(50),
    definition_criteria jsonb,
    time_period character varying(20),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cohort_definitions OWNER TO postgres;

--
-- TOC entry 557 (class 1259 OID 248530)
-- Name: collections_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collections_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid NOT NULL,
    invoice_id uuid,
    member_id uuid NOT NULL,
    collection_stage character varying(50) NOT NULL,
    days_overdue integer NOT NULL,
    outstanding_amount numeric(15,2) NOT NULL,
    action_type character varying(50) NOT NULL,
    communication_channel character varying(30),
    communication_sent_at timestamp with time zone DEFAULT now(),
    message_template_used character varying(100),
    personalized_message text,
    recipient_contact_info jsonb,
    member_responded boolean DEFAULT false,
    response_received_at timestamp with time zone,
    response_type character varying(30),
    response_details text,
    payment_received boolean DEFAULT false,
    payment_amount numeric(15,2),
    payment_date date,
    payment_method character varying(50),
    next_action_scheduled character varying(50),
    next_action_date date,
    escalation_required boolean DEFAULT false,
    escalation_reason text,
    collection_status character varying(30) DEFAULT 'active'::character varying,
    resolution_date date,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid NOT NULL,
    updated_by uuid,
    CONSTRAINT valid_action_type CHECK (((action_type)::text = ANY ((ARRAY['email_reminder'::character varying, 'sms_reminder'::character varying, 'phone_call'::character varying, 'postal_letter'::character varying, 'legal_referral'::character varying, 'payment_plan_setup'::character varying])::text[]))),
    CONSTRAINT valid_amounts CHECK (((outstanding_amount > (0)::numeric) AND ((payment_amount IS NULL) OR (payment_amount >= (0)::numeric)))),
    CONSTRAINT valid_collection_stage CHECK (((collection_stage)::text = ANY ((ARRAY['first_reminder'::character varying, 'second_reminder'::character varying, 'final_notice'::character varying, 'pre_legal'::character varying, 'legal_action'::character varying, 'debt_collection'::character varying])::text[])))
);


ALTER TABLE public.collections_logs OWNER TO postgres;

--
-- TOC entry 10545 (class 0 OID 0)
-- Dependencies: 557
-- Name: TABLE collections_logs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.collections_logs IS 'Payment collection activities and member follow-up tracking';


--
-- TOC entry 279 (class 1259 OID 245215)
-- Name: commission_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commission_rules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid,
    agent_type text,
    commission_percent numeric(5,2),
    min_premium numeric(12,2),
    max_cap numeric(12,2),
    payment_type text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.commission_rules OWNER TO postgres;

--
-- TOC entry 280 (class 1259 OID 245222)
-- Name: commission_statements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commission_statements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_id uuid,
    period_start date,
    period_end date,
    total_commission numeric(12,2),
    status text DEFAULT 'pending'::text,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.commission_statements OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 245230)
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    name character varying(100) NOT NULL,
    registration_number character varying(50),
    tax_id character varying(50),
    email character varying(100),
    phone character varying(20),
    address text,
    postal_code character varying(20),
    website character varying(200),
    logo_url character varying(500),
    is_active boolean DEFAULT true,
    license_number character varying(50),
    license_expiry_date date,
    regulatory_rating character varying(20),
    solvency_ratio numeric(8,4),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    geom public.geometry(Point,4326),
    country_id uuid,
    state_id uuid,
    city_id uuid,
    default_language character varying(10) DEFAULT 'en'::character varying,
    theme_color character varying(20) DEFAULT '#0066cc'::character varying,
    timezone character varying(50) DEFAULT 'Asia/Beirut'::character varying,
    subscription_status character varying(20) DEFAULT 'active'::character varying,
    custom_domain character varying(255),
    notes text,
    region_id uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 245243)
-- Name: company_esg_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_esg_scores (
    company_id uuid,
    framework_id uuid,
    reporting_period_start date,
    reporting_period_end date,
    overall_esg_score numeric(5,2),
    environmental_score numeric(5,2),
    social_score numeric(5,2),
    governance_score numeric(5,2),
    detailed_scores jsonb,
    peer_comparison jsonb,
    improvement_areas jsonb,
    certification_level character varying(30),
    third_party_verified boolean DEFAULT false,
    verifier_organization character varying(100),
    calculated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.company_esg_scores OWNER TO postgres;

--
-- TOC entry 628 (class 1259 OID 250433)
-- Name: competitor_intelligence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competitor_intelligence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    competitor_name character varying(200),
    intelligence_type character varying(50),
    intelligence_summary text,
    data_sources jsonb,
    credibility_score numeric(3,2),
    competitive_threat_level character varying(20),
    potential_customer_impact jsonb,
    recommended_response jsonb,
    monitoring_priority character varying(20) DEFAULT 'normal'::character varying,
    intelligence_date timestamp without time zone,
    follow_up_required boolean DEFAULT false,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.competitor_intelligence OWNER TO postgres;

--
-- TOC entry 283 (class 1259 OID 245252)
-- Name: compliance_monitoring; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compliance_monitoring (
    company_id uuid,
    requirement_id uuid,
    monitoring_date date DEFAULT CURRENT_DATE,
    current_value numeric(15,4),
    threshold_value numeric(15,4),
    status character varying(30),
    variance_percentage numeric(5,2),
    remediation_plan text,
    target_date date,
    responsible_person uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.compliance_monitoring OWNER TO postgres;

--
-- TOC entry 284 (class 1259 OID 245260)
-- Name: computer_vision_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.computer_vision_models (
    model_name character varying(100) NOT NULL,
    model_type character varying(50),
    model_version character varying(20),
    accuracy_metrics jsonb,
    model_endpoints jsonb,
    training_dataset_info jsonb,
    inference_cost_per_request numeric(10,6),
    max_requests_per_second integer DEFAULT 100,
    is_production_ready boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.computer_vision_models OWNER TO postgres;

--
-- TOC entry 285 (class 1259 OID 245269)
-- Name: content_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.content_templates (
    template_name character varying(100) NOT NULL,
    content_type character varying(50),
    template_structure jsonb,
    personalization_rules jsonb,
    a_b_test_variants jsonb,
    performance_metrics jsonb,
    target_personas integer[],
    created_by uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.content_templates OWNER TO postgres;

--
-- TOC entry 286 (class 1259 OID 245277)
-- Name: conversation_memory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversation_memory (
    user_id uuid,
    memory_type character varying(50),
    memory_key character varying(200),
    memory_value jsonb,
    confidence_level numeric(3,2),
    source_conversation_id uuid,
    extraction_method character varying(30),
    validation_status character varying(20),
    first_mentioned timestamp with time zone,
    last_reinforced timestamp with time zone,
    reinforcement_count integer DEFAULT 1,
    contradiction_count integer DEFAULT 0,
    memory_strength numeric(5,4),
    decay_function character varying(20) DEFAULT 'exponential'::character varying,
    half_life_days integer DEFAULT 30,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.conversation_memory OWNER TO postgres;

--
-- TOC entry 287 (class 1259 OID 245289)
-- Name: conversational_ai_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversational_ai_models (
    model_name character varying(100) NOT NULL,
    model_type character varying(50),
    language_capabilities text[],
    domain_specialization character varying(50),
    context_window_size integer DEFAULT 4096,
    response_quality_score numeric(3,2),
    hallucination_rate numeric(5,4),
    api_endpoint character varying(200),
    cost_per_token numeric(12,8),
    is_production boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.conversational_ai_models OWNER TO postgres;

--
-- TOC entry 288 (class 1259 OID 245298)
-- Name: countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.countries (
    name character varying(100) NOT NULL,
    iso_code character varying(10) NOT NULL,
    phone_code character varying(10),
    is_active boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.countries OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 245303)
-- Name: coverage_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coverage_options (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    insurance_type character varying(50) NOT NULL,
    option_name character varying(255) NOT NULL,
    description text,
    base_price numeric(15,2) NOT NULL,
    pricing_formula text,
    is_optional boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.coverage_options OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 245311)
-- Name: coverages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coverages (
    name character varying(100) NOT NULL,
    description text,
    coverage_type character varying(50),
    maximum_amount numeric(15,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    type character varying,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.coverages OWNER TO postgres;

--
-- TOC entry 291 (class 1259 OID 245320)
-- Name: cpt_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cpt_codes (
    code character varying(50) NOT NULL,
    description text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cpt_codes OWNER TO postgres;

--
-- TOC entry 292 (class 1259 OID 245326)
-- Name: cryptographic_algorithms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cryptographic_algorithms (
    algorithm_name character varying(100) NOT NULL,
    algorithm_type character varying(50),
    quantum_resistant boolean DEFAULT false,
    key_size_bits integer,
    security_level integer,
    performance_benchmark jsonb,
    standardization_status character varying(30),
    implementation_library character varying(100),
    is_approved boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cryptographic_algorithms OWNER TO postgres;

--
-- TOC entry 293 (class 1259 OID 245335)
-- Name: cultural_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cultural_preferences (
    locale_code character varying(10),
    preference_category character varying(50),
    preference_key character varying(100),
    preference_value jsonb,
    cultural_notes text,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.cultural_preferences OWNER TO postgres;

--
-- TOC entry 574 (class 1259 OID 248919)
-- Name: custom_field_values; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.custom_field_values (
    id uuid NOT NULL,
    custom_field_id uuid,
    entity_id uuid NOT NULL,
    value text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.custom_field_values OWNER TO postgres;

--
-- TOC entry 573 (class 1259 OID 248910)
-- Name: custom_fields; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.custom_fields (
    id uuid NOT NULL,
    entity_type character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    label character varying(100),
    field_type character varying(50) DEFAULT 'text'::character varying,
    is_required boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.custom_fields OWNER TO postgres;

--
-- TOC entry 592 (class 1259 OID 249232)
-- Name: customer_360_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_360_profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    unified_profile jsonb,
    segment_ids uuid[],
    lifetime_value numeric(15,2),
    churn_score numeric(5,4),
    next_best_action character varying(200),
    last_interaction timestamp without time zone,
    preference_profile jsonb,
    risk_profile jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.customer_360_profiles OWNER TO postgres;

--
-- TOC entry 294 (class 1259 OID 245342)
-- Name: customer_journey_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_journey_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    event_type character varying(50),
    event_name character varying(100),
    channel character varying(30),
    touchpoint character varying(100),
    event_data jsonb,
    session_id character varying(100),
    user_agent text,
    ip_address inet,
    conversion_value numeric(15,2),
    event_timestamp timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customer_journey_events OWNER TO postgres;

--
-- TOC entry 593 (class 1259 OID 249246)
-- Name: customer_journey_touchpoints; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_journey_touchpoints (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    customer_id uuid,
    touchpoint_type character varying(50),
    channel character varying(50),
    interaction_data jsonb,
    sentiment_score numeric(3,2),
    conversion_event boolean DEFAULT false,
    touchpoint_timestamp timestamp without time zone,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.customer_journey_touchpoints OWNER TO postgres;

--
-- TOC entry 295 (class 1259 OID 245349)
-- Name: customer_lifecycle_stages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_lifecycle_stages (
    stage_name character varying(50) NOT NULL,
    stage_description text,
    stage_criteria jsonb,
    typical_duration_days integer,
    next_stages integer[],
    actions jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_lifecycle_stages OWNER TO postgres;

--
-- TOC entry 296 (class 1259 OID 245356)
-- Name: customer_lifetime_value; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_lifetime_value (
    member_id uuid,
    calculation_date date DEFAULT CURRENT_DATE,
    historical_value numeric(15,2),
    predicted_value numeric(15,2),
    total_ltv numeric(15,2),
    confidence_interval jsonb,
    contributing_factors jsonb,
    model_version character varying(20),
    valid_until date,
    calculated_by character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_lifetime_value OWNER TO postgres;

--
-- TOC entry 297 (class 1259 OID 245364)
-- Name: customer_personas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_personas (
    persona_name character varying(100) NOT NULL,
    demographic_profile jsonb,
    behavioral_patterns jsonb,
    risk_tolerance character varying(30),
    product_preferences jsonb,
    channel_preferences jsonb,
    life_stage character varying(50),
    value_drivers jsonb,
    communication_style character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_personas OWNER TO postgres;

--
-- TOC entry 298 (class 1259 OID 245371)
-- Name: customer_risk_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_risk_profiles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_id uuid NOT NULL,
    insurance_type character varying(50) NOT NULL,
    risk_score numeric(5,2) DEFAULT 1.0,
    risk_factors jsonb,
    medical_conditions jsonb,
    lifestyle_factors jsonb,
    occupation_risk_level character varying(20),
    credit_based_insurance_score integer,
    last_assessed timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_risk_profiles OWNER TO postgres;

--
-- TOC entry 299 (class 1259 OID 245380)
-- Name: customer_segment_analytics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_segment_analytics (
    segment_id uuid,
    analysis_period_start date,
    analysis_period_end date,
    total_customers integer,
    new_customers integer,
    churned_customers integer,
    net_growth integer,
    total_revenue numeric(15,2),
    revenue_per_customer numeric(15,2),
    profit_margin numeric(5,4),
    customer_acquisition_cost numeric(15,2),
    avg_session_duration integer,
    avg_sessions_per_customer numeric(8,4),
    feature_adoption_rates jsonb,
    support_ticket_rate numeric(8,6),
    churn_risk_distribution jsonb,
    upsell_opportunity_score numeric(5,2),
    cross_sell_propensity jsonb,
    calculated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_segment_analytics OWNER TO postgres;

--
-- TOC entry 300 (class 1259 OID 245387)
-- Name: customer_segments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_segments (
    segment_name character varying(100) NOT NULL,
    segment_description text,
    segmentation_criteria jsonb,
    segment_type character varying(30),
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.customer_segments OWNER TO postgres;

--
-- TOC entry 301 (class 1259 OID 245395)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_code character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255),
    phone character varying(20),
    date_of_birth date,
    address jsonb,
    national_id character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 302 (class 1259 OID 245403)
-- Name: data_annotations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_annotations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dataset_id uuid,
    sample_id character varying(200),
    sample_path character varying(500),
    annotation_type character varying(50),
    annotations jsonb,
    confidence_score numeric(3,2),
    quality_rating integer,
    needs_review boolean DEFAULT false,
    is_validated boolean DEFAULT false,
    annotated_by uuid,
    annotation_time_seconds integer,
    annotation_method character varying(30),
    reviewed_by uuid,
    reviewed_at timestamp with time zone,
    review_comments text,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.data_annotations OWNER TO postgres;

--
-- TOC entry 303 (class 1259 OID 245412)
-- Name: data_exports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_exports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    report_name text,
    exported_by uuid,
    exported_at timestamp without time zone DEFAULT now(),
    format text DEFAULT 'xlsx'::text,
    filters jsonb,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.data_exports OWNER TO postgres;

--
-- TOC entry 304 (class 1259 OID 245420)
-- Name: data_import_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_import_logs (
    file_name text,
    imported_by uuid,
    rows_imported integer,
    import_time timestamp without time zone DEFAULT now(),
    status text,
    error_log text,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.data_import_logs OWNER TO postgres;

--
-- TOC entry 305 (class 1259 OID 245427)
-- Name: data_quality_checks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_checks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    rule_id uuid,
    check_date date DEFAULT CURRENT_DATE NOT NULL,
    total_records integer,
    failed_records integer,
    pass_percentage numeric(5,2),
    status character varying(20),
    error_details jsonb,
    sample_errors text[],
    execution_time_ms integer,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.data_quality_checks OWNER TO postgres;

--
-- TOC entry 306 (class 1259 OID 245435)
-- Name: data_quality_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_rules (
    rule_name character varying(100) NOT NULL,
    table_name character varying(100) NOT NULL,
    column_name character varying(100),
    rule_type character varying(30),
    rule_definition jsonb,
    severity character varying(20),
    threshold_percentage numeric(5,2) DEFAULT 95.0,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.data_quality_rules OWNER TO postgres;

--
-- TOC entry 307 (class 1259 OID 245444)
-- Name: data_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    request_type text,
    status text DEFAULT 'pending'::text,
    requested_at timestamp without time zone DEFAULT now(),
    processed_at timestamp without time zone,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.data_requests OWNER TO postgres;

--
-- TOC entry 308 (class 1259 OID 245452)
-- Name: decentralized_identities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.decentralized_identities (
    member_id uuid,
    did_identifier character varying(200) NOT NULL,
    did_document jsonb,
    verification_methods jsonb,
    service_endpoints jsonb,
    controllers text[],
    created_timestamp timestamp with time zone,
    updated_timestamp timestamp with time zone,
    revoked boolean DEFAULT false,
    revocation_reason text,
    blockchain_anchor jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.decentralized_identities OWNER TO postgres;

--
-- TOC entry 621 (class 1259 OID 250328)
-- Name: decision_universes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.decision_universes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    decision_name character varying(200) NOT NULL,
    decision_context text,
    universe_count integer DEFAULT 5,
    decision_parameters jsonb,
    evaluation_criteria jsonb,
    time_horizon_months integer DEFAULT 12,
    simulation_complexity character varying(20) DEFAULT 'medium'::character varying,
    stakeholders jsonb,
    decision_deadline date,
    status character varying(30) DEFAULT 'setup'::character varying,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.decision_universes OWNER TO postgres;

--
-- TOC entry 564 (class 1259 OID 248723)
-- Name: delegates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.delegates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    group_id uuid,
    delegate_name character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    phone character varying(50),
    "position" character varying(100),
    department character varying(100),
    permissions jsonb,
    is_primary boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.delegates OWNER TO postgres;

--
-- TOC entry 10546 (class 0 OID 0)
-- Dependencies: 564
-- Name: TABLE delegates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.delegates IS 'Corporate HR delegates authorized to manage group policies';


--
-- TOC entry 587 (class 1259 OID 249100)
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    parent_department_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- TOC entry 309 (class 1259 OID 245460)
-- Name: dependents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dependents (
    member_id uuid,
    full_name character varying(255) NOT NULL,
    full_name_ar character varying(255),
    gender character varying(10),
    date_of_birth date,
    relation character varying(50),
    national_id_number character varying(100),
    insurance_id_card_number character varying(100),
    photo_url text,
    has_card boolean DEFAULT false,
    coverage_level character varying(50),
    coverage_limit numeric(12,2),
    status character varying(50) DEFAULT 'active'::character varying,
    address text,
    address_ar text,
    notes text,
    is_active boolean DEFAULT true,
    is_test_account boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.dependents OWNER TO postgres;

--
-- TOC entry 614 (class 1259 OID 250236)
-- Name: digital_twin_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.digital_twin_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_name character varying(200) NOT NULL,
    twin_type character varying(50),
    model_scope jsonb,
    simulation_engine character varying(50),
    model_parameters jsonb,
    calibration_data jsonb,
    validation_metrics jsonb,
    update_frequency character varying(20) DEFAULT 'daily'::character varying,
    computational_complexity character varying(20),
    is_production_ready boolean DEFAULT false,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.digital_twin_models OWNER TO postgres;

--
-- TOC entry 310 (class 1259 OID 245472)
-- Name: discounts_promotions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.discounts_promotions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    discount_type character varying(20),
    discount_value numeric(10,4) NOT NULL,
    insurance_type character varying(50),
    applicable_to character varying(50),
    min_premium numeric(15,2),
    max_discount numeric(15,2),
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT discounts_promotions_discount_type_check CHECK (((discount_type)::text = ANY (ARRAY[('PERCENTAGE'::character varying)::text, ('FIXED_AMOUNT'::character varying)::text, ('MULTIPLIER'::character varying)::text])))
);


ALTER TABLE public.discounts_promotions OWNER TO postgres;

--
-- TOC entry 311 (class 1259 OID 245481)
-- Name: document_expiry_alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_expiry_alerts (
    document_id uuid,
    alert_sent_at timestamp without time zone DEFAULT now(),
    method text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_expiry_alerts OWNER TO postgres;

--
-- TOC entry 312 (class 1259 OID 245488)
-- Name: document_intelligence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_intelligence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid,
    nlp_model_id uuid,
    extracted_entities jsonb,
    sentiment_analysis jsonb,
    contract_clauses jsonb,
    risk_indicators jsonb,
    compliance_flags jsonb,
    confidence_scores jsonb,
    processing_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_intelligence OWNER TO postgres;

--
-- TOC entry 539 (class 1259 OID 247883)
-- Name: document_public_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_public_tokens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    public_token uuid DEFAULT gen_random_uuid() NOT NULL,
    qr_code_url text,
    expires_at timestamp without time zone,
    usage_limit integer DEFAULT 1,
    access_count integer DEFAULT 0,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    qr_style_id uuid
);


ALTER TABLE public.document_public_tokens OWNER TO postgres;

--
-- TOC entry 313 (class 1259 OID 245495)
-- Name: document_revisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_revisions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid,
    revision_number integer NOT NULL,
    version_label character varying(50),
    change_description text,
    change_type character varying(30),
    document_content bytea,
    content_hash character varying(64),
    file_size integer,
    mime_type character varying(100),
    changes_from_previous jsonb,
    author_id uuid,
    reviewer_id uuid,
    approval_status character varying(30) DEFAULT 'draft'::character varying,
    approval_date timestamp with time zone,
    approval_notes text,
    download_count integer DEFAULT 0,
    last_downloaded timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_revisions OWNER TO postgres;

--
-- TOC entry 537 (class 1259 OID 247857)
-- Name: document_signatures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_signatures (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    signer_id uuid NOT NULL,
    signer_type character varying(50) NOT NULL,
    signature_type character varying(50) DEFAULT 'e-signature'::character varying NOT NULL,
    signature_data text,
    signed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(50) DEFAULT 'signed'::character varying,
    notes text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_signatures OWNER TO postgres;

--
-- TOC entry 314 (class 1259 OID 245504)
-- Name: document_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_templates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    template_type text NOT NULL,
    design_version text DEFAULT 'v1'::text,
    content text NOT NULL,
    preview_image text,
    description text,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    is_active boolean DEFAULT true,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_templates OWNER TO postgres;

--
-- TOC entry 10547 (class 0 OID 0)
-- Dependencies: 314
-- Name: TABLE document_templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.document_templates IS 'Templates for generating insurance documents and certificates';


--
-- TOC entry 315 (class 1259 OID 245513)
-- Name: document_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_versions (
    document_id uuid,
    version_number integer,
    file_url text,
    uploaded_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.document_versions OWNER TO postgres;

--
-- TOC entry 316 (class 1259 OID 245520)
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    document_name character varying(255) NOT NULL,
    document_type character varying(100),
    file_path character varying(500),
    file_size integer,
    mime_type character varying(100),
    status public.docstatusenum DEFAULT 'pending'::public.docstatusenum,
    uploaded_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 630 (class 1259 OID 250457)
-- Name: employee_skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_skills (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    employee_id uuid,
    skill_id uuid,
    current_proficiency character varying(20),
    proficiency_score numeric(3,2),
    assessment_method character varying(50),
    last_assessed timestamp without time zone,
    assessment_validity_months integer DEFAULT 12,
    development_priority character varying(20) DEFAULT 'medium'::character varying,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.employee_skills OWNER TO postgres;

--
-- TOC entry 317 (class 1259 OID 245529)
-- Name: encryption_zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.encryption_zones (
    zone_name character varying(100) NOT NULL,
    classification_level character varying(30),
    encryption_algorithm_id uuid,
    key_rotation_interval_days integer DEFAULT 90,
    access_control_policy jsonb,
    compliance_requirements text[],
    geographic_restrictions jsonb,
    last_key_rotation timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.encryption_zones OWNER TO postgres;

--
-- TOC entry 318 (class 1259 OID 245537)
-- Name: endorsements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.endorsements (
    policy_id uuid,
    endorsement_number character varying(50),
    type character varying(50),
    effective_date date,
    details text,
    document_url text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    member_id uuid,
    status character varying(20) DEFAULT 'pending'::character varying,
    reason text,
    previous_value jsonb,
    new_value jsonb,
    approved_by uuid,
    approved_at timestamp without time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.endorsements OWNER TO postgres;

--
-- TOC entry 319 (class 1259 OID 245545)
-- Name: entities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entities (
    company_id uuid,
    entity_type_id uuid,
    name character varying(255) NOT NULL,
    code character varying(50),
    registration_number character varying(100),
    email character varying(255),
    phone character varying(30),
    contact_person character varying(255),
    contact_position character varying(100),
    address_line text,
    city_id uuid,
    region_id uuid,
    country_id uuid,
    postal_code character varying(20),
    latitude numeric(9,6),
    longitude numeric(9,6),
    is_active boolean DEFAULT true,
    is_blacklisted boolean DEFAULT false,
    notes text,
    created_by uuid,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    archived_at timestamp without time zone
);


ALTER TABLE public.entities OWNER TO postgres;

--
-- TOC entry 320 (class 1259 OID 245555)
-- Name: entity_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entity_types (
    company_id uuid,
    code character varying(50) NOT NULL,
    label character varying(100) NOT NULL,
    description text,
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.entity_types OWNER TO postgres;

--
-- TOC entry 321 (class 1259 OID 245565)
-- Name: esg_frameworks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.esg_frameworks (
    framework_name character varying(100) NOT NULL,
    version character varying(20),
    issuing_organization character varying(100),
    focus_area character varying(50),
    scoring_methodology jsonb,
    industry_applicability text[],
    mandatory_disclosure boolean DEFAULT false,
    effective_date date,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.esg_frameworks OWNER TO postgres;

--
-- TOC entry 322 (class 1259 OID 245573)
-- Name: exchange_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exchange_rates (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    base_currency character varying(3) NOT NULL,
    target_currency character varying(3) NOT NULL,
    exchange_rate numeric(12,6) NOT NULL,
    effective_date timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.exchange_rates OWNER TO postgres;

--
-- TOC entry 323 (class 1259 OID 245578)
-- Name: exclusions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exclusions (
    text text NOT NULL,
    type character varying(10) NOT NULL,
    notes text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cpt_code_id uuid,
    icd10_code_id uuid,
    motor_code_id uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT exclusions_type_check CHECK (((type)::text = ANY (ARRAY[('medical'::character varying)::text, ('motor'::character varying)::text])))
);


ALTER TABLE public.exclusions OWNER TO postgres;

--
-- TOC entry 324 (class 1259 OID 245588)
-- Name: external_data_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.external_data_sources (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    source_name character varying(255) NOT NULL,
    source_type character varying(50) NOT NULL,
    endpoint_url text,
    api_key_encrypted text,
    last_sync timestamp with time zone,
    sync_status character varying(20),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.external_data_sources OWNER TO postgres;

--
-- TOC entry 643 (class 1259 OID 250861)
-- Name: external_field_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.external_field_mappings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    integration_id uuid,
    internal_table text NOT NULL,
    internal_field text NOT NULL,
    external_field text NOT NULL,
    data_type text,
    transformation_rule text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.external_field_mappings OWNER TO postgres;

--
-- TOC entry 325 (class 1259 OID 245595)
-- Name: external_service_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.external_service_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    service_name character varying(100) NOT NULL,
    service_category character varying(50),
    endpoint_url character varying(500),
    check_method character varying(10) DEFAULT 'GET'::character varying,
    expected_status_code integer DEFAULT 200,
    timeout_seconds integer DEFAULT 30,
    current_status character varying(20),
    last_check_timestamp timestamp with time zone NOT NULL,
    response_time_ms integer,
    uptime_percentage numeric(5,2),
    avg_response_time_ms integer,
    error_rate numeric(5,4),
    alert_threshold_ms integer DEFAULT 5000,
    consecutive_failures integer DEFAULT 0,
    alert_sent boolean DEFAULT false,
    last_alert_sent timestamp with time zone,
    business_criticality character varying(20),
    affected_features jsonb,
    fallback_available boolean DEFAULT false,
    fallback_service character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.external_service_status OWNER TO postgres;

--
-- TOC entry 642 (class 1259 OID 250851)
-- Name: external_services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.external_services (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    system_type text,
    base_url text,
    api_version text,
    auth_type text,
    credentials jsonb,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.external_services OWNER TO postgres;

--
-- TOC entry 581 (class 1259 OID 249030)
-- Name: faq_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faq_entries (
    id uuid NOT NULL,
    question text,
    answer text,
    category character varying(100),
    language character varying(10),
    is_active boolean DEFAULT true
);


ALTER TABLE public.faq_entries OWNER TO postgres;

--
-- TOC entry 326 (class 1259 OID 245610)
-- Name: financial_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_accounts (
    account_code character varying(20) NOT NULL,
    account_name character varying(100) NOT NULL,
    account_type character varying(30),
    parent_account_id uuid,
    normal_balance character varying(10),
    is_active boolean DEFAULT true,
    company_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.financial_accounts OWNER TO postgres;

--
-- TOC entry 327 (class 1259 OID 245616)
-- Name: financial_periods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.financial_periods (
    company_id uuid,
    period_name character varying(50),
    period_type character varying(20),
    start_date date NOT NULL,
    end_date date NOT NULL,
    status character varying(20) DEFAULT 'open'::character varying,
    closed_by integer,
    closed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.financial_periods OWNER TO postgres;

--
-- TOC entry 328 (class 1259 OID 245622)
-- Name: fiscal_periods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fiscal_periods (
    period_name text NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    is_closed boolean DEFAULT false,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.fiscal_periods OWNER TO postgres;

--
-- TOC entry 329 (class 1259 OID 245629)
-- Name: forecasting_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forecasting_models (
    model_name character varying(100) NOT NULL,
    model_type character varying(50),
    target_metric_id uuid,
    model_parameters jsonb,
    training_period_start timestamp with time zone,
    training_period_end timestamp with time zone,
    validation_metrics jsonb,
    seasonal_patterns jsonb,
    trend_analysis jsonb,
    forecast_horizon_days integer DEFAULT 90,
    confidence_intervals boolean DEFAULT true,
    is_production boolean DEFAULT false,
    last_retrained timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.forecasting_models OWNER TO postgres;

--
-- TOC entry 330 (class 1259 OID 245639)
-- Name: forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forecasts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid,
    entity_type character varying(50),
    entity_id uuid,
    forecast_timestamp timestamp with time zone NOT NULL,
    predicted_value numeric(20,8),
    confidence_lower numeric(20,8),
    confidence_upper numeric(20,8),
    prediction_interval numeric(3,2),
    influencing_factors jsonb,
    scenario_assumptions jsonb,
    generated_at timestamp with time zone DEFAULT now(),
    actual_value numeric(20,8),
    forecast_accuracy numeric(5,4),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.forecasts OWNER TO postgres;

--
-- TOC entry 331 (class 1259 OID 245646)
-- Name: fraud_detection_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fraud_detection_models (
    model_name character varying(100) NOT NULL,
    model_type character varying(50),
    feature_set jsonb,
    model_weights bytea,
    threshold_config jsonb,
    false_positive_rate numeric(8,6),
    false_negative_rate numeric(8,6),
    last_retrained timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.fraud_detection_models OWNER TO postgres;

--
-- TOC entry 332 (class 1259 OID 245654)
-- Name: gdpr_consent_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gdpr_consent_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    consent_type text,
    granted boolean,
    granted_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.gdpr_consent_logs OWNER TO postgres;

--
-- TOC entry 333 (class 1259 OID 245661)
-- Name: general_ledger_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.general_ledger_accounts (
    code text NOT NULL,
    name text NOT NULL,
    category text,
    is_active boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT general_ledger_accounts_category_check CHECK ((category = ANY (ARRAY['asset'::text, 'liability'::text, 'income'::text, 'expense'::text, 'equity'::text])))
);


ALTER TABLE public.general_ledger_accounts OWNER TO postgres;

--
-- TOC entry 334 (class 1259 OID 245669)
-- Name: generated_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generated_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_id uuid,
    generated_for_type text NOT NULL,
    generated_for_id uuid NOT NULL,
    file_url text NOT NULL,
    format text DEFAULT 'pdf'::text,
    generated_by uuid,
    generated_at timestamp without time zone DEFAULT now(),
    is_final boolean DEFAULT false,
    notes text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.generated_documents OWNER TO postgres;

--
-- TOC entry 335 (class 1259 OID 245678)
-- Name: geographic_pricing_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.geographic_pricing_factors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    zip_code character varying(10) NOT NULL,
    state character varying(2) NOT NULL,
    city character varying(100) NOT NULL,
    insurance_type character varying(50) NOT NULL,
    risk_factor numeric(5,2) DEFAULT 1.0,
    description text,
    effective_from timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    effective_to timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.geographic_pricing_factors OWNER TO postgres;

--
-- TOC entry 336 (class 1259 OID 245687)
-- Name: group_admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.group_admins (
    group_id uuid,
    user_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.group_admins OWNER TO postgres;

--
-- TOC entry 337 (class 1259 OID 245692)
-- Name: group_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.group_audit_logs (
    group_id uuid,
    action text,
    performed_by uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.group_audit_logs OWNER TO postgres;

--
-- TOC entry 338 (class 1259 OID 245699)
-- Name: group_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.group_contacts (
    group_id uuid,
    name text,
    email text,
    phone text,
    role text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.group_contacts OWNER TO postgres;

--
-- TOC entry 339 (class 1259 OID 245705)
-- Name: group_demographics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.group_demographics (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    age_bracket_id uuid NOT NULL,
    member_count integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT group_demographics_member_count_check CHECK ((member_count >= 0))
);


ALTER TABLE public.group_demographics OWNER TO postgres;

--
-- TOC entry 340 (class 1259 OID 245711)
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    name character varying(100) NOT NULL,
    description text,
    company_id uuid,
    parent_group_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- TOC entry 341 (class 1259 OID 245720)
-- Name: health_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    wearable_device_id uuid,
    metric_type character varying(50),
    metric_value numeric(10,4),
    unit_of_measure character varying(20),
    quality_score numeric(3,2),
    contextual_data jsonb,
    anomaly_detected boolean DEFAULT false,
    health_insights jsonb,
    recorded_at timestamp with time zone NOT NULL,
    synced_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.health_metrics OWNER TO postgres;

--
-- TOC entry 342 (class 1259 OID 245728)
-- Name: icd10_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.icd10_codes (
    code character varying(50) NOT NULL,
    description text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.icd10_codes OWNER TO postgres;

--
-- TOC entry 343 (class 1259 OID 245734)
-- Name: integration_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.integration_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    integration_name character varying(100) NOT NULL,
    endpoint_url character varying(500),
    http_method character varying(10),
    request_headers jsonb,
    request_body jsonb,
    request_size_bytes integer,
    response_status_code integer,
    response_headers jsonb,
    response_body jsonb,
    response_size_bytes integer,
    response_time_ms integer,
    error_message text,
    error_code character varying(50),
    retry_count integer DEFAULT 0,
    business_transaction_id character varying(100),
    user_id uuid,
    correlation_id uuid DEFAULT gen_random_uuid(),
    contains_pii boolean DEFAULT false,
    data_classification character varying(30),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.integration_logs OWNER TO postgres;

--
-- TOC entry 600 (class 1259 OID 249999)
-- Name: iot_alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iot_alerts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    device_id uuid,
    alert_type character varying(50),
    severity character varying(20),
    alert_message text,
    alert_data jsonb,
    triggered_at timestamp without time zone NOT NULL,
    acknowledged_at timestamp without time zone,
    acknowledged_by uuid,
    resolved_at timestamp without time zone,
    action_taken text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.iot_alerts OWNER TO postgres;

--
-- TOC entry 344 (class 1259 OID 245744)
-- Name: iot_data_streams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iot_data_streams (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    device_id uuid,
    stream_type character varying(50),
    sensor_data jsonb,
    processed_data jsonb,
    anomaly_detected boolean DEFAULT false,
    anomaly_details jsonb,
    location public.geometry(Point,4326),
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    ingestion_timestamp timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.iot_data_streams OWNER TO postgres;

--
-- TOC entry 345 (class 1259 OID 245753)
-- Name: iot_device_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iot_device_types (
    device_type_name character varying(100) NOT NULL,
    category character varying(50),
    manufacturer character varying(100),
    model_name character varying(100),
    connectivity_protocol character varying(30),
    data_transmission_frequency integer,
    battery_life_hours integer,
    environmental_rating character varying(10),
    sensor_capabilities jsonb,
    security_features jsonb,
    cost_usd numeric(10,2),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.iot_device_types OWNER TO postgres;

--
-- TOC entry 346 (class 1259 OID 245760)
-- Name: iot_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iot_devices (
    device_type_id uuid,
    member_id uuid,
    device_serial_number character varying(100),
    firmware_version character varying(50),
    last_seen timestamp with time zone,
    location public.geometry(Point,4326),
    battery_level numeric(5,2),
    signal_strength numeric(5,2),
    status character varying(30),
    configuration jsonb,
    security_keys jsonb,
    installed_at timestamp with time zone,
    warranty_expires timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.iot_devices OWNER TO postgres;

--
-- TOC entry 347 (class 1259 OID 245767)
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.journal_entries (
    entry_number character varying(30) NOT NULL,
    company_id uuid,
    period_id uuid,
    entry_date date NOT NULL,
    description text,
    reference_type character varying(50),
    reference_id uuid,
    total_debit numeric(15,2) NOT NULL,
    total_credit numeric(15,2) NOT NULL,
    currency character varying(3) DEFAULT 'USD'::character varying,
    exchange_rate numeric(10,6) DEFAULT 1.0,
    status character varying(20) DEFAULT 'draft'::character varying,
    created_by uuid,
    approved_by uuid,
    posted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.journal_entries OWNER TO postgres;

--
-- TOC entry 348 (class 1259 OID 245777)
-- Name: journal_entry_lines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.journal_entry_lines (
    journal_entry_id uuid,
    line_number integer NOT NULL,
    account_id uuid,
    description text,
    debit_amount numeric(15,2) DEFAULT 0,
    credit_amount numeric(15,2) DEFAULT 0,
    cost_center character varying(50),
    department character varying(50),
    project_code character varying(50),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.journal_entry_lines OWNER TO postgres;

--
-- TOC entry 579 (class 1259 OID 249000)
-- Name: knowledge_articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.knowledge_articles (
    id uuid NOT NULL,
    category_id uuid,
    title character varying(200),
    content text,
    language character varying(10),
    is_published boolean DEFAULT false,
    created_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.knowledge_articles OWNER TO postgres;

--
-- TOC entry 578 (class 1259 OID 248988)
-- Name: knowledge_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.knowledge_categories (
    id uuid NOT NULL,
    name character varying(100),
    description text,
    parent_id uuid
);


ALTER TABLE public.knowledge_categories OWNER TO postgres;

--
-- TOC entry 349 (class 1259 OID 245785)
-- Name: language_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.language_keys (
    key_name character varying(200) NOT NULL,
    key_category character varying(100),
    context character varying(500),
    data_type character varying(20) DEFAULT 'text'::character varying,
    usage_count bigint DEFAULT 0,
    last_used timestamp with time zone,
    is_deprecated boolean DEFAULT false,
    replacement_key character varying(200),
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.language_keys OWNER TO postgres;

--
-- TOC entry 350 (class 1259 OID 245795)
-- Name: language_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.language_settings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    company_id uuid,
    preferred_language text DEFAULT 'en'::text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.language_settings OWNER TO postgres;

--
-- TOC entry 351 (class 1259 OID 245802)
-- Name: languages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.languages (
    language_code character varying(10) NOT NULL,
    iso_639_code character varying(3),
    language_name character varying(100),
    native_name character varying(100),
    text_direction character varying(3) DEFAULT 'ltr'::character varying,
    is_active boolean DEFAULT true,
    completion_percentage numeric(5,2) DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.languages OWNER TO postgres;

--
-- TOC entry 352 (class 1259 OID 245810)
-- Name: locales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locales (
    locale_code character varying(10) NOT NULL,
    language_id uuid,
    country_code character varying(2),
    currency_code character varying(3),
    date_format character varying(50),
    time_format character varying(50),
    number_format jsonb,
    is_default boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.locales OWNER TO postgres;

--
-- TOC entry 353 (class 1259 OID 245818)
-- Name: login_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.login_attempts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(100),
    user_id uuid,
    ip_address inet,
    user_agent text,
    attempt_result character varying(20),
    failure_reason character varying(100),
    location_data jsonb,
    device_fingerprint text,
    session_id character varying(255),
    attempted_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.login_attempts OWNER TO postgres;

--
-- TOC entry 582 (class 1259 OID 249038)
-- Name: login_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.login_devices (
    id uuid NOT NULL,
    user_id uuid,
    device_fingerprint text,
    user_agent text,
    ip_address text,
    last_used_at timestamp without time zone,
    is_trusted boolean DEFAULT false
);


ALTER TABLE public.login_devices OWNER TO postgres;

--
-- TOC entry 354 (class 1259 OID 245825)
-- Name: login_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.login_sessions (
    user_type text,
    user_id uuid,
    device_info text,
    ip_address text,
    started_at timestamp without time zone DEFAULT now(),
    ended_at timestamp without time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid,
    CONSTRAINT login_sessions_user_type_check CHECK ((user_type = ANY (ARRAY['admin'::text, 'member'::text, 'garage'::text, 'broker'::text])))
);


ALTER TABLE public.login_sessions OWNER TO postgres;

--
-- TOC entry 625 (class 1259 OID 250389)
-- Name: market_data_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_data_sources (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_name character varying(200) NOT NULL,
    source_type character varying(50),
    api_endpoint character varying(500),
    authentication_config jsonb,
    data_extraction_rules jsonb,
    update_frequency character varying(20) DEFAULT 'hourly'::character varying,
    reliability_score numeric(3,2) DEFAULT 0.8,
    cost_per_api_call numeric(8,4),
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.market_data_sources OWNER TO postgres;

--
-- TOC entry 627 (class 1259 OID 250418)
-- Name: market_impact_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_impact_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    signal_id uuid,
    analysis_type character varying(50),
    impact_categories jsonb,
    quantified_impacts jsonb,
    probability_assessment jsonb,
    timeline_assessment jsonb,
    recommended_actions jsonb,
    urgency_level character varying(20) DEFAULT 'normal'::character varying,
    assigned_analyst uuid,
    analysis_completed_at timestamp without time zone,
    stakeholder_notifications jsonb,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.market_impact_analysis OWNER TO postgres;

--
-- TOC entry 626 (class 1259 OID 250401)
-- Name: market_signals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_signals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id uuid,
    signal_type character varying(50),
    signal_title character varying(300),
    signal_description text,
    raw_data jsonb,
    processed_data jsonb,
    confidence_score numeric(3,2),
    impact_severity character varying(20) DEFAULT 'medium'::character varying,
    affected_business_areas jsonb,
    detected_at timestamp without time zone DEFAULT now(),
    validation_status character varying(30) DEFAULT 'pending'::character varying,
    validated_by uuid,
    validated_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.market_signals OWNER TO postgres;

--
-- TOC entry 355 (class 1259 OID 245833)
-- Name: marketing_campaigns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketing_campaigns (
    campaign_name character varying(200) NOT NULL,
    campaign_type character varying(50),
    channel character varying(50),
    target_segment_ids integer[],
    start_date date,
    end_date date,
    budget numeric(15,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    target_audience_size integer,
    inclusion_criteria jsonb,
    exclusion_criteria jsonb,
    campaign_assets jsonb,
    a_b_test_variants jsonb,
    status character varying(30) DEFAULT 'planning'::character varying,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.marketing_campaigns OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 245111)
-- Name: medical_cards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medical_cards (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    policy_id uuid,
    company_id uuid,
    issued_at timestamp without time zone,
    expires_at timestamp without time zone,
    status character varying(50),
    plan_name text,
    card_number text,
    qr_code_url text,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.medical_cards OWNER TO postgres;

--
-- TOC entry 356 (class 1259 OID 245842)
-- Name: member_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_audit_logs (
    member_id uuid,
    action text,
    performed_by uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.member_audit_logs OWNER TO postgres;

--
-- TOC entry 553 (class 1259 OID 248401)
-- Name: member_benefit_usage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_benefit_usage (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid NOT NULL,
    policy_id uuid NOT NULL,
    plan_id uuid NOT NULL,
    coverage_id uuid,
    benefit_type character varying(100) NOT NULL,
    period_type character varying(20) DEFAULT 'annual'::character varying,
    period_start_date date NOT NULL,
    period_end_date date NOT NULL,
    benefit_limit numeric(15,2) NOT NULL,
    used_amount numeric(15,2) DEFAULT 0,
    remaining_amount numeric(15,2) NOT NULL,
    benefit_count_limit integer,
    used_count integer DEFAULT 0,
    remaining_count integer,
    utilization_percentage numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (benefit_limit > (0)::numeric) THEN ((used_amount / benefit_limit) * (100)::numeric)
    ELSE (0)::numeric
END) STORED,
    alert_sent_at_80_percent timestamp with time zone,
    alert_sent_at_90_percent timestamp with time zone,
    is_exhausted boolean DEFAULT false,
    exhausted_date date,
    last_used_date date,
    last_claim_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    CONSTRAINT valid_amounts CHECK (((used_amount >= (0)::numeric) AND (remaining_amount >= (0)::numeric))),
    CONSTRAINT valid_counts CHECK (((used_count >= 0) AND ((remaining_count IS NULL) OR (remaining_count >= 0))))
);


ALTER TABLE public.member_benefit_usage OWNER TO postgres;

--
-- TOC entry 10548 (class 0 OID 0)
-- Dependencies: 553
-- Name: TABLE member_benefit_usage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.member_benefit_usage IS 'Real-time tracking of member benefit utilization against limits';


--
-- TOC entry 548 (class 1259 OID 248098)
-- Name: member_benefit_utilization; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_benefit_utilization (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid NOT NULL,
    policy_id uuid NOT NULL,
    benefit_schedule_id uuid NOT NULL,
    period_type character varying(20) DEFAULT 'annual'::character varying NOT NULL,
    period_start_date date NOT NULL,
    period_end_date date NOT NULL,
    utilized_amount numeric(15,2) DEFAULT 0,
    utilized_count integer DEFAULT 0,
    remaining_amount numeric(15,2),
    remaining_count integer,
    last_utilized_at timestamp with time zone,
    is_exhausted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.member_benefit_utilization OWNER TO postgres;

--
-- TOC entry 10549 (class 0 OID 0)
-- Dependencies: 548
-- Name: TABLE member_benefit_utilization; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.member_benefit_utilization IS 'Tracks how much of each benefit a member has used';


--
-- TOC entry 357 (class 1259 OID 245849)
-- Name: member_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_history (
    member_id uuid,
    field_name character varying(50),
    old_value text,
    new_value text,
    changed_by uuid,
    changed_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.member_history OWNER TO postgres;

--
-- TOC entry 358 (class 1259 OID 245856)
-- Name: member_login_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_login_logs (
    member_id uuid,
    login_time timestamp without time zone DEFAULT now(),
    ip_address text,
    device_info text,
    location text,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.member_login_logs OWNER TO postgres;

--
-- TOC entry 359 (class 1259 OID 245863)
-- Name: member_persona_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_persona_mapping (
    member_id uuid,
    persona_id uuid,
    confidence_score numeric(5,4),
    assignment_date date DEFAULT CURRENT_DATE,
    assignment_method character varying(50),
    persona_evolution_history jsonb,
    last_updated timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.member_persona_mapping OWNER TO postgres;

--
-- TOC entry 360 (class 1259 OID 245871)
-- Name: member_signatures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_signatures (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid NOT NULL,
    signature_url text NOT NULL,
    signed_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.member_signatures OWNER TO postgres;

--
-- TOC entry 361 (class 1259 OID 245878)
-- Name: member_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.member_tags (
    member_id uuid,
    tag text NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.member_tags OWNER TO postgres;

--
-- TOC entry 363 (class 1259 OID 245897)
-- Name: mfa_methods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mfa_methods (
    user_id uuid,
    method_type character varying(30),
    method_config jsonb,
    is_primary boolean DEFAULT false,
    is_active boolean DEFAULT true,
    backup_codes text[],
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.mfa_methods OWNER TO postgres;

--
-- TOC entry 364 (class 1259 OID 245906)
-- Name: mfa_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mfa_sessions (
    user_id uuid,
    session_token character varying(255) NOT NULL,
    method_used character varying(30),
    device_fingerprint text,
    ip_address inet,
    expires_at timestamp with time zone,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.mfa_sessions OWNER TO postgres;

--
-- TOC entry 365 (class 1259 OID 245913)
-- Name: ml_experiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ml_experiments (
    experiment_name character varying(200) NOT NULL,
    experiment_type character varying(50),
    objective character varying(200),
    base_model_version_id uuid,
    dataset_version_id uuid,
    experiment_config jsonb,
    hypothesis text,
    success_criteria jsonb,
    expected_improvement numeric(5,4),
    status character varying(30) DEFAULT 'planned'::character varying,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    total_runtime_minutes integer,
    results jsonb,
    conclusions text,
    lessons_learned text,
    recommended_actions jsonb,
    next_experiments jsonb,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ml_experiments OWNER TO postgres;

--
-- TOC entry 366 (class 1259 OID 245921)
-- Name: ml_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ml_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_name text,
    version text,
    trained_at timestamp without time zone,
    accuracy double precision,
    notes text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.ml_models OWNER TO postgres;

--
-- TOC entry 367 (class 1259 OID 245927)
-- Name: model_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_versions (
    model_name character varying(200) NOT NULL,
    version character varying(50) NOT NULL,
    parent_version character varying(50),
    architecture_type character varying(50),
    framework character varying(50),
    model_size_mb numeric(10,2),
    parameter_count bigint,
    training_dataset_id uuid,
    hyperparameters jsonb,
    training_duration_minutes integer,
    training_cost numeric(10,2),
    compute_resources jsonb,
    training_metrics jsonb,
    validation_metrics jsonb,
    test_metrics jsonb,
    benchmark_results jsonb,
    model_file_path character varying(500),
    model_hash character varying(64),
    checkpoint_paths jsonb,
    export_formats jsonb,
    deployment_status character varying(30) DEFAULT 'experimental'::character varying,
    deployment_config jsonb,
    api_endpoint character varying(200),
    inference_cost_per_request numeric(10,6),
    drift_detection_enabled boolean DEFAULT false,
    performance_threshold numeric(5,4),
    retraining_trigger_conditions jsonb,
    bias_testing_results jsonb,
    fairness_metrics jsonb,
    explainability_support boolean DEFAULT false,
    created_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.model_versions OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 245119)
-- Name: motor_cards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.motor_cards (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    policy_id uuid,
    company_id uuid,
    plate_number text,
    car_model text,
    chassis_number text,
    insurance_type text,
    issued_at timestamp without time zone,
    expires_at timestamp without time zone,
    status character varying(50),
    insured_value numeric,
    driver_name text,
    license_number text,
    license_expiry_date date,
    color text,
    year_of_manufacture integer,
    vehicle_make text,
    notes text,
    qr_code_url text,
    policy_number text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.motor_cards OWNER TO postgres;

--
-- TOC entry 368 (class 1259 OID 245937)
-- Name: motor_exclusion_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.motor_exclusion_categories (
    name character varying(100) NOT NULL,
    description text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.motor_exclusion_categories OWNER TO postgres;

--
-- TOC entry 369 (class 1259 OID 245943)
-- Name: motor_exclusion_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.motor_exclusion_codes (
    code character varying(50) NOT NULL,
    title character varying(150) NOT NULL,
    category_id uuid,
    description text,
    is_active boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.motor_exclusion_codes OWNER TO postgres;

--
-- TOC entry 370 (class 1259 OID 245950)
-- Name: nlp_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nlp_models (
    model_name character varying(100) NOT NULL,
    model_type character varying(50),
    language_support text[],
    model_config jsonb,
    performance_metrics jsonb,
    api_endpoint character varying(200),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.nlp_models OWNER TO postgres;

--
-- TOC entry 603 (class 1259 OID 250067)
-- Name: notification_queue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_queue (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    recipient_id uuid NOT NULL,
    recipient_type character varying(20) DEFAULT 'user'::character varying,
    notification_type character varying(50) NOT NULL,
    channel character varying(30) NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    priority character varying(20) DEFAULT 'normal'::character varying,
    status character varying(20) DEFAULT 'pending'::character varying,
    scheduled_at timestamp with time zone DEFAULT now(),
    sent_at timestamp with time zone,
    delivery_status character varying(30),
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    archived_at timestamp without time zone,
    CONSTRAINT notification_queue_channel_check CHECK (((channel)::text = ANY ((ARRAY['email'::character varying, 'sms'::character varying, 'push'::character varying, 'in-app'::character varying])::text[]))),
    CONSTRAINT notification_queue_priority_check CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'normal'::character varying, 'high'::character varying, 'urgent'::character varying])::text[]))),
    CONSTRAINT notification_queue_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'sent'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.notification_queue OWNER TO postgres;

--
-- TOC entry 569 (class 1259 OID 248854)
-- Name: notifications_read_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications_read_log (
    id uuid NOT NULL,
    notification_id uuid,
    user_id uuid,
    read_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.notifications_read_log OWNER TO postgres;

--
-- TOC entry 371 (class 1259 OID 245958)
-- Name: otp_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.otp_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    otp_code text NOT NULL,
    sent_via text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    expires_at timestamp without time zone,
    is_used boolean DEFAULT false
);


ALTER TABLE public.otp_requests OWNER TO postgres;

--
-- TOC entry 622 (class 1259 OID 250341)
-- Name: parallel_scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parallel_scenarios (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    universe_id uuid,
    scenario_name character varying(200),
    scenario_number integer,
    decision_choices jsonb,
    environmental_assumptions jsonb,
    resource_allocations jsonb,
    risk_profile character varying(20),
    expected_outcomes jsonb,
    success_probability numeric(3,2),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.parallel_scenarios OWNER TO postgres;

--
-- TOC entry 372 (class 1259 OID 245966)
-- Name: password_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_policies (
    company_id uuid,
    policy_name character varying(100) DEFAULT 'default'::character varying,
    min_length integer DEFAULT 8,
    max_length integer DEFAULT 128,
    require_uppercase boolean DEFAULT true,
    require_lowercase boolean DEFAULT true,
    require_numbers boolean DEFAULT true,
    require_symbols boolean DEFAULT true,
    forbidden_sequences text[],
    password_history_count integer DEFAULT 5,
    max_age_days integer DEFAULT 90,
    warning_days_before_expiry integer DEFAULT 7,
    max_failed_attempts integer DEFAULT 5,
    lockout_duration_minutes integer DEFAULT 30,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.password_policies OWNER TO postgres;

--
-- TOC entry 373 (class 1259 OID 245987)
-- Name: payment_methods; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_methods (
    member_id uuid,
    method_type character varying(30) NOT NULL,
    provider character varying(50),
    account_identifier character varying(100),
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    expiry_date date,
    billing_address jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.payment_methods OWNER TO postgres;

--
-- TOC entry 374 (class 1259 OID 245997)
-- Name: payment_receipts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_receipts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    payment_date date,
    received_from text,
    amount numeric(14,2),
    method text,
    reference text,
    status text DEFAULT 'confirmed'::text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.payment_receipts OWNER TO postgres;

--
-- TOC entry 375 (class 1259 OID 246005)
-- Name: payment_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_transactions (
    invoice_id uuid,
    payment_method_id uuid,
    transaction_id character varying(100),
    amount numeric(15,2) NOT NULL,
    currency character varying(3) DEFAULT 'USD'::character varying,
    status public.payment_status DEFAULT 'pending'::public.payment_status,
    gateway_response jsonb,
    processed_at timestamp with time zone,
    failure_reason text,
    retry_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.payment_transactions OWNER TO postgres;

--
-- TOC entry 604 (class 1259 OID 250090)
-- Name: performance_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.performance_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_value numeric(15,4),
    metric_unit character varying(20),
    table_name character varying(100),
    query_type character varying(50),
    execution_time_ms numeric(10,2),
    recorded_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.performance_metrics OWNER TO postgres;

--
-- TOC entry 376 (class 1259 OID 246015)
-- Name: permission_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permission_audit_logs (
    user_id uuid,
    role_before text,
    role_after text,
    changed_by uuid,
    changed_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.permission_audit_logs OWNER TO postgres;

--
-- TOC entry 589 (class 1259 OID 249132)
-- Name: permission_restrictions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permission_restrictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_id uuid,
    resource_type character varying(50) NOT NULL,
    action character varying(20) NOT NULL,
    access_level character varying(20) NOT NULL,
    conditions jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.permission_restrictions OWNER TO postgres;

--
-- TOC entry 377 (class 1259 OID 246022)
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    name character varying(100) NOT NULL,
    description text,
    resource character varying(50),
    action character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    scope_department character varying(50),
    scope_unit character varying(50),
    scope_company uuid,
    conditions jsonb
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- TOC entry 378 (class 1259 OID 246029)
-- Name: personalized_content_delivery; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personalized_content_delivery (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    template_id uuid,
    delivery_channel character varying(50),
    personalized_content jsonb,
    delivery_timestamp timestamp with time zone NOT NULL,
    opened boolean DEFAULT false,
    clicked boolean DEFAULT false,
    converted boolean DEFAULT false,
    engagement_score numeric(3,2),
    feedback_rating integer,
    optimization_feedback jsonb,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.personalized_content_delivery OWNER TO postgres;

--
-- TOC entry 543 (class 1259 OID 247982)
-- Name: plan_benefit_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_benefit_schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    plan_id uuid NOT NULL,
    coverage_id uuid,
    category_id uuid,
    benefit_name character varying(200) NOT NULL,
    benefit_description text,
    benefit_code character varying(50),
    limit_amount numeric(15,2),
    coinsurance_percent numeric(5,2),
    deductible_amount numeric(15,2) DEFAULT 0,
    copay_amount numeric(10,2) DEFAULT 0,
    requires_preapproval boolean DEFAULT false,
    is_optional boolean DEFAULT false,
    is_active boolean DEFAULT true,
    network_tier character varying(50),
    display_group character varying(100),
    display_order integer DEFAULT 0,
    disclaimer text,
    alert_threshold_percent numeric(5,2) DEFAULT 80.0,
    frequency_limit character varying(50),
    waiting_period_days integer DEFAULT 0,
    ai_summary text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT plan_benefit_schedules_coinsurance_percent_check CHECK (((coinsurance_percent >= (0)::numeric) AND (coinsurance_percent <= (100)::numeric))),
    CONSTRAINT valid_deductible CHECK ((deductible_amount >= (0)::numeric)),
    CONSTRAINT valid_limit_amount CHECK (((limit_amount IS NULL) OR (limit_amount >= (0)::numeric)))
);


ALTER TABLE public.plan_benefit_schedules OWNER TO postgres;

--
-- TOC entry 10550 (class 0 OID 0)
-- Dependencies: 543
-- Name: TABLE plan_benefit_schedules; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.plan_benefit_schedules IS 'Detailed benefit schedules for insurance plans with enhanced TOB features';


--
-- TOC entry 379 (class 1259 OID 246038)
-- Name: plan_coverage_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_coverage_links (
    plan_id uuid,
    coverage_id uuid,
    coverage_amount numeric(15,2),
    deductible numeric(15,2) DEFAULT 0,
    copay_percentage numeric(5,2) DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    notes text,
    unit character varying(50),
    frequency_limit integer,
    is_mandatory boolean DEFAULT false,
    approval_needed boolean DEFAULT false,
    limit_type character varying(50),
    sub_category character varying(100),
    condition_tag character varying(100),
    specific_limit numeric(10,2),
    is_excluded boolean DEFAULT false,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.plan_coverage_links OWNER TO postgres;

--
-- TOC entry 380 (class 1259 OID 246051)
-- Name: plan_exclusion_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_exclusion_links (
    plan_id uuid,
    exclusion_id uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.plan_exclusion_links OWNER TO postgres;

--
-- TOC entry 381 (class 1259 OID 246056)
-- Name: plan_exclusions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_exclusions (
    plan_id uuid,
    plan_type character varying(10) NOT NULL,
    exclusion_text text NOT NULL,
    cpt_code_id uuid,
    icd10_code_id uuid,
    motor_code_id uuid,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    exclusion_text_ar text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT plan_exclusions_plan_type_check CHECK (((plan_type)::text = ANY (ARRAY[('medical'::character varying)::text, ('motor'::character varying)::text])))
);


ALTER TABLE public.plan_exclusions OWNER TO postgres;

--
-- TOC entry 382 (class 1259 OID 246065)
-- Name: plan_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plan_types (
    code character varying NOT NULL,
    label character varying NOT NULL,
    icon character varying(10),
    order_index integer,
    language_labels jsonb,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.plan_types OWNER TO postgres;

--
-- TOC entry 384 (class 1259 OID 246085)
-- Name: plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plans (
    name character varying(100) NOT NULL,
    description text,
    plan_type character varying(30),
    company_id uuid,
    product_id uuid,
    premium_amount numeric(15,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    coverage_period_months integer DEFAULT 12,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    version character varying(50),
    start_date date,
    end_date date,
    is_default boolean DEFAULT false,
    visibility character varying(20) DEFAULT 'public'::character varying,
    tags text[],
    approval_required boolean DEFAULT false,
    created_by uuid,
    archived_at timestamp without time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid
);


ALTER TABLE public.plans OWNER TO postgres;

--
-- TOC entry 383 (class 1259 OID 246073)
-- Name: policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policies (
    policy_number character varying(50) NOT NULL,
    member_id uuid,
    plan_id uuid,
    application_id uuid,
    status public.policy_status DEFAULT 'pending'::public.policy_status,
    effective_date date NOT NULL,
    expiry_date date,
    premium_amount numeric(15,2),
    total_sum_insured numeric(15,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    payment_frequency character varying(20) DEFAULT 'annual'::character varying,
    agent_id uuid,
    broker_id uuid,
    underwriter_id uuid,
    policy_terms jsonb,
    endorsements jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    policy_channel_id uuid,
    product_id uuid,
    entity_id uuid,
    endorsement_number character varying(50),
    auto_renew_date date,
    document_url text,
    tags text,
    underwriter_notes text,
    policy_type_id uuid,
    is_renewable boolean DEFAULT false,
    notes text,
    group_id uuid,
    name character varying,
    company_id uuid,
    deleted_at timestamp without time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT chk_policies_date_logic CHECK ((effective_date <= expiry_date))
);


ALTER TABLE public.policies OWNER TO postgres;

--
-- TOC entry 547 (class 1259 OID 248074)
-- Name: policy_benefit_overrides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_benefit_overrides (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid NOT NULL,
    benefit_schedule_id uuid NOT NULL,
    override_limit_amount numeric(15,2),
    override_coinsurance_percent numeric(5,2),
    override_deductible_amount numeric(15,2),
    override_copay_amount numeric(10,2),
    override_preapproval_required boolean,
    override_network_tier character varying(50),
    effective_date date DEFAULT CURRENT_DATE NOT NULL,
    expiry_date date,
    override_reason character varying(200) NOT NULL,
    approval_reference character varying(100),
    notes text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid NOT NULL,
    updated_by uuid,
    approved_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT valid_date_range CHECK (((effective_date <= expiry_date) OR (expiry_date IS NULL))),
    CONSTRAINT valid_override_coinsurance CHECK (((override_coinsurance_percent IS NULL) OR ((override_coinsurance_percent >= (0)::numeric) AND (override_coinsurance_percent <= (100)::numeric))))
);


ALTER TABLE public.policy_benefit_overrides OWNER TO postgres;

--
-- TOC entry 10551 (class 0 OID 0)
-- Dependencies: 547
-- Name: TABLE policy_benefit_overrides; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.policy_benefit_overrides IS 'Policy-specific overrides to standard benefit schedules';


--
-- TOC entry 552 (class 1259 OID 248359)
-- Name: policy_cancellations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_cancellations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid NOT NULL,
    cancellation_type character varying(50) NOT NULL,
    requested_date date NOT NULL,
    effective_date date NOT NULL,
    cancellation_reason text NOT NULL,
    refund_amount numeric(15,2) DEFAULT 0,
    refund_processed boolean DEFAULT false,
    refund_date date,
    requested_by uuid,
    approved_by uuid,
    approval_date timestamp with time zone,
    approval_notes text,
    status character varying(30) DEFAULT 'requested'::character varying,
    is_reversed boolean DEFAULT false,
    reversal_reason text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT valid_cancellation_type CHECK (((cancellation_type)::text = ANY ((ARRAY['member_request'::character varying, 'non_payment'::character varying, 'fraud'::character varying, 'regulatory'::character varying, 'underwriting_decline'::character varying, 'business_decision'::character varying])::text[]))),
    CONSTRAINT valid_dates CHECK ((effective_date >= requested_date)),
    CONSTRAINT valid_status CHECK (((status)::text = ANY ((ARRAY['requested'::character varying, 'under_review'::character varying, 'approved'::character varying, 'denied'::character varying, 'processed'::character varying, 'completed'::character varying])::text[])))
);


ALTER TABLE public.policy_cancellations OWNER TO postgres;

--
-- TOC entry 10552 (class 0 OID 0)
-- Dependencies: 552
-- Name: TABLE policy_cancellations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.policy_cancellations IS 'Tracks all policy cancellation requests and processing workflow';


--
-- TOC entry 385 (class 1259 OID 246099)
-- Name: policy_channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_channels (
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_channels OWNER TO postgres;

--
-- TOC entry 386 (class 1259 OID 246107)
-- Name: policy_coverages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_coverages (
    policy_id uuid,
    coverage_id uuid,
    coverage_limit numeric,
    co_insurance numeric,
    is_active boolean DEFAULT true,
    is_override boolean DEFAULT false,
    notes text,
    assigned_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_coverages OWNER TO postgres;

--
-- TOC entry 387 (class 1259 OID 246117)
-- Name: policy_dependents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_dependents (
    policy_id uuid,
    full_name character varying(150),
    date_of_birth date,
    relation character varying(50),
    gender character varying(10),
    national_id character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_dependents OWNER TO postgres;

--
-- TOC entry 388 (class 1259 OID 246122)
-- Name: policy_endorsements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_endorsements (
    policy_id uuid,
    change_type text,
    old_value jsonb,
    new_value jsonb,
    approved_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_endorsements OWNER TO postgres;

--
-- TOC entry 389 (class 1259 OID 246129)
-- Name: policy_exclusion_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_exclusion_links (
    policy_id uuid,
    exclusion_id uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_exclusion_links OWNER TO postgres;

--
-- TOC entry 558 (class 1259 OID 248573)
-- Name: policy_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_flags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid NOT NULL,
    flag_type character varying(50) NOT NULL,
    flag_value boolean DEFAULT true,
    flag_severity character varying(20) DEFAULT 'info'::character varying,
    flag_reason text NOT NULL,
    flag_description text,
    reference_number character varying(100),
    effective_date date DEFAULT CURRENT_DATE,
    expiry_date date,
    is_active boolean DEFAULT true,
    auto_expire boolean DEFAULT false,
    blocks_renewals boolean DEFAULT false,
    blocks_endorsements boolean DEFAULT false,
    blocks_claims boolean DEFAULT false,
    blocks_cancellations boolean DEFAULT false,
    requires_manager_approval boolean DEFAULT false,
    is_resolved boolean DEFAULT false,
    resolved_date date,
    resolved_by uuid,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid NOT NULL,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT valid_dates CHECK (((expiry_date IS NULL) OR (expiry_date >= effective_date))),
    CONSTRAINT valid_flag_type CHECK (((flag_type)::text = ANY ((ARRAY['compliance_review'::character varying, 'fraud_investigation'::character varying, 'payment_default'::character varying, 'high_risk'::character varying, 'regulatory_hold'::character varying, 'manual_review_required'::character varying, 'data_quality_issue'::character varying, 'subsidized_policy'::character varying, 'vip_member'::character varying, 'corporate_special_terms'::character varying, 'reinsurance_notification'::character varying])::text[]))),
    CONSTRAINT valid_severity CHECK (((flag_severity)::text = ANY ((ARRAY['info'::character varying, 'warning'::character varying, 'critical'::character varying, 'blocker'::character varying])::text[])))
);


ALTER TABLE public.policy_flags OWNER TO postgres;

--
-- TOC entry 10553 (class 0 OID 0)
-- Dependencies: 558
-- Name: TABLE policy_flags; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.policy_flags IS 'Special compliance and operational flags on policies';


--
-- TOC entry 390 (class 1259 OID 246134)
-- Name: policy_lifecycle_stages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_lifecycle_stages (
    stage_name character varying(50) NOT NULL,
    stage_order integer,
    description text,
    typical_duration_days integer,
    required_actions jsonb,
    next_possible_stages integer[],
    is_terminal boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_lifecycle_stages OWNER TO postgres;

--
-- TOC entry 391 (class 1259 OID 246142)
-- Name: policy_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_payments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid,
    amount numeric(12,2),
    payment_date date,
    payment_method text,
    status text,
    receipt_number text,
    is_refunded boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT policy_payments_status_check CHECK ((status = ANY (ARRAY['paid'::text, 'pending'::text, 'failed'::text, 'refunded'::text])))
);


ALTER TABLE public.policy_payments OWNER TO postgres;

--
-- TOC entry 392 (class 1259 OID 246151)
-- Name: policy_renewals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_renewals (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    previous_policy_id uuid,
    renewal_date timestamp with time zone NOT NULL,
    premium_before_renewal numeric(15,2),
    renewal_premium numeric(15,2),
    renewal_reason text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_renewals OWNER TO postgres;

--
-- TOC entry 393 (class 1259 OID 246158)
-- Name: policy_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_schedule (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    policy_id uuid,
    event_type text,
    scheduled_date date,
    status text,
    executed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT policy_schedule_event_type_check CHECK ((event_type = ANY (ARRAY['renewal'::text, 'lapse'::text, 'cancellation'::text, 'auto_renew'::text])))
);


ALTER TABLE public.policy_schedule OWNER TO postgres;

--
-- TOC entry 394 (class 1259 OID 246166)
-- Name: policy_status_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_status_logs (
    policy_id uuid,
    old_status character varying(50),
    new_status character varying(50),
    changed_by uuid,
    change_reason text,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.policy_status_logs OWNER TO postgres;

--
-- TOC entry 395 (class 1259 OID 246173)
-- Name: policy_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_types (
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_types OWNER TO postgres;

--
-- TOC entry 396 (class 1259 OID 246181)
-- Name: policy_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.policy_versions (
    policy_id uuid,
    version_number integer NOT NULL,
    change_reason text,
    changes jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.policy_versions OWNER TO postgres;

--
-- TOC entry 598 (class 1259 OID 249391)
-- Name: pool_participations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pool_participations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pool_name character varying(200) NOT NULL,
    pool_type character varying(50),
    participation_percentage numeric(8,4) NOT NULL,
    maximum_line numeric(15,2),
    joining_date date NOT NULL,
    exit_date date,
    annual_deposit numeric(15,2),
    profit_share_percentage numeric(8,4),
    management_expense_percentage numeric(8,4),
    pool_manager character varying(200),
    pool_agreement_terms text,
    currency character varying(3),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.pool_participations OWNER TO postgres;

--
-- TOC entry 10554 (class 0 OID 0)
-- Dependencies: 598
-- Name: TABLE pool_participations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.pool_participations IS 'Insurance pool participations (terrorism, nuclear, etc.)';


--
-- TOC entry 610 (class 1259 OID 250177)
-- Name: prediction_batch_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction_batch_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_name character varying(200),
    model_id uuid,
    schedule_expression character varying(100),
    target_entities jsonb,
    job_status character varying(30) DEFAULT 'scheduled'::character varying,
    last_run_at timestamp without time zone,
    next_run_at timestamp without time zone,
    results_count integer,
    execution_time_seconds integer,
    error_message text,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.prediction_batch_jobs OWNER TO postgres;

--
-- TOC entry 608 (class 1259 OID 250149)
-- Name: prediction_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction_models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_name character varying(200) NOT NULL,
    prediction_type character varying(50),
    algorithm_type character varying(50),
    training_features jsonb,
    model_parameters jsonb,
    performance_metrics jsonb,
    prediction_horizon_days integer,
    confidence_threshold numeric(3,2) DEFAULT 0.8,
    model_file_path character varying(500),
    model_version character varying(50),
    deployment_status character varying(30) DEFAULT 'development'::character varying,
    last_retrained timestamp without time zone,
    retraining_frequency character varying(20) DEFAULT 'monthly'::character varying,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.prediction_models OWNER TO postgres;

--
-- TOC entry 609 (class 1259 OID 250161)
-- Name: prediction_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid,
    entity_type character varying(50),
    entity_id uuid,
    prediction_value numeric(15,4),
    confidence_score numeric(3,2),
    prediction_factors jsonb,
    prediction_date timestamp without time zone DEFAULT now(),
    actual_outcome numeric(15,4),
    prediction_accuracy numeric(5,4),
    feedback_provided boolean DEFAULT false,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.prediction_results OWNER TO postgres;

--
-- TOC entry 397 (class 1259 OID 246188)
-- Name: premium_age_brackets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_age_brackets (
    pricing_profile_id uuid,
    age_from integer NOT NULL,
    age_to integer NOT NULL,
    premium numeric(10,2) NOT NULL,
    gender character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_age_brackets OWNER TO postgres;

--
-- TOC entry 398 (class 1259 OID 246194)
-- Name: premium_calculations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_calculations (
    policy_id uuid,
    pricing_model_id uuid,
    calculation_date date DEFAULT CURRENT_DATE,
    base_premium numeric(15,2),
    risk_adjustments jsonb,
    final_premium numeric(15,2),
    calculation_details jsonb,
    manual_override boolean DEFAULT false,
    override_reason text,
    calculated_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_calculations OWNER TO postgres;

--
-- TOC entry 399 (class 1259 OID 246203)
-- Name: premium_coinsurance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_coinsurance (
    uuid uuid DEFAULT gen_random_uuid(),
    pricing_profile_id uuid,
    service_type character varying(100),
    percentage numeric(5,2),
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT premium_coinsurance_percentage_check CHECK (((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))
);


ALTER TABLE public.premium_coinsurance OWNER TO postgres;

--
-- TOC entry 400 (class 1259 OID 246213)
-- Name: premium_copay; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_copay (
    pricing_profile_id uuid,
    service_type character varying(100) NOT NULL,
    copay_percent numeric(5,2) NOT NULL,
    copay_cap numeric(10,2),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_copay OWNER TO postgres;

--
-- TOC entry 401 (class 1259 OID 246221)
-- Name: premium_copayment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_copayment (
    uuid uuid DEFAULT gen_random_uuid(),
    pricing_profile_id uuid,
    service_type character varying(100),
    amount numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT premium_copayment_amount_check CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.premium_copayment OWNER TO postgres;

--
-- TOC entry 402 (class 1259 OID 246230)
-- Name: premium_deductible; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_deductible (
    uuid uuid DEFAULT gen_random_uuid(),
    pricing_profile_id uuid,
    service_type character varying(100),
    amount numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT premium_deductible_amount_check CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.premium_deductible OWNER TO postgres;

--
-- TOC entry 403 (class 1259 OID 246239)
-- Name: premium_deductibles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_deductibles (
    deductible_amount integer NOT NULL,
    factor numeric(5,3) NOT NULL,
    notes text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_deductibles OWNER TO postgres;

--
-- TOC entry 404 (class 1259 OID 246248)
-- Name: premium_industries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_industries (
    industry_name character varying(100) NOT NULL,
    load_factor numeric(5,3) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_industries OWNER TO postgres;

--
-- TOC entry 405 (class 1259 OID 246257)
-- Name: premium_invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_invoices (
    invoice_number character varying(30) NOT NULL,
    policy_id uuid,
    premium_schedule_id uuid,
    billing_period_start date NOT NULL,
    billing_period_end date NOT NULL,
    premium_amount numeric(15,2) NOT NULL,
    taxes numeric(15,2) DEFAULT 0,
    fees numeric(15,2) DEFAULT 0,
    discounts numeric(15,2) DEFAULT 0,
    total_amount numeric(15,2) NOT NULL,
    due_date date NOT NULL,
    invoice_date date DEFAULT CURRENT_DATE,
    status public.payment_status DEFAULT 'pending'::public.payment_status,
    payment_method character varying(50),
    payment_reference character varying(100),
    paid_amount numeric(15,2) DEFAULT 0,
    paid_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_invoices OWNER TO postgres;

--
-- TOC entry 406 (class 1259 OID 246269)
-- Name: premium_networks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_networks (
    pricing_profile_id uuid,
    network_type character varying(100) NOT NULL,
    surcharge numeric(10,2),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_networks OWNER TO postgres;

--
-- TOC entry 407 (class 1259 OID 246277)
-- Name: premium_override_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_override_logs (
    quotation_id uuid,
    overridden_by uuid,
    original_premium numeric(12,2),
    new_premium numeric(12,2),
    reason text,
    overridden_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.premium_override_logs OWNER TO postgres;

--
-- TOC entry 408 (class 1259 OID 246284)
-- Name: premium_regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_regions (
    region_id uuid,
    load_factor numeric(5,3) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    pricing_profile_id uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_regions OWNER TO postgres;

--
-- TOC entry 409 (class 1259 OID 246292)
-- Name: premium_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_rules (
    pricing_profile_id uuid,
    service_type character varying(100) NOT NULL,
    is_included boolean DEFAULT true,
    coinsurance_percent numeric(5,2),
    coverage_limit numeric(12,2),
    copayment_amount numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_rules OWNER TO postgres;

--
-- TOC entry 410 (class 1259 OID 246300)
-- Name: premium_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_schedules (
    policy_id uuid,
    billing_cycle_id uuid,
    total_premium numeric(15,2) NOT NULL,
    installment_count integer DEFAULT 1,
    installment_amount numeric(15,2),
    start_date date NOT NULL,
    end_date date NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_schedules OWNER TO postgres;

--
-- TOC entry 411 (class 1259 OID 246308)
-- Name: premium_services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_services (
    pricing_profile_id uuid,
    service_type character varying(100) NOT NULL,
    base_rate numeric(10,2),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_services OWNER TO postgres;

--
-- TOC entry 412 (class 1259 OID 246316)
-- Name: premium_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premium_settings (
    smoker_multiplier numeric(5,3) DEFAULT 0.5,
    max_group_discount numeric(5,3) DEFAULT 0.3,
    min_premium numeric(10,2) DEFAULT 100.00,
    rounding_precision integer DEFAULT 2,
    notes text,
    updated_at timestamp without time zone DEFAULT now(),
    key character varying(100) NOT NULL,
    value character varying(500) NOT NULL,
    description text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    archived_at timestamp without time zone
);


ALTER TABLE public.premium_settings OWNER TO postgres;

--
-- TOC entry 413 (class 1259 OID 246327)
-- Name: pricing_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pricing_models (
    model_name character varying(100) NOT NULL,
    product_type character varying(50) NOT NULL,
    model_version character varying(20) NOT NULL,
    model_type character varying(30),
    base_factors jsonb,
    adjustment_factors jsonb,
    model_coefficients jsonb,
    confidence_interval numeric(5,4),
    accuracy_metrics jsonb,
    training_data_period daterange,
    last_calibration_date date,
    is_active boolean DEFAULT true,
    created_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.pricing_models OWNER TO postgres;

--
-- TOC entry 414 (class 1259 OID 246335)
-- Name: pricing_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pricing_profiles (
    name character varying NOT NULL,
    insurance_type character varying NOT NULL,
    base_premium double precision DEFAULT 0.0,
    min_premium double precision DEFAULT 0.0,
    max_premium double precision DEFAULT 0.0,
    currency character varying DEFAULT 'USD'::character varying,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    version character varying,
    status character varying,
    effective_date date,
    uuid uuid DEFAULT gen_random_uuid(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.pricing_profiles OWNER TO postgres;

--
-- TOC entry 415 (class 1259 OID 246347)
-- Name: pricing_version_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pricing_version_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    target_type character varying(20) NOT NULL,
    target_id uuid NOT NULL,
    version_from integer NOT NULL,
    version_to integer NOT NULL,
    change_description text,
    changed_by character varying(100),
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pricing_version_logs_target_type_check CHECK (((target_type)::text = ANY (ARRAY[('RULE'::character varying)::text, ('PROFILE'::character varying)::text])))
);


ALTER TABLE public.pricing_version_logs OWNER TO postgres;

--
-- TOC entry 416 (class 1259 OID 246355)
-- Name: process_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.process_instances (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    process_id uuid,
    instance_name character varying(100),
    status character varying(30) DEFAULT 'running'::character varying,
    current_step character varying(100),
    input_data jsonb,
    context_data jsonb,
    priority character varying(20) DEFAULT 'normal'::character varying,
    assigned_to uuid,
    started_by integer,
    started_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    sla_due_date timestamp with time zone,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.process_instances OWNER TO postgres;

--
-- TOC entry 417 (class 1259 OID 246364)
-- Name: process_step_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.process_step_executions (
    instance_id uuid,
    step_name character varying(100),
    step_type character varying(30),
    status character varying(30),
    input_data jsonb,
    output_data jsonb,
    executed_by integer,
    execution_time_ms integer,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.process_step_executions OWNER TO postgres;

--
-- TOC entry 418 (class 1259 OID 246370)
-- Name: product_catalog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_catalog (
    product_code character varying(50) NOT NULL,
    product_name character varying(100) NOT NULL,
    product_category character varying(50),
    product_type character varying(50),
    description text,
    target_market jsonb,
    distribution_channels text[],
    regulatory_approvals jsonb,
    pricing_model_id uuid,
    underwriting_rules integer[],
    policy_terms jsonb,
    coverage_options jsonb,
    exclusions jsonb,
    commission_structure jsonb,
    is_active boolean DEFAULT true,
    launch_date date,
    sunset_date date,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.product_catalog OWNER TO postgres;

--
-- TOC entry 419 (class 1259 OID 246378)
-- Name: product_features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_features (
    product_id uuid,
    feature_name character varying(100),
    feature_type character varying(30),
    feature_description text,
    feature_config jsonb,
    is_optional boolean DEFAULT true,
    additional_premium numeric(15,2) DEFAULT 0,
    eligibility_criteria jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.product_features OWNER TO postgres;

--
-- TOC entry 420 (class 1259 OID 246388)
-- Name: provider_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_audit_logs (
    provider_id uuid,
    action text,
    performed_by uuid,
    old_data jsonb,
    new_data jsonb,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.provider_audit_logs OWNER TO postgres;

--
-- TOC entry 421 (class 1259 OID 246395)
-- Name: provider_availability_exceptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_availability_exceptions (
    provider_id uuid,
    exception_date date,
    reason text,
    is_closed boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_availability_exceptions OWNER TO postgres;

--
-- TOC entry 422 (class 1259 OID 246402)
-- Name: provider_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_claims (
    provider_id uuid,
    claim_id uuid,
    handled_at timestamp without time zone,
    status character varying(20),
    notes text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_claims OWNER TO postgres;

--
-- TOC entry 423 (class 1259 OID 246408)
-- Name: provider_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_contacts (
    provider_id uuid,
    name character varying(100),
    phone character varying(50),
    email character varying(100),
    "position" character varying(100),
    is_primary boolean DEFAULT false,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_contacts OWNER TO postgres;

--
-- TOC entry 424 (class 1259 OID 246413)
-- Name: provider_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_documents (
    provider_id uuid,
    document_type character varying(100),
    file_url text,
    expires_at date,
    uploaded_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_documents OWNER TO postgres;

--
-- TOC entry 425 (class 1259 OID 246420)
-- Name: provider_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_flags (
    provider_id uuid,
    flag_type character varying(100),
    flag_reason text,
    flagged_by integer,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_flags OWNER TO postgres;

--
-- TOC entry 426 (class 1259 OID 246427)
-- Name: provider_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_images (
    provider_id uuid,
    image_url text,
    label text,
    uploaded_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_images OWNER TO postgres;

--
-- TOC entry 427 (class 1259 OID 246434)
-- Name: provider_network_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_network_assignments (
    provider_network_id uuid,
    company_id uuid,
    group_id uuid,
    contract_id uuid,
    member_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_network_assignments OWNER TO postgres;

--
-- TOC entry 428 (class 1259 OID 246440)
-- Name: provider_network_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_network_members (
    provider_id uuid,
    provider_network_id uuid,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_network_members OWNER TO postgres;

--
-- TOC entry 429 (class 1259 OID 246446)
-- Name: provider_networks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_networks (
    code character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    type character varying(20),
    company_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT provider_networks_type_check CHECK (((type)::text = ANY (ARRAY[('medical'::character varying)::text, ('motor'::character varying)::text])))
);


ALTER TABLE public.provider_networks OWNER TO postgres;

--
-- TOC entry 430 (class 1259 OID 246456)
-- Name: provider_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_ratings (
    provider_id uuid,
    member_id uuid,
    rating integer,
    comment text,
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT provider_ratings_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.provider_ratings OWNER TO postgres;

--
-- TOC entry 431 (class 1259 OID 246464)
-- Name: provider_service_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_service_prices (
    provider_id uuid,
    service_tag character varying(100),
    price numeric(10,2),
    currency character varying(10) DEFAULT 'USD'::character varying,
    is_discounted boolean DEFAULT false,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_service_prices OWNER TO postgres;

--
-- TOC entry 432 (class 1259 OID 246474)
-- Name: provider_services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_services (
    provider_id uuid,
    service_tag character varying(100),
    created_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_services OWNER TO postgres;

--
-- TOC entry 433 (class 1259 OID 246479)
-- Name: provider_specialties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_specialties (
    provider_id uuid,
    specialty text NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_specialties OWNER TO postgres;

--
-- TOC entry 434 (class 1259 OID 246485)
-- Name: provider_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_tags (
    provider_id uuid,
    tag text NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_tags OWNER TO postgres;

--
-- TOC entry 435 (class 1259 OID 246491)
-- Name: provider_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_types (
    code character varying(50) NOT NULL,
    label character varying(100) NOT NULL,
    description text,
    category character varying(20),
    icon text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT provider_types_category_check CHECK (((category)::text = ANY (ARRAY[('medical'::character varying)::text, ('motor'::character varying)::text])))
);


ALTER TABLE public.provider_types OWNER TO postgres;

--
-- TOC entry 436 (class 1259 OID 246501)
-- Name: provider_working_hours; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.provider_working_hours (
    provider_id uuid,
    day_of_week character varying(10),
    opens_at time without time zone,
    closes_at time without time zone,
    is_closed boolean DEFAULT false,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.provider_working_hours OWNER TO postgres;

--
-- TOC entry 437 (class 1259 OID 246506)
-- Name: providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.providers (
    name character varying(255) NOT NULL,
    provider_type_id uuid,
    email character varying(100),
    phone character varying(50),
    address text,
    city_id uuid,
    latitude double precision,
    longitude double precision,
    rating numeric(3,2) DEFAULT 0.0,
    logo_url text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.providers OWNER TO postgres;

--
-- TOC entry 538 (class 1259 OID 247871)
-- Name: public_card_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.public_card_views (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    card_type character varying(50) NOT NULL,
    card_id uuid NOT NULL,
    public_token uuid DEFAULT gen_random_uuid() NOT NULL,
    qr_code_url text,
    expires_at timestamp without time zone,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    qr_style_id uuid
);


ALTER TABLE public.public_card_views OWNER TO postgres;

--
-- TOC entry 541 (class 1259 OID 247906)
-- Name: qr_styles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qr_styles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_type character varying(50),
    owner_id uuid,
    foreground_color character varying(20) DEFAULT '#000000'::character varying,
    background_color character varying(20) DEFAULT '#FFFFFF'::character varying,
    logo_url text,
    border_size integer DEFAULT 4,
    image_format character varying(10) DEFAULT 'png'::character varying,
    caption_text text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.qr_styles OWNER TO postgres;

--
-- TOC entry 540 (class 1259 OID 247897)
-- Name: qr_view_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qr_view_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    public_token uuid NOT NULL,
    viewer_ip inet,
    viewer_user_agent text,
    viewed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    referrer_url text,
    notes text
);


ALTER TABLE public.qr_view_logs OWNER TO postgres;

--
-- TOC entry 438 (class 1259 OID 246516)
-- Name: quantum_algorithms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quantum_algorithms (
    algorithm_name character varying(100) NOT NULL,
    quantum_advantage_type character varying(50),
    qubit_requirements integer,
    circuit_depth integer,
    gate_count integer,
    error_tolerance numeric(10,8),
    classical_complexity character varying(50),
    quantum_complexity character varying(50),
    use_cases jsonb,
    implementation_status character varying(30),
    hardware_requirements jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quantum_algorithms OWNER TO postgres;

--
-- TOC entry 439 (class 1259 OID 246523)
-- Name: quantum_computations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quantum_computations (
    algorithm_id uuid,
    computation_type character varying(50),
    input_parameters jsonb,
    quantum_circuit jsonb,
    execution_time_ms integer,
    quantum_advantage_factor numeric(8,4),
    fidelity_score numeric(5,4),
    error_rate numeric(8,6),
    classical_benchmark_time integer,
    results jsonb,
    executed_on character varying(100),
    executed_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quantum_computations OWNER TO postgres;

--
-- TOC entry 440 (class 1259 OID 246531)
-- Name: quantum_safe_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quantum_safe_keys (
    key_id uuid DEFAULT gen_random_uuid(),
    algorithm_id uuid,
    key_usage character varying(50),
    public_key bytea,
    private_key_reference character varying(200),
    key_generation_timestamp timestamp with time zone DEFAULT now(),
    expiration_timestamp timestamp with time zone,
    revocation_timestamp timestamp with time zone,
    key_status character varying(30) DEFAULT 'active'::character varying,
    associated_entity_type character varying(50),
    associated_entity_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.quantum_safe_keys OWNER TO postgres;

--
-- TOC entry 441 (class 1259 OID 246541)
-- Name: quotation_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_attachments (
    quotation_id uuid,
    file_name text NOT NULL,
    file_url text NOT NULL,
    file_type text,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    uploaded_by uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_attachments OWNER TO postgres;

--
-- TOC entry 442 (class 1259 OID 246548)
-- Name: quotation_audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_audit_log (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    user_id uuid,
    action_type character varying(50) NOT NULL,
    action_details text,
    changed_values jsonb,
    ip_address character varying(45),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.quotation_audit_log OWNER TO postgres;

--
-- TOC entry 443 (class 1259 OID 246555)
-- Name: quotation_coverage_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_coverage_options (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    coverage_option_id uuid NOT NULL,
    calculated_price numeric(15,2) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_coverage_options OWNER TO postgres;

--
-- TOC entry 444 (class 1259 OID 246560)
-- Name: quotation_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_documents (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    document_type character varying(50) NOT NULL,
    document_name character varying(255) NOT NULL,
    file_path text,
    generated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    version integer DEFAULT 1,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_documents OWNER TO postgres;

--
-- TOC entry 445 (class 1259 OID 246569)
-- Name: quotation_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_factors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid NOT NULL,
    key character varying(100) NOT NULL,
    value text NOT NULL,
    factor_type character varying(50),
    impact_description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_factors OWNER TO postgres;

--
-- TOC entry 446 (class 1259 OID 246576)
-- Name: quotation_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid,
    coverage_name text,
    coverage_name_ar text,
    limit_amount numeric(12,2),
    notes text,
    notes_ar text,
    display_order integer DEFAULT 0,
    meta_data jsonb DEFAULT '{}'::jsonb,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_items OWNER TO postgres;

--
-- TOC entry 447 (class 1259 OID 246584)
-- Name: quotation_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid,
    status_from character varying(50),
    status_to character varying(50),
    actor_id uuid,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.quotation_logs OWNER TO postgres;

--
-- TOC entry 448 (class 1259 OID 246591)
-- Name: quotation_pricing_profile_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_profile_rules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    profile_id uuid NOT NULL,
    rule_id uuid NOT NULL,
    order_index integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_pricing_profile_rules OWNER TO postgres;

--
-- TOC entry 449 (class 1259 OID 246599)
-- Name: quotation_pricing_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_profiles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    insurance_type character varying(50) NOT NULL,
    description text,
    notes text,
    currency_code character varying(3) DEFAULT 'USD'::character varying,
    base_premium numeric(15,2),
    min_premium numeric(15,2),
    max_premium numeric(15,2),
    risk_formula text,
    is_default boolean DEFAULT false,
    version integer DEFAULT 1,
    created_by character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by character varying(100),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    archived_at timestamp without time zone,
    CONSTRAINT quotation_pricing_profiles_currency_code_check CHECK (((currency_code)::text ~ '^[A-Z]{3}$'::text))
);


ALTER TABLE public.quotation_pricing_profiles OWNER TO postgres;

--
-- TOC entry 450 (class 1259 OID 246611)
-- Name: quotation_pricing_profiles_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_profiles_history (
    history_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    profile_id uuid NOT NULL,
    operation character varying(10) NOT NULL,
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    changed_by character varying(100),
    old_data jsonb,
    new_data jsonb,
    CONSTRAINT quotation_pricing_profiles_history_operation_check CHECK (((operation)::text = ANY (ARRAY[('INSERT'::character varying)::text, ('UPDATE'::character varying)::text, ('DELETE'::character varying)::text])))
);


ALTER TABLE public.quotation_pricing_profiles_history OWNER TO postgres;

--
-- TOC entry 451 (class 1259 OID 246619)
-- Name: quotation_pricing_rule_age_brackets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_rule_age_brackets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    rule_id uuid NOT NULL,
    age_bracket_id uuid NOT NULL,
    multiplier numeric(8,4) DEFAULT 1.0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_pricing_rule_age_brackets OWNER TO postgres;

--
-- TOC entry 452 (class 1259 OID 246625)
-- Name: quotation_pricing_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_rules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    insurance_type character varying(50) NOT NULL,
    rule_name character varying(255) NOT NULL,
    description text,
    base_premium numeric(15,2),
    min_premium numeric(15,2),
    max_premium numeric(15,2),
    currency_code character varying(3) DEFAULT 'USD'::character varying,
    applies_to character varying(50),
    comparison_operator character varying(10),
    value text,
    adjustment_type character varying(20),
    adjustment_value numeric(15,4),
    formula_expression text,
    formula_variables jsonb,
    is_active boolean DEFAULT true,
    effective_from timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    effective_to timestamp with time zone,
    priority integer DEFAULT 0,
    version integer DEFAULT 1,
    created_by character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by character varying(100),
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    archived_at timestamp without time zone,
    CONSTRAINT quotation_pricing_rules_adjectment_type_check CHECK (((adjustment_type)::text = ANY (ARRAY[('PERCENTAGE'::character varying)::text, ('FIXED_AMOUNT'::character varying)::text, ('MULTIPLIER'::character varying)::text, ('FORMULA'::character varying)::text]))),
    CONSTRAINT quotation_pricing_rules_comparison_operator_check CHECK (((comparison_operator)::text = ANY (ARRAY[('='::character varying)::text, ('!='::character varying)::text, ('>'::character varying)::text, ('>='::character varying)::text, ('<'::character varying)::text, ('<='::character varying)::text, ('IN'::character varying)::text, ('NOT IN'::character varying)::text, ('BETWEEN'::character varying)::text]))),
    CONSTRAINT quotation_pricing_rules_currency_code_check CHECK (((currency_code)::text ~ '^[A-Z]{3}$'::text)),
    CONSTRAINT valid_effective_range CHECK (((effective_to IS NULL) OR (effective_from < effective_to)))
);


ALTER TABLE public.quotation_pricing_rules OWNER TO postgres;

--
-- TOC entry 453 (class 1259 OID 246642)
-- Name: quotation_pricing_rules_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_pricing_rules_history (
    history_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    rule_id uuid NOT NULL,
    operation character varying(10) NOT NULL,
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    changed_by character varying(100),
    old_data jsonb,
    new_data jsonb,
    CONSTRAINT quotation_pricing_rules_history_operation_check CHECK (((operation)::text = ANY (ARRAY[('INSERT'::character varying)::text, ('UPDATE'::character varying)::text, ('DELETE'::character varying)::text])))
);


ALTER TABLE public.quotation_pricing_rules_history OWNER TO postgres;

--
-- TOC entry 454 (class 1259 OID 246650)
-- Name: quotation_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_versions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quotation_id uuid,
    version_number integer,
    data_snapshot jsonb,
    is_latest_version boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.quotation_versions OWNER TO postgres;

--
-- TOC entry 455 (class 1259 OID 246658)
-- Name: quotation_workflow_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotation_workflow_logs (
    quotation_id uuid,
    event text NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.quotation_workflow_logs OWNER TO postgres;

--
-- TOC entry 456 (class 1259 OID 246665)
-- Name: quotations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quotations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    quote_number character varying(50),
    customer_name text,
    customer_email text,
    customer_phone text,
    channel character varying(50),
    lead_source character varying(100),
    assigned_to_user_id uuid,
    follow_up_date date,
    last_contacted_at timestamp without time zone,
    auto_expire_at timestamp without time zone,
    is_locked boolean DEFAULT false,
    converted_policy_id uuid,
    ai_score numeric(5,2),
    risk_score numeric(5,2),
    summary_generated boolean DEFAULT false,
    summary_text text,
    quote_bundle_id uuid,
    tags text[],
    metadata jsonb DEFAULT '{}'::jsonb,
    status character varying(50) DEFAULT 'draft'::character varying,
    created_by uuid,
    updated_by integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    customer_national_id character varying,
    customer_date_of_birth date,
    customer_address text,
    campaign_id uuid,
    referral_code character varying(50),
    assigned_team_id uuid,
    priority_level character varying(50),
    policy_type_id uuid,
    plan_id uuid,
    product_code character varying(50),
    base_premium numeric(12,2),
    discount_amount numeric(12,2),
    surcharge_amount numeric(12,2),
    fees_amount numeric(12,2),
    tax_amount numeric(12,2),
    items_premium numeric(12,2),
    total_premium numeric(12,2),
    currency_code character varying(10),
    valid_from date,
    valid_to date,
    quote_expires_at timestamp without time zone,
    submitted_at timestamp without time zone,
    approved_at timestamp without time zone,
    converted_at timestamp without time zone,
    lock_reason text,
    locked_by integer,
    locked_at timestamp without time zone,
    parent_quotation_id uuid,
    renewal_quotation_id uuid,
    fraud_score numeric(5,2),
    priority_score numeric(5,2),
    terms_conditions text,
    special_conditions text,
    rejection_reason text,
    cancellation_reason text,
    external_ref_id character varying(100),
    source_system character varying(100),
    version integer,
    is_latest_version boolean DEFAULT true,
    reference_number character varying(50),
    profile_id uuid,
    final_premium numeric(15,2),
    base_currency character varying(3) DEFAULT 'USD'::character varying,
    converted_premium numeric(15,2),
    exchange_rate_used numeric(12,6),
    group_size integer,
    customer_id uuid,
    version_notes text,
    assigned_to_user_id_uuid uuid,
    archived_at timestamp without time zone,
    CONSTRAINT quotations_currency_code_check CHECK (((currency_code)::text ~ '^[A-Z]{3}$'::text)),
    CONSTRAINT quotations_status_check CHECK (((status)::text = ANY (ARRAY[('DRAFT'::character varying)::text, ('CALCULATED'::character varying)::text, ('APPROVED'::character varying)::text, ('REJECTED'::character varying)::text, ('EXPIRED'::character varying)::text, ('draft'::character varying)::text, ('submitted'::character varying)::text, ('approved'::character varying)::text, ('converted'::character varying)::text])))
);


ALTER TABLE public.quotations OWNER TO postgres;

--
-- TOC entry 457 (class 1259 OID 246681)
-- Name: rating_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rating_factors (
    factor_name character varying(100) NOT NULL,
    factor_code character varying(20) NOT NULL,
    product_type character varying(50),
    factor_type character varying(30),
    data_type character varying(20),
    min_value numeric(15,4),
    max_value numeric(15,4),
    default_value numeric(15,4),
    relativities jsonb,
    is_mandatory boolean DEFAULT false,
    effective_from date DEFAULT CURRENT_DATE,
    effective_to date,
    regulatory_filed boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.rating_factors OWNER TO postgres;

--
-- TOC entry 458 (class 1259 OID 246691)
-- Name: real_time_catastrophe_monitoring; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.real_time_catastrophe_monitoring (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid,
    detection_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    event_type character varying(50),
    severity_level integer,
    confidence_score numeric(5,4),
    affected_area public.geometry(MultiPolygon,4326),
    estimated_damage_usd numeric(18,2),
    population_at_risk integer,
    properties_at_risk integer,
    alert_level character varying(20),
    source_data_references jsonb,
    automated_response_actions jsonb,
    human_verification_status character varying(30),
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.real_time_catastrophe_monitoring OWNER TO postgres;

--
-- TOC entry 459 (class 1259 OID 246699)
-- Name: real_time_fraud_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.real_time_fraud_scores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type character varying(50),
    entity_id uuid,
    model_id uuid,
    fraud_probability numeric(8,6),
    risk_level character varying(20),
    contributing_factors jsonb,
    anomaly_indicators jsonb,
    investigation_priority integer,
    human_review_required boolean DEFAULT false,
    model_explanation jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.real_time_fraud_scores OWNER TO postgres;

--
-- TOC entry 460 (class 1259 OID 246707)
-- Name: real_time_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.real_time_recommendations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    model_id uuid,
    session_id character varying(100),
    recommendation_type character varying(50),
    recommended_items jsonb,
    confidence_scores jsonb,
    explanation jsonb,
    context_factors jsonb,
    presented boolean DEFAULT false,
    clicked boolean DEFAULT false,
    converted boolean DEFAULT false,
    feedback_score integer,
    generated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.real_time_recommendations OWNER TO postgres;

--
-- TOC entry 461 (class 1259 OID 246717)
-- Name: recommendation_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recommendation_models (
    model_name character varying(100) NOT NULL,
    recommendation_type character varying(50),
    algorithm_type character varying(50),
    model_parameters jsonb,
    training_data_features jsonb,
    accuracy_metrics jsonb,
    real_time_capable boolean DEFAULT true,
    cold_start_strategy jsonb,
    explanation_capability boolean DEFAULT true,
    last_retrained timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.recommendation_models OWNER TO postgres;

--
-- TOC entry 462 (class 1259 OID 246726)
-- Name: regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regions (
    country_id uuid,
    name character varying(255) NOT NULL,
    code character varying(50),
    is_active boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regions OWNER TO postgres;

--
-- TOC entry 463 (class 1259 OID 246731)
-- Name: regulatory_compliance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulatory_compliance (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    region character varying(50) NOT NULL,
    insurance_type character varying(50) NOT NULL,
    requirement_name character varying(255) NOT NULL,
    description text,
    compliance_value text,
    effective_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regulatory_compliance OWNER TO postgres;

--
-- TOC entry 464 (class 1259 OID 246738)
-- Name: regulatory_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulatory_flags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type text,
    entity_id uuid,
    flag_type text,
    flag_value text,
    effective_date date,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regulatory_flags OWNER TO postgres;

--
-- TOC entry 465 (class 1259 OID 246745)
-- Name: regulatory_frameworks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulatory_frameworks (
    framework_name character varying(100) NOT NULL,
    jurisdiction character varying(50),
    regulator character varying(100),
    version character varying(20),
    effective_date date,
    description text,
    reporting_requirements jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regulatory_frameworks OWNER TO postgres;

--
-- TOC entry 466 (class 1259 OID 246753)
-- Name: regulatory_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulatory_reports (
    report_name character varying(100) NOT NULL,
    framework_id uuid,
    report_type character varying(50),
    company_id uuid,
    reporting_period_start date,
    reporting_period_end date,
    due_date date,
    filing_date date,
    status character varying(30) DEFAULT 'draft'::character varying,
    report_data jsonb,
    validation_results jsonb,
    submission_reference character varying(100),
    prepared_by uuid,
    reviewed_by uuid,
    submitted_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regulatory_reports OWNER TO postgres;

--
-- TOC entry 467 (class 1259 OID 246761)
-- Name: regulatory_requirements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regulatory_requirements (
    framework_id uuid,
    requirement_code character varying(50),
    requirement_name character varying(200),
    requirement_type character varying(50),
    description text,
    calculation_method text,
    frequency character varying(20),
    threshold_values jsonb,
    is_mandatory boolean DEFAULT true,
    effective_from date,
    effective_to date,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.regulatory_requirements OWNER TO postgres;

--
-- TOC entry 468 (class 1259 OID 246769)
-- Name: reinsurance_agreements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reinsurance_agreements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    reinsurer_name text NOT NULL,
    agreement_type text NOT NULL,
    quota_share numeric(5,2),
    retention_limit numeric(12,2),
    excess_limit numeric(12,2),
    start_date date,
    end_date date,
    status text DEFAULT 'active'::text,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT reinsurance_agreements_agreement_type_check CHECK ((agreement_type = ANY (ARRAY['quota_share'::text, 'excess_of_loss'::text, 'facultative'::text])))
);


ALTER TABLE public.reinsurance_agreements OWNER TO postgres;

--
-- TOC entry 469 (class 1259 OID 246778)
-- Name: reinsurance_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reinsurance_claims (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    claim_id uuid,
    agreement_id uuid,
    ceded_amount numeric(12,2),
    retained_amount numeric(12,2),
    paid_by_reinsurer numeric(12,2),
    recovery_status text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT reinsurance_claims_recovery_status_check CHECK ((recovery_status = ANY (ARRAY['pending'::text, 'recovered'::text, 'partial'::text, 'denied'::text])))
);


ALTER TABLE public.reinsurance_claims OWNER TO postgres;

--
-- TOC entry 470 (class 1259 OID 246786)
-- Name: reinsurance_commissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reinsurance_commissions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    commission_type text,
    rate numeric(5,2),
    cap numeric(12,2),
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT reinsurance_commissions_commission_type_check CHECK ((commission_type = ANY (ARRAY['sliding_scale'::text, 'flat'::text, 'no_commission'::text])))
);


ALTER TABLE public.reinsurance_commissions OWNER TO postgres;

--
-- TOC entry 471 (class 1259 OID 246794)
-- Name: reinsurance_partners; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reinsurance_partners (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    code text,
    contact_email text,
    rating text,
    type text,
    logo_url text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.reinsurance_partners OWNER TO postgres;

--
-- TOC entry 640 (class 1259 OID 250781)
-- Name: report_analytics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_analytics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_id uuid,
    report_instance_id uuid,
    analytics_date date DEFAULT CURRENT_DATE,
    generation_count integer DEFAULT 0,
    view_count integer DEFAULT 0,
    download_count integer DEFAULT 0,
    share_count integer DEFAULT 0,
    average_generation_time_seconds numeric(10,2),
    error_rate_percentage numeric(5,2),
    user_satisfaction_score numeric(3,2),
    popular_filters jsonb DEFAULT '{}'::jsonb,
    performance_metrics jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT report_analytics_error_rate_percentage_check CHECK (((error_rate_percentage >= 0.0) AND (error_rate_percentage <= 100.0))),
    CONSTRAINT report_analytics_user_satisfaction_score_check CHECK (((user_satisfaction_score >= 1.0) AND (user_satisfaction_score <= 5.0)))
);


ALTER TABLE public.report_analytics OWNER TO postgres;

--
-- TOC entry 639 (class 1259 OID 250758)
-- Name: report_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    report_instance_id uuid NOT NULL,
    component_id character varying(100),
    user_id uuid,
    comment_text text NOT NULL,
    comment_type character varying(30) DEFAULT 'general'::character varying,
    position_data jsonb DEFAULT '{}'::jsonb,
    parent_comment_id uuid,
    is_resolved boolean DEFAULT false,
    resolved_by uuid,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp without time zone,
    CONSTRAINT report_comments_comment_type_check CHECK (((comment_type)::text = ANY ((ARRAY['general'::character varying, 'question'::character varying, 'insight'::character varying, 'action_item'::character varying, 'bug'::character varying, 'enhancement'::character varying])::text[])))
);


ALTER TABLE public.report_comments OWNER TO postgres;

--
-- TOC entry 635 (class 1259 OID 250673)
-- Name: report_components; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_components (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    component_name character varying(100) NOT NULL,
    component_type character varying(50) NOT NULL,
    component_category character varying(50),
    component_config jsonb DEFAULT '{}'::jsonb,
    default_settings jsonb DEFAULT '{}'::jsonb,
    data_binding_schema jsonb DEFAULT '{}'::jsonb,
    styling_options jsonb DEFAULT '{}'::jsonb,
    icon_url character varying(500),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp without time zone,
    CONSTRAINT report_components_component_type_check CHECK (((component_type)::text = ANY ((ARRAY['chart'::character varying, 'table'::character varying, 'kpi_card'::character varying, 'filter'::character varying, 'text'::character varying, 'image'::character varying, 'gauge'::character varying, 'map'::character varying])::text[])))
);


ALTER TABLE public.report_components OWNER TO postgres;

--
-- TOC entry 641 (class 1259 OID 250809)
-- Name: report_favorites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_favorites (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    template_id uuid,
    report_instance_id uuid,
    favorite_type character varying(20) DEFAULT 'template'::character varying,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT report_favorites_favorite_type_check CHECK (((favorite_type)::text = ANY ((ARRAY['template'::character varying, 'instance'::character varying])::text[])))
);


ALTER TABLE public.report_favorites OWNER TO postgres;

--
-- TOC entry 636 (class 1259 OID 250690)
-- Name: report_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_instances (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_id uuid,
    report_name character varying(200) NOT NULL,
    generated_by uuid,
    generation_method character varying(30) DEFAULT 'manual'::character varying,
    parameters_used jsonb DEFAULT '{}'::jsonb,
    filters_applied jsonb DEFAULT '{}'::jsonb,
    data_snapshot_date timestamp with time zone,
    generation_status character varying(30) DEFAULT 'generating'::character varying,
    file_format character varying(20),
    file_path character varying(500),
    file_size_bytes bigint,
    generation_time_seconds integer,
    download_count integer DEFAULT 0,
    expires_at timestamp with time zone,
    is_cached boolean DEFAULT false,
    cache_key character varying(200),
    created_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    error_message text,
    CONSTRAINT report_instances_file_format_check CHECK (((file_format)::text = ANY ((ARRAY['pdf'::character varying, 'excel'::character varying, 'csv'::character varying, 'json'::character varying, 'html'::character varying, 'png'::character varying, 'jpg'::character varying])::text[]))),
    CONSTRAINT report_instances_generation_method_check CHECK (((generation_method)::text = ANY ((ARRAY['manual'::character varying, 'scheduled'::character varying, 'api'::character varying, 'automated'::character varying])::text[]))),
    CONSTRAINT report_instances_generation_status_check CHECK (((generation_status)::text = ANY ((ARRAY['generating'::character varying, 'completed'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.report_instances OWNER TO postgres;

--
-- TOC entry 637 (class 1259 OID 250715)
-- Name: report_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_id uuid,
    schedule_name character varying(200) NOT NULL,
    schedule_expression character varying(100),
    parameters jsonb DEFAULT '{}'::jsonb,
    recipients jsonb DEFAULT '{}'::jsonb,
    delivery_method character varying(30) DEFAULT 'email'::character varying,
    file_formats character varying(50)[] DEFAULT ARRAY['pdf'::text],
    is_active boolean DEFAULT true,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    success_count integer DEFAULT 0,
    failure_count integer DEFAULT 0,
    last_error_message text,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    CONSTRAINT report_schedules_delivery_method_check CHECK (((delivery_method)::text = ANY ((ARRAY['email'::character varying, 'ftp'::character varying, 'api'::character varying, 'portal'::character varying, 'webhook'::character varying])::text[])))
);


ALTER TABLE public.report_schedules OWNER TO postgres;

--
-- TOC entry 638 (class 1259 OID 250739)
-- Name: report_shares; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_shares (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    report_instance_id uuid,
    shared_by uuid,
    shared_with_type character varying(20),
    shared_with_id uuid,
    access_level character varying(20) DEFAULT 'read'::character varying,
    share_token character varying(100),
    expires_at timestamp with time zone,
    access_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT report_shares_access_level_check CHECK (((access_level)::text = ANY ((ARRAY['read'::character varying, 'comment'::character varying, 'edit'::character varying, 'admin'::character varying])::text[]))),
    CONSTRAINT report_shares_shared_with_type_check CHECK (((shared_with_type)::text = ANY ((ARRAY['user'::character varying, 'role'::character varying, 'department'::character varying, 'public'::character varying, 'group'::character varying])::text[])))
);


ALTER TABLE public.report_shares OWNER TO postgres;

--
-- TOC entry 472 (class 1259 OID 246801)
-- Name: report_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_templates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    query text NOT NULL,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    template_name character varying(200),
    template_category character varying(50),
    template_type character varying(50),
    template_description text,
    visual_layout jsonb,
    data_sources jsonb,
    sql_query text,
    parameters jsonb,
    default_filters jsonb,
    permissions jsonb,
    is_public boolean DEFAULT false,
    is_prebuilt boolean DEFAULT false,
    usage_count integer DEFAULT 0
);


ALTER TABLE public.report_templates OWNER TO postgres;

--
-- TOC entry 473 (class 1259 OID 246808)
-- Name: retention_forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.retention_forecasts (
    company_id uuid,
    forecast_model character varying(100),
    customer_segment_id uuid,
    forecast_period_start date,
    forecast_period_end date,
    predicted_retention_rate numeric(5,4),
    confidence_interval_lower numeric(5,4),
    confidence_interval_upper numeric(5,4),
    month_1_retention numeric(5,4),
    month_3_retention numeric(5,4),
    month_6_retention numeric(5,4),
    month_12_retention numeric(5,4),
    month_24_retention numeric(5,4),
    expected_revenue_retained numeric(15,2),
    expected_customers_retained integer,
    retention_improvement_opportunities jsonb,
    model_accuracy numeric(5,4),
    historical_validation jsonb,
    feature_importance jsonb,
    forecast_generated_at timestamp with time zone DEFAULT now(),
    valid_until timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.retention_forecasts OWNER TO postgres;

--
-- TOC entry 474 (class 1259 OID 246816)
-- Name: risk_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_assessments (
    entity_type character varying(50),
    entity_id uuid,
    assessment_date date DEFAULT CURRENT_DATE,
    overall_risk_score numeric(5,2),
    risk_level public.risk_level,
    risk_factors jsonb,
    assessment_method character varying(50),
    valid_until date,
    assessed_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    factors text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.risk_assessments OWNER TO postgres;

--
-- TOC entry 475 (class 1259 OID 246824)
-- Name: risk_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_factors (
    factor_name character varying(100) NOT NULL,
    factor_category character varying(50),
    data_type character varying(20),
    calculation_method text,
    weight numeric DEFAULT 1.0,
    min_value numeric(15,4),
    max_value numeric(15,4),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    impact_score numeric,
    name character varying,
    description text,
    factor_type character varying,
    applies_to character varying,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.risk_factors OWNER TO postgres;

--
-- TOC entry 476 (class 1259 OID 246833)
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id uuid,
    permission_id uuid,
    role_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- TOC entry 477 (class 1259 OID 246836)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    old_id uuid,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    user_type character varying(20),
    department character varying(50),
    unit character varying(50),
    access_level character varying(20) DEFAULT 'standard'::character varying,
    is_manager boolean DEFAULT false
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 478 (class 1259 OID 246843)
-- Name: roles_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles_backup (
    name character varying(50),
    description text,
    created_at timestamp with time zone,
    id uuid,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.roles_backup OWNER TO postgres;

--
-- TOC entry 576 (class 1259 OID 248962)
-- Name: saas_feature_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_feature_flags (
    id uuid NOT NULL,
    code character varying(100),
    name character varying(100),
    description text,
    is_active boolean DEFAULT true
);


ALTER TABLE public.saas_feature_flags OWNER TO postgres;

--
-- TOC entry 577 (class 1259 OID 248972)
-- Name: saas_plan_features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_plan_features (
    id uuid NOT NULL,
    saas_plan_id uuid,
    feature_flag_id uuid,
    is_enabled boolean DEFAULT true
);


ALTER TABLE public.saas_plan_features OWNER TO postgres;

--
-- TOC entry 575 (class 1259 OID 248951)
-- Name: saas_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saas_plans (
    id uuid NOT NULL,
    code character varying(100),
    name character varying(100) NOT NULL,
    description text,
    price numeric(10,2),
    billing_cycle character varying(20),
    max_users integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.saas_plans OWNER TO postgres;

--
-- TOC entry 479 (class 1259 OID 246848)
-- Name: satellite_imagery; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.satellite_imagery (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    provider_id uuid,
    image_id character varying(200) NOT NULL,
    capture_timestamp timestamp with time zone NOT NULL,
    geographic_bounds public.geometry(Polygon,4326),
    resolution_meters numeric(8,4),
    cloud_coverage_percentage numeric(5,2),
    image_url character varying(500),
    metadata jsonb,
    processing_level character varying(20),
    atmospheric_correction boolean DEFAULT false,
    quality_score numeric(3,2),
    download_cost numeric(10,4),
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.satellite_imagery OWNER TO postgres;

--
-- TOC entry 480 (class 1259 OID 246856)
-- Name: satellite_providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.satellite_providers (
    provider_name character varying(100) NOT NULL,
    satellite_constellation character varying(100),
    resolution_meters numeric(8,4),
    revisit_frequency_days integer,
    spectral_bands jsonb,
    data_types jsonb,
    api_endpoint character varying(200),
    pricing_model jsonb,
    coverage_area public.geometry(MultiPolygon,4326),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.satellite_providers OWNER TO postgres;

--
-- TOC entry 481 (class 1259 OID 246864)
-- Name: scheduled_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scheduled_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_name text NOT NULL,
    payload jsonb,
    status text DEFAULT 'pending'::text,
    scheduled_for timestamp without time zone,
    executed_at timestamp without time zone,
    result text
);


ALTER TABLE public.scheduled_tasks OWNER TO postgres;

--
-- TOC entry 482 (class 1259 OID 246871)
-- Name: security_incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_incidents (
    incident_type character varying(50),
    severity character varying(20),
    user_id uuid,
    ip_address inet,
    description text,
    evidence jsonb,
    status character varying(30) DEFAULT 'open'::character varying,
    assigned_to uuid,
    resolved_at timestamp with time zone,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.security_incidents OWNER TO postgres;

--
-- TOC entry 483 (class 1259 OID 246879)
-- Name: security_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_sessions (
    user_id uuid,
    session_id character varying(255) NOT NULL,
    device_fingerprint text,
    ip_address inet,
    user_agent text,
    location_data jsonb,
    trust_score integer DEFAULT 50,
    risk_indicators jsonb,
    is_active boolean DEFAULT true,
    last_activity timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.security_sessions OWNER TO postgres;

--
-- TOC entry 612 (class 1259 OID 250204)
-- Name: serendipity_discoveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.serendipity_discoveries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pattern_id uuid,
    discovery_title character varying(300),
    discovery_description text,
    discovery_type character varying(50),
    significance_score numeric(5,4),
    confidence_level numeric(3,2),
    supporting_data jsonb,
    affected_entities jsonb,
    potential_value_estimate numeric(15,2),
    actionability_score numeric(3,2),
    discovery_date timestamp without time zone DEFAULT now(),
    validation_status character varying(30) DEFAULT 'pending'::character varying,
    validated_by uuid,
    validated_at timestamp without time zone,
    business_impact_actual numeric(15,2),
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.serendipity_discoveries OWNER TO postgres;

--
-- TOC entry 611 (class 1259 OID 250192)
-- Name: serendipity_patterns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.serendipity_patterns (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pattern_name character varying(200) NOT NULL,
    pattern_type character varying(50),
    discovery_algorithm character varying(50),
    data_sources jsonb,
    pattern_definition jsonb,
    significance_threshold numeric(5,4) DEFAULT 0.8,
    discovery_frequency character varying(20) DEFAULT 'daily'::character varying,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.serendipity_patterns OWNER TO postgres;

--
-- TOC entry 613 (class 1259 OID 250220)
-- Name: serendipity_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.serendipity_recommendations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    discovery_id uuid,
    recommendation_type character varying(50),
    recommendation_title character varying(300),
    recommendation_description text,
    priority character varying(20) DEFAULT 'medium'::character varying,
    estimated_effort character varying(20),
    estimated_roi numeric(5,2),
    implementation_complexity character varying(20),
    target_deadline date,
    assigned_to uuid,
    status character varying(30) DEFAULT 'proposed'::character varying,
    implementation_notes text,
    results_metrics jsonb,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.serendipity_recommendations OWNER TO postgres;

--
-- TOC entry 484 (class 1259 OID 246889)
-- Name: session_embeddings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.session_embeddings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id character varying(100) NOT NULL,
    embedding_type character varying(50),
    source_text text,
    embedding public.vector(1536),
    embedding_model character varying(100),
    embedding_version character varying(20),
    token_count integer,
    semantic_tags jsonb,
    importance_score numeric(3,2),
    context_window jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.session_embeddings OWNER TO postgres;

--
-- TOC entry 485 (class 1259 OID 246896)
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    ip_address text,
    device text,
    created_at timestamp without time zone DEFAULT now(),
    last_active_at timestamp without time zone,
    is_active boolean DEFAULT true
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- TOC entry 616 (class 1259 OID 250264)
-- Name: simulation_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scenario_id uuid,
    simulation_run_id character varying(100),
    run_started_at timestamp without time zone,
    run_completed_at timestamp without time zone,
    computation_time_minutes integer,
    results_summary jsonb,
    detailed_results jsonb,
    confidence_metrics jsonb,
    sensitivity_analysis jsonb,
    risk_metrics jsonb,
    recommendations jsonb,
    validation_score numeric(3,2),
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.simulation_results OWNER TO postgres;

--
-- TOC entry 615 (class 1259 OID 250247)
-- Name: simulation_scenarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_scenarios (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    twin_model_id uuid,
    scenario_name character varying(200),
    scenario_type character varying(50),
    scenario_description text,
    input_parameters jsonb,
    simulation_duration_months integer DEFAULT 12,
    monte_carlo_iterations integer DEFAULT 1000,
    scenario_assumptions jsonb,
    confidence_intervals boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.simulation_scenarios OWNER TO postgres;

--
-- TOC entry 617 (class 1259 OID 250278)
-- Name: simulation_validation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulation_validation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    simulation_result_id uuid,
    validation_period_start date,
    validation_period_end date,
    predicted_values jsonb,
    actual_values jsonb,
    accuracy_metrics jsonb,
    model_drift_indicators jsonb,
    calibration_adjustments_needed boolean DEFAULT false,
    validation_notes text,
    validated_by uuid,
    validated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.simulation_validation OWNER TO postgres;

--
-- TOC entry 631 (class 1259 OID 250471)
-- Name: skills_demand_forecast; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skills_demand_forecast (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    skill_id uuid,
    forecast_date date,
    forecast_horizon_years integer DEFAULT 3,
    demand_trend character varying(20),
    demand_growth_rate numeric(5,2),
    industry_demand_score numeric(3,2),
    automation_threat_level character varying(20) DEFAULT 'low'::character varying,
    emergence_factors jsonb,
    confidence_level numeric(3,2),
    data_sources jsonb,
    forecast_model character varying(50),
    created_by uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.skills_demand_forecast OWNER TO postgres;

--
-- TOC entry 633 (class 1259 OID 250498)
-- Name: skills_development_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skills_development_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    employee_id uuid,
    gap_analysis_id uuid,
    target_skills jsonb,
    development_methods jsonb,
    estimated_duration_months integer,
    estimated_cost numeric(10,2),
    priority_ranking integer,
    success_metrics jsonb,
    progress_milestones jsonb,
    assigned_mentor uuid,
    plan_status character varying(30) DEFAULT 'proposed'::character varying,
    start_date date,
    target_completion_date date,
    actual_completion_date date,
    effectiveness_rating numeric(3,2),
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.skills_development_plans OWNER TO postgres;

--
-- TOC entry 632 (class 1259 OID 250487)
-- Name: skills_gap_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skills_gap_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    analysis_name character varying(200),
    department_id uuid,
    analysis_date date DEFAULT CURRENT_DATE,
    current_skills_inventory jsonb,
    future_skills_requirements jsonb,
    identified_gaps jsonb,
    gap_severity_assessment jsonb,
    affected_employee_count integer,
    estimated_impact jsonb,
    recommended_actions jsonb,
    implementation_timeline jsonb,
    budget_requirements jsonb,
    success_metrics jsonb,
    analysis_status character varying(30) DEFAULT 'draft'::character varying,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone
);


ALTER TABLE public.skills_gap_analysis OWNER TO postgres;

--
-- TOC entry 629 (class 1259 OID 250444)
-- Name: skills_taxonomy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skills_taxonomy (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    skill_name character varying(200) NOT NULL,
    skill_category character varying(50),
    skill_subcategory character varying(100),
    skill_description text,
    proficiency_levels jsonb,
    industry_relevance character varying(20) DEFAULT 'high'::character varying,
    technology_dependency character varying(50),
    obsolescence_risk character varying(20) DEFAULT 'low'::character varying,
    learning_difficulty character varying(20) DEFAULT 'medium'::character varying,
    average_acquisition_time_months integer,
    is_active boolean DEFAULT true,
    created_by uuid,
    created_at timestamp without time zone DEFAULT now(),
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.skills_taxonomy OWNER TO postgres;

--
-- TOC entry 486 (class 1259 OID 246904)
-- Name: smart_contracts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smart_contracts (
    contract_name character varying(100) NOT NULL,
    contract_address character varying(42),
    network_id uuid,
    contract_type character varying(50),
    abi jsonb,
    bytecode text,
    deployment_tx_hash character varying(66),
    deployment_block_number bigint,
    gas_used bigint,
    deployment_cost numeric(18,8),
    is_verified boolean DEFAULT false,
    deployed_by integer,
    deployed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.smart_contracts OWNER TO postgres;

--
-- TOC entry 487 (class 1259 OID 246912)
-- Name: smart_home_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smart_home_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    system_id uuid,
    event_type character varying(50),
    severity character varying(20),
    sensor_location character varying(100),
    event_data jsonb,
    automated_response jsonb,
    human_verification_required boolean DEFAULT false,
    emergency_services_notified boolean DEFAULT false,
    insurance_claim_eligible boolean DEFAULT false,
    potential_claim_amount numeric(15,2),
    event_timestamp timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.smart_home_events OWNER TO postgres;

--
-- TOC entry 488 (class 1259 OID 246922)
-- Name: smart_home_systems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smart_home_systems (
    member_id uuid,
    property_address text,
    system_type character varying(50),
    brand character varying(50),
    model character varying(100),
    installation_date date,
    monitoring_plan character varying(30),
    monthly_fee numeric(8,2),
    emergency_contacts jsonb,
    integration_status character varying(30),
    api_credentials jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.smart_home_systems OWNER TO postgres;

--
-- TOC entry 489 (class 1259 OID 246929)
-- Name: speech_analytics_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.speech_analytics_models (
    model_name character varying(100) NOT NULL,
    analysis_type character varying(50),
    language_support text[],
    model_accuracy numeric(5,4),
    real_time_processing boolean DEFAULT true,
    api_endpoint character varying(200),
    cost_per_minute numeric(8,4),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.speech_analytics_models OWNER TO postgres;

--
-- TOC entry 490 (class 1259 OID 246937)
-- Name: states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.states (
    name character varying(100) NOT NULL,
    country_id uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.states OWNER TO postgres;

--
-- TOC entry 491 (class 1259 OID 246941)
-- Name: status_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.status_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type text NOT NULL,
    entity_id uuid NOT NULL,
    previous_status text,
    new_status text,
    changed_by uuid,
    changed_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.status_logs OWNER TO postgres;

--
-- TOC entry 572 (class 1259 OID 248881)
-- Name: support_response_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.support_response_templates (
    id uuid NOT NULL,
    category_id uuid,
    title character varying(100),
    body text,
    language character varying(10)
);


ALTER TABLE public.support_response_templates OWNER TO postgres;

--
-- TOC entry 492 (class 1259 OID 246948)
-- Name: sustainability_indicators; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sustainability_indicators (
    framework_id uuid,
    indicator_code character varying(50),
    indicator_name character varying(200),
    category character varying(50),
    measurement_unit character varying(50),
    calculation_method text,
    data_source_requirements jsonb,
    target_setting_guidance jsonb,
    industry_benchmarks jsonb,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.sustainability_indicators OWNER TO postgres;

--
-- TOC entry 532 (class 1259 OID 247708)
-- Name: system_configuration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_configuration (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    category character varying(50) NOT NULL,
    key character varying(100) NOT NULL,
    value jsonb NOT NULL,
    description text,
    is_encrypted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.system_configuration OWNER TO postgres;

--
-- TOC entry 556 (class 1259 OID 248497)
-- Name: system_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_flags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    flag_name character varying(100) NOT NULL,
    flag_category character varying(50) NOT NULL,
    is_enabled boolean DEFAULT false,
    flag_value jsonb,
    description text NOT NULL,
    company_id uuid,
    environment character varying(20) DEFAULT 'production'::character varying,
    conditions jsonb,
    rollout_percentage numeric(5,2) DEFAULT 100.00,
    target_user_segments character varying(100)[],
    created_date date DEFAULT CURRENT_DATE,
    enabled_date date,
    disabled_date date,
    scheduled_removal_date date,
    usage_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone,
    performance_impact_ms integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid NOT NULL,
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT valid_rollout_percentage CHECK (((rollout_percentage >= (0)::numeric) AND (rollout_percentage <= (100)::numeric)))
);


ALTER TABLE public.system_flags OWNER TO postgres;

--
-- TOC entry 10555 (class 0 OID 0)
-- Dependencies: 556
-- Name: TABLE system_flags; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.system_flags IS 'Feature flags and system configuration for operational control';


--
-- TOC entry 620 (class 1259 OID 250318)
-- Name: system_resilience_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_resilience_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    system_name character varying(100),
    metric_date date DEFAULT CURRENT_DATE,
    availability_percentage numeric(5,2),
    mean_time_to_recovery_minutes integer,
    mean_time_between_failures_hours integer,
    error_rate_percentage numeric(5,2),
    response_time_percentiles jsonb,
    chaos_resilience_score numeric(3,2),
    improvement_trend character varying(20),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.system_resilience_metrics OWNER TO postgres;

--
-- TOC entry 493 (class 1259 OID 246955)
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key text NOT NULL,
    value text,
    description text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- TOC entry 599 (class 1259 OID 249893)
-- Name: telematics_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.telematics_data (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    device_id uuid,
    trip_start timestamp without time zone,
    trip_end timestamp without time zone,
    distance_km numeric(8,2),
    max_speed_kmh numeric(5,1),
    harsh_braking_events integer,
    rapid_acceleration_events integer,
    night_driving_minutes integer,
    safety_score numeric(5,2),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.telematics_data OWNER TO postgres;

--
-- TOC entry 494 (class 1259 OID 246961)
-- Name: template_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_categories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.template_categories OWNER TO postgres;

--
-- TOC entry 495 (class 1259 OID 246967)
-- Name: template_variables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_variables (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_id uuid,
    variable_key text NOT NULL,
    label text,
    sample_value text,
    description text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.template_variables OWNER TO postgres;

--
-- TOC entry 571 (class 1259 OID 248874)
-- Name: ticket_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_categories (
    id uuid NOT NULL,
    name character varying(100),
    description text
);


ALTER TABLE public.ticket_categories OWNER TO postgres;

--
-- TOC entry 570 (class 1259 OID 248860)
-- Name: ticket_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_requests (
    id uuid NOT NULL,
    member_id uuid,
    category character varying(100),
    subject text,
    status character varying(50) DEFAULT 'open'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticket_requests OWNER TO postgres;

--
-- TOC entry 496 (class 1259 OID 246973)
-- Name: time_series_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.time_series_data (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    metric_id uuid,
    entity_type character varying(50),
    entity_id uuid,
    "timestamp" timestamp with time zone NOT NULL,
    value numeric(20,8),
    labels jsonb,
    quality_score numeric(3,2) DEFAULT 1.0,
    is_anomaly boolean DEFAULT false,
    anomaly_score numeric(5,4),
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.time_series_data OWNER TO postgres;

--
-- TOC entry 497 (class 1259 OID 246982)
-- Name: time_series_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.time_series_metrics (
    metric_name character varying(100) NOT NULL,
    metric_category character varying(50),
    data_type character varying(20),
    aggregation_method character varying(30),
    unit_of_measure character varying(50),
    collection_frequency character varying(20),
    retention_period_days integer DEFAULT 365,
    anomaly_detection_enabled boolean DEFAULT true,
    forecasting_enabled boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.time_series_metrics OWNER TO postgres;

--
-- TOC entry 498 (class 1259 OID 246990)
-- Name: training_datasets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_datasets (
    dataset_name character varying(200) NOT NULL,
    dataset_version character varying(50) NOT NULL,
    dataset_type character varying(50),
    description text,
    data_source character varying(100),
    collection_method character varying(100),
    total_samples integer,
    total_size_bytes bigint,
    quality_score numeric(3,2),
    completeness_percentage numeric(5,2),
    accuracy_percentage numeric(5,2),
    consistency_score numeric(3,2),
    feature_schema jsonb,
    target_variables jsonb,
    data_distribution jsonb,
    preprocessing_steps jsonb,
    augmentation_techniques jsonb,
    storage_location character varying(500),
    access_credentials_ref character varying(200),
    format character varying(50),
    contains_pii boolean DEFAULT false,
    privacy_level character varying(20),
    consent_obtained boolean DEFAULT false,
    gdpr_compliant boolean DEFAULT false,
    status character varying(30) DEFAULT 'active'::character varying,
    created_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.training_datasets OWNER TO postgres;

--
-- TOC entry 499 (class 1259 OID 247001)
-- Name: translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.translations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type text NOT NULL,
    entity_id uuid NOT NULL,
    language_code text NOT NULL,
    field text NOT NULL,
    translation text NOT NULL
);


ALTER TABLE public.translations OWNER TO postgres;

--
-- TOC entry 500 (class 1259 OID 247007)
-- Name: translations_enhanced; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.translations_enhanced (
    key_id uuid,
    language_code character varying(10),
    translated_text text NOT NULL,
    translation_status character varying(30) DEFAULT 'draft'::character varying,
    quality_score numeric(3,2),
    translated_by uuid,
    translation_method character varying(30),
    translation_engine character varying(50),
    reviewed_by uuid,
    reviewed_at timestamp with time zone,
    review_notes text,
    version integer DEFAULT 1,
    is_current boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.translations_enhanced OWNER TO postgres;

--
-- TOC entry 501 (class 1259 OID 247018)
-- Name: treaty_cessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.treaty_cessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    period_start date,
    period_end date,
    total_premium numeric(12,2),
    total_claims numeric(12,2),
    net_retention numeric(12,2),
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.treaty_cessions OWNER TO postgres;

--
-- TOC entry 502 (class 1259 OID 247023)
-- Name: treaty_programs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.treaty_programs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    program_name text NOT NULL,
    treaty_type_id uuid,
    year integer,
    notes text,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.treaty_programs OWNER TO postgres;

--
-- TOC entry 597 (class 1259 OID 249376)
-- Name: treaty_reinstatements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.treaty_reinstatements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    reinstatement_number integer NOT NULL,
    trigger_event character varying(200),
    trigger_date date NOT NULL,
    reinstatement_premium numeric(15,2) NOT NULL,
    reinstatement_percentage numeric(8,4),
    available_limit_before numeric(15,2),
    available_limit_after numeric(15,2),
    effective_date date NOT NULL,
    expiry_date date,
    terms_and_conditions text,
    payment_status character varying(20) DEFAULT 'pending'::character varying,
    payment_due_date date,
    paid_date date,
    paid_amount numeric(15,2),
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.treaty_reinstatements OWNER TO postgres;

--
-- TOC entry 10556 (class 0 OID 0)
-- Dependencies: 597
-- Name: TABLE treaty_reinstatements; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.treaty_reinstatements IS 'Treaty limit reinstatements after losses';


--
-- TOC entry 503 (class 1259 OID 247029)
-- Name: treaty_statements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.treaty_statements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    agreement_id uuid,
    statement_date date,
    gross_premium numeric(12,2),
    commission_deducted numeric(12,2),
    loss_recovery numeric(12,2),
    balance_due numeric(12,2),
    status text,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT treaty_statements_status_check CHECK ((status = ANY (ARRAY['sent'::text, 'received'::text, 'settled'::text])))
);


ALTER TABLE public.treaty_statements OWNER TO postgres;

--
-- TOC entry 504 (class 1259 OID 247037)
-- Name: treaty_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.treaty_types (
    name text NOT NULL,
    description text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.treaty_types OWNER TO postgres;

--
-- TOC entry 505 (class 1259 OID 247043)
-- Name: underwriting_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_actions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    profile_id uuid,
    action_type text,
    taken_by uuid,
    notes text,
    taken_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT underwriting_actions_action_type_check CHECK ((action_type = ANY (ARRAY['approve'::text, 'refer'::text, 'reject'::text, 'escalate'::text])))
);


ALTER TABLE public.underwriting_actions OWNER TO postgres;

--
-- TOC entry 506 (class 1259 OID 247051)
-- Name: underwriting_applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_applications (
    application_number character varying(30) NOT NULL,
    member_id uuid,
    product_type character varying(50) NOT NULL,
    application_data jsonb NOT NULL,
    submission_channel character varying(30),
    status character varying(30) DEFAULT 'submitted'::character varying,
    assigned_underwriter uuid,
    priority character varying(20) DEFAULT 'normal'::character varying,
    sla_due_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    policy_id uuid,
    submitted_at timestamp without time zone DEFAULT now(),
    notes text,
    source character varying,
    channel character varying,
    assigned_to uuid,
    decision_at timestamp without time zone,
    estimated_premium numeric,
    premium_score numeric,
    pricing_model_used character varying,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.underwriting_applications OWNER TO postgres;

--
-- TOC entry 507 (class 1259 OID 247062)
-- Name: underwriting_decision_matrix; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_decision_matrix (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    factor_1 text,
    factor_2 text,
    score integer,
    decision text,
    weight numeric(5,2),
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT underwriting_decision_matrix_decision_check CHECK ((decision = ANY (ARRAY['accept'::text, 'reject'::text, 'manual_review'::text])))
);


ALTER TABLE public.underwriting_decision_matrix OWNER TO postgres;

--
-- TOC entry 508 (class 1259 OID 247070)
-- Name: underwriting_decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_decisions (
    application_id uuid,
    rule_id uuid,
    decision public.underwriting_decision NOT NULL,
    risk_score numeric(5,2),
    premium_adjustment numeric(15,2),
    conditions_applied jsonb,
    underwriter_notes text,
    automated boolean DEFAULT true,
    reviewed_by uuid,
    decision_date timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    notes text,
    decided_by uuid,
    decision_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    decision_score numeric,
    decision_notes text,
    decided_at timestamp without time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.underwriting_decisions OWNER TO postgres;

--
-- TOC entry 509 (class 1259 OID 247082)
-- Name: underwriting_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    profile_id uuid,
    document_type text,
    file_url text,
    uploaded_by uuid,
    uploaded_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.underwriting_documents OWNER TO postgres;

--
-- TOC entry 510 (class 1259 OID 247089)
-- Name: underwriting_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_logs (
    application_id uuid,
    action character varying(100),
    performed_by uuid,
    notes text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    log_type character varying,
    log_data jsonb,
    created_by uuid,
    created_at timestamp without time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.underwriting_logs OWNER TO postgres;

--
-- TOC entry 511 (class 1259 OID 247096)
-- Name: underwriting_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    policy_id uuid,
    plan_id uuid,
    quote_id uuid,
    risk_score numeric(5,2),
    decision text,
    notes text,
    created_at timestamp without time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT underwriting_profiles_decision_check CHECK ((decision = ANY (ARRAY['approved'::text, 'referred'::text, 'rejected'::text, 'pending'::text])))
);


ALTER TABLE public.underwriting_profiles OWNER TO postgres;

--
-- TOC entry 512 (class 1259 OID 247104)
-- Name: underwriting_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_rules (
    rule_name character varying(100) NOT NULL,
    product_type character varying(50) NOT NULL,
    rule_category character varying(50),
    priority integer DEFAULT 100,
    conditions jsonb NOT NULL,
    actions jsonb NOT NULL,
    decision_outcome public.underwriting_decision,
    risk_score_impact numeric(5,2) DEFAULT 0,
    premium_adjustment_percentage numeric(5,2) DEFAULT 0,
    coverage_modifications jsonb,
    is_active boolean DEFAULT true,
    effective_from date DEFAULT CURRENT_DATE,
    effective_to date,
    created_by uuid,
    approved_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    name character varying,
    description text,
    condition_json jsonb,
    target_score numeric,
    rule_type character varying,
    applies_to character varying,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.underwriting_rules OWNER TO postgres;

--
-- TOC entry 513 (class 1259 OID 247117)
-- Name: underwriting_workflow_steps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.underwriting_workflow_steps (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text,
    description text,
    order_index integer,
    step_type text,
    is_required boolean DEFAULT true,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone,
    CONSTRAINT underwriting_workflow_steps_step_type_check CHECK ((step_type = ANY (ARRAY['auto'::text, 'manual'::text])))
);


ALTER TABLE public.underwriting_workflow_steps OWNER TO postgres;

--
-- TOC entry 588 (class 1259 OID 249117)
-- Name: units; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.units (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    department_id uuid,
    name character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.units OWNER TO postgres;

--
-- TOC entry 623 (class 1259 OID 250355)
-- Name: universe_outcomes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.universe_outcomes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scenario_id uuid,
    simulation_completed_at timestamp without time zone,
    financial_outcomes jsonb,
    operational_outcomes jsonb,
    risk_outcomes jsonb,
    strategic_outcomes jsonb,
    stakeholder_impact jsonb,
    unintended_consequences jsonb,
    overall_success_score numeric(3,2),
    confidence_level numeric(3,2),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.universe_outcomes OWNER TO postgres;

--
-- TOC entry 624 (class 1259 OID 250369)
-- Name: universe_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.universe_recommendations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    universe_id uuid,
    recommended_scenario_id uuid,
    recommendation_rationale text,
    risk_assessment jsonb,
    implementation_plan jsonb,
    success_probability numeric(3,2),
    expected_roi numeric(5,2),
    implementation_timeline jsonb,
    contingency_plans jsonb,
    monitoring_kpis jsonb,
    decision_confidence numeric(3,2),
    generated_at timestamp without time zone DEFAULT now(),
    reviewed_by uuid,
    approved_for_implementation boolean DEFAULT false,
    approval_date timestamp without time zone
);


ALTER TABLE public.universe_recommendations OWNER TO postgres;

--
-- TOC entry 514 (class 1259 OID 247125)
-- Name: usage_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usage_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    module text,
    action text,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.usage_logs OWNER TO postgres;

--
-- TOC entry 515 (class 1259 OID 247132)
-- Name: user_passwords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_passwords (
    user_id uuid,
    password_hash character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    is_current boolean DEFAULT true,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid
);


ALTER TABLE public.user_passwords OWNER TO postgres;

--
-- TOC entry 565 (class 1259 OID 248759)
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_preferences (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid,
    member_id uuid,
    preference_category character varying(50) NOT NULL,
    preference_key character varying(100) NOT NULL,
    preference_value jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT check_user_or_member CHECK ((((user_id IS NOT NULL) AND (member_id IS NULL)) OR ((user_id IS NULL) AND (member_id IS NOT NULL))))
);


ALTER TABLE public.user_preferences OWNER TO postgres;

--
-- TOC entry 10557 (class 0 OID 0)
-- Dependencies: 565
-- Name: TABLE user_preferences; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.user_preferences IS 'User and member portal preference settings';


--
-- TOC entry 516 (class 1259 OID 247138)
-- Name: user_preferences_ai; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_preferences_ai (
    user_id uuid,
    preference_category character varying(100),
    preference_key character varying(200),
    preference_value jsonb,
    confidence_score numeric(3,2),
    learned_from character varying(50),
    supporting_evidence jsonb,
    preference_stability character varying(20),
    last_confirmed timestamp with time zone,
    business_impact jsonb,
    personalization_weight numeric(3,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.user_preferences_ai OWNER TO postgres;

--
-- TOC entry 517 (class 1259 OID 247146)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id uuid NOT NULL,
    role_id uuid NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 518 (class 1259 OID 247149)
-- Name: user_roles_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles_backup (
    user_id uuid,
    role_id uuid,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.user_roles_backup OWNER TO postgres;

--
-- TOC entry 519 (class 1259 OID 247152)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    full_name character varying(255),
    phone character varying(20),
    is_active boolean DEFAULT true,
    last_login timestamp with time zone,
    failed_login_attempts integer DEFAULT 0,
    account_locked_until timestamp with time zone,
    password_changed_at timestamp with time zone DEFAULT now(),
    must_change_password boolean DEFAULT false,
    role_id uuid,
    profile_image_url text,
    language character varying(10) DEFAULT 'en'::character varying,
    theme character varying(20) DEFAULT 'light'::character varying,
    company_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    role_id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone,
    user_type character varying(20) DEFAULT 'user'::character varying,
    department character varying(50),
    unit character varying(50),
    "position" character varying(100),
    manager_id uuid
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 520 (class 1259 OID 247166)
-- Name: users_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_backup (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    username character varying(50),
    email character varying(100),
    password_hash character varying(255),
    first_name character varying(50),
    last_name character varying(50),
    phone character varying(20),
    is_active boolean,
    last_login timestamp with time zone,
    failed_login_attempts integer,
    account_locked_until timestamp with time zone,
    password_changed_at timestamp with time zone,
    must_change_password boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    full_name character varying(255),
    role_id uuid,
    profile_image_url text,
    language character varying(10),
    theme character varying(20),
    company_id uuid,
    id_uuid uuid,
    created_by uuid,
    updated_by uuid,
    archived_at timestamp without time zone
);


ALTER TABLE public.users_backup OWNER TO postgres;

--
-- TOC entry 521 (class 1259 OID 247172)
-- Name: uuid_conversion_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.uuid_conversion_log (
    table_name text NOT NULL,
    phase text NOT NULL,
    status text NOT NULL,
    rows_affected integer,
    started_at timestamp without time zone DEFAULT now(),
    completed_at timestamp without time zone,
    error_message text,
    execution_time_ms integer,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE public.uuid_conversion_log OWNER TO postgres;

--
-- TOC entry 550 (class 1259 OID 248151)
-- Name: v_active_plan_benefits; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_active_plan_benefits AS
 SELECT pbs.id,
    pbs.plan_id,
    pbs.coverage_id,
    pbs.category_id,
    pbs.benefit_name,
    pbs.benefit_description,
    pbs.benefit_code,
    pbs.limit_amount,
    pbs.coinsurance_percent,
    pbs.deductible_amount,
    pbs.copay_amount,
    pbs.requires_preapproval,
    pbs.is_optional,
    pbs.is_active,
    pbs.network_tier,
    pbs.display_group,
    pbs.display_order,
    pbs.disclaimer,
    pbs.alert_threshold_percent,
    pbs.frequency_limit,
    pbs.waiting_period_days,
    pbs.ai_summary,
    pbs.created_at,
    pbs.updated_at,
    pbs.created_by,
    pbs.updated_by,
    pbs.archived_at,
    bc.name AS category_name,
    bc.name_ar AS category_name_ar,
    p.name AS plan_name,
    c.name AS coverage_name
   FROM (((public.plan_benefit_schedules pbs
     LEFT JOIN public.benefit_categories bc ON ((pbs.category_id = bc.id)))
     LEFT JOIN public.plans p ON ((pbs.plan_id = p.id)))
     LEFT JOIN public.coverages c ON ((pbs.coverage_id = c.id)))
  WHERE ((pbs.is_active = true) AND (pbs.archived_at IS NULL));


ALTER VIEW public.v_active_plan_benefits OWNER TO postgres;

--
-- TOC entry 559 (class 1259 OID 248641)
-- Name: v_active_policy_flags; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_active_policy_flags AS
 SELECT pf.id,
    pf.policy_id,
    pf.flag_type,
    pf.flag_value,
    pf.flag_severity,
    pf.flag_reason,
    pf.flag_description,
    pf.reference_number,
    pf.effective_date,
    pf.expiry_date,
    pf.is_active,
    pf.auto_expire,
    pf.blocks_renewals,
    pf.blocks_endorsements,
    pf.blocks_claims,
    pf.blocks_cancellations,
    pf.requires_manager_approval,
    pf.is_resolved,
    pf.resolved_date,
    pf.resolved_by,
    pf.resolution_notes,
    pf.created_at,
    pf.updated_at,
    pf.created_by,
    pf.updated_by,
    pf.archived_at,
    p.policy_number,
    p.status AS policy_status,
    m.full_name AS member_name,
    c.name AS company_name
   FROM (((public.policy_flags pf
     JOIN public.policies p ON ((pf.policy_id = p.id)))
     JOIN public.members m ON ((p.member_id = m.id)))
     JOIN public.companies c ON ((p.company_id = c.id)))
  WHERE ((pf.is_active = true) AND ((pf.expiry_date IS NULL) OR (pf.expiry_date >= CURRENT_DATE)));


ALTER VIEW public.v_active_policy_flags OWNER TO postgres;

--
-- TOC entry 560 (class 1259 OID 248646)
-- Name: v_benefit_utilization_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_benefit_utilization_summary AS
 SELECT mbu.member_id,
    mbu.policy_id,
    m.full_name AS member_name,
    p.policy_number,
    count(*) AS total_benefits,
    count(*) FILTER (WHERE (mbu.utilization_percentage >= (80)::numeric)) AS benefits_near_limit,
    count(*) FILTER (WHERE (mbu.is_exhausted = true)) AS exhausted_benefits,
    sum(mbu.used_amount) AS total_used_amount,
    sum(mbu.remaining_amount) AS total_remaining_amount
   FROM ((public.member_benefit_usage mbu
     JOIN public.members m ON ((mbu.member_id = m.id)))
     JOIN public.policies p ON ((mbu.policy_id = p.id)))
  GROUP BY mbu.member_id, mbu.policy_id, m.full_name, p.policy_number;


ALTER VIEW public.v_benefit_utilization_summary OWNER TO postgres;

--
-- TOC entry 561 (class 1259 OID 248659)
-- Name: v_member_benefit_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_member_benefit_summary AS
 SELECT mbu.member_id,
    m.full_name,
    mbu.policy_id,
    p.policy_number,
    count(*) AS total_benefits,
    count(*) FILTER (WHERE (mbu.utilization_percentage >= (80)::numeric)) AS benefits_near_limit,
    count(*) FILTER (WHERE (mbu.is_exhausted = true)) AS exhausted_benefits,
    sum(mbu.used_amount) AS total_used_amount,
    sum(mbu.remaining_amount) AS total_remaining_amount,
    avg(mbu.utilization_percentage) AS avg_utilization
   FROM ((public.member_benefit_usage mbu
     JOIN public.members m ON ((mbu.member_id = m.id)))
     JOIN public.policies p ON ((mbu.policy_id = p.id)))
  GROUP BY mbu.member_id, m.full_name, mbu.policy_id, p.policy_number;


ALTER VIEW public.v_member_benefit_summary OWNER TO postgres;

--
-- TOC entry 551 (class 1259 OID 248156)
-- Name: v_plan_coverage_enhanced; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_plan_coverage_enhanced AS
 SELECT pcl.plan_id,
    pcl.coverage_id,
    c.name AS coverage_name,
    pcl.coverage_amount,
    pcl.deductible,
    pcl.copay_percentage,
    pbs.benefit_name,
    pbs.limit_amount AS benefit_limit,
    pbs.requires_preapproval,
    pbs.network_tier,
    bc.name AS benefit_category
   FROM (((public.plan_coverage_links pcl
     LEFT JOIN public.coverages c ON ((pcl.coverage_id = c.id)))
     LEFT JOIN public.plan_benefit_schedules pbs ON (((pbs.plan_id = pcl.plan_id) AND (pbs.coverage_id = pcl.coverage_id))))
     LEFT JOIN public.benefit_categories bc ON ((pbs.category_id = bc.id)))
  WHERE (pcl.is_excluded = false);


ALTER VIEW public.v_plan_coverage_enhanced OWNER TO postgres;

--
-- TOC entry 522 (class 1259 OID 247179)
-- Name: verifiable_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.verifiable_credentials (
    credential_id character varying(200) NOT NULL,
    holder_did character varying(200),
    issuer_did character varying(200),
    credential_type character varying(100),
    credential_subject jsonb,
    proof jsonb,
    issued_at timestamp with time zone,
    expires_at timestamp with time zone,
    revoked boolean DEFAULT false,
    revocation_registry character varying(200),
    schema_id character varying(200),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.verifiable_credentials OWNER TO postgres;

--
-- TOC entry 523 (class 1259 OID 247187)
-- Name: versioned_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.versioned_documents (
    template_name character varying(200) NOT NULL,
    document_type character varying(100),
    current_version integer DEFAULT 1,
    total_versions integer DEFAULT 1,
    base_template jsonb,
    variable_definitions jsonb,
    conditional_sections jsonb,
    regulatory_version character varying(50),
    legal_review_required boolean DEFAULT true,
    last_legal_review timestamp with time zone,
    usage_count integer DEFAULT 0,
    last_used timestamp with time zone,
    status character varying(30) DEFAULT 'active'::character varying,
    replacement_template_id uuid,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.versioned_documents OWNER TO postgres;

--
-- TOC entry 524 (class 1259 OID 247199)
-- Name: voice_analytics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.voice_analytics (
    interaction_id uuid,
    model_id uuid,
    sentiment_score numeric(6,4),
    emotion_analysis jsonb,
    stress_indicators jsonb,
    speech_patterns jsonb,
    language_complexity jsonb,
    caller_mood_progression jsonb,
    insights jsonb,
    analyzed_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.voice_analytics OWNER TO postgres;

--
-- TOC entry 525 (class 1259 OID 247206)
-- Name: voice_assistants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.voice_assistants (
    assistant_name character varying(50) NOT NULL,
    platform_type character varying(30),
    supported_languages text[],
    api_endpoint character varying(200),
    authentication_config jsonb,
    capability_features jsonb,
    privacy_settings jsonb,
    integration_status character varying(30),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.voice_assistants OWNER TO postgres;

--
-- TOC entry 526 (class 1259 OID 247213)
-- Name: voice_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.voice_interactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    member_id uuid,
    assistant_id uuid,
    session_id character varying(100),
    intent character varying(100),
    utterance_text text,
    confidence_score numeric(5,4),
    entity_extractions jsonb,
    response_text text,
    response_audio_url character varying(500),
    interaction_duration_seconds integer,
    user_satisfaction character varying(20),
    handoff_required boolean DEFAULT false,
    privacy_compliance jsonb,
    interaction_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.voice_interactions OWNER TO postgres;

--
-- TOC entry 527 (class 1259 OID 247221)
-- Name: vr_training_modules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vr_training_modules (
    module_name character varying(100) NOT NULL,
    training_category character varying(50),
    difficulty_level character varying(20),
    duration_minutes integer,
    learning_objectives jsonb,
    assessment_criteria jsonb,
    immersive_scenarios jsonb,
    completion_requirements jsonb,
    certification_credits numeric(4,2),
    created_by uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.vr_training_modules OWNER TO postgres;

--
-- TOC entry 528 (class 1259 OID 247229)
-- Name: vr_training_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vr_training_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    module_id uuid,
    trainee_id uuid,
    session_id character varying(100),
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    completion_percentage numeric(5,2),
    performance_metrics jsonb,
    learning_progress jsonb,
    assessment_scores jsonb,
    feedback_rating integer,
    instructor_notes text,
    certification_earned boolean DEFAULT false
);


ALTER TABLE public.vr_training_sessions OWNER TO postgres;

--
-- TOC entry 529 (class 1259 OID 247236)
-- Name: wearable_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wearable_devices (
    member_id uuid,
    device_brand character varying(50),
    device_model character varying(100),
    device_id character varying(200),
    health_permissions jsonb,
    data_sharing_consent jsonb,
    sync_frequency_minutes integer DEFAULT 60,
    last_sync_timestamp timestamp with time zone,
    privacy_settings jsonb,
    is_active boolean DEFAULT true,
    connected_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by uuid,
    updated_by uuid,
    updated_at timestamp without time zone,
    archived_at timestamp without time zone
);


ALTER TABLE public.wearable_devices OWNER TO postgres;

--
-- TOC entry 530 (class 1259 OID 247246)
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webhook_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type character varying(100) NOT NULL,
    event_source character varying(100),
    event_data jsonb NOT NULL,
    event_version character varying(20) DEFAULT '1.0'::character varying,
    event_timestamp timestamp with time zone DEFAULT now() NOT NULL,
    processing_status character varying(30) DEFAULT 'pending'::character varying,
    processing_attempts integer DEFAULT 0,
    max_retries integer DEFAULT 3,
    next_retry_at timestamp with time zone,
    webhook_deliverings jsonb,
    successful_deliveries integer DEFAULT 0,
    failed_deliveries integer DEFAULT 0,
    affects_entities jsonb,
    business_priority character varying(20) DEFAULT 'normal'::character varying,
    idempotency_key character varying(100),
    duplicate_of bigint,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.webhook_events OWNER TO postgres;

--
-- TOC entry 602 (class 1259 OID 250048)
-- Name: workflow_queue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_queue (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id uuid NOT NULL,
    workflow_type character varying(100) NOT NULL,
    priority character varying(20) DEFAULT 'medium'::character varying,
    status character varying(30) DEFAULT 'pending'::character varying,
    scheduled_at timestamp with time zone DEFAULT now(),
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    error_message text,
    retry_count integer DEFAULT 0,
    max_retries integer DEFAULT 3,
    created_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_at timestamp with time zone DEFAULT now(),
    updated_by uuid,
    archived_at timestamp without time zone,
    CONSTRAINT workflow_queue_priority_check CHECK (((priority)::text = ANY ((ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying])::text[]))),
    CONSTRAINT workflow_queue_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.workflow_queue OWNER TO postgres;

--
-- TOC entry 10116 (class 0 OID 244883)
-- Dependencies: 241
-- Data for Name: accounting_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounting_audit_logs (id, entry_type, entry_id, action, user_id, old_data, new_data, created_at) FROM stdin;
\.


--
-- TOC entry 10454 (class 0 OID 249071)
-- Dependencies: 585
-- Data for Name: activity_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.activity_log (id, user_id, activity, metadata, created_at) FROM stdin;
\.


--
-- TOC entry 10117 (class 0 OID 244890)
-- Dependencies: 242
-- Data for Name: actuarial_tables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.actuarial_tables (table_name, table_type, version, effective_date, expiry_date, geographic_scope, demographic_scope, table_data, data_source, regulatory_approval, approved_by, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10118 (class 0 OID 244898)
-- Dependencies: 243
-- Data for Name: age_brackets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.age_brackets (id, bracket_name, min_age, max_age, base_rate, description, insurance_type, is_active, effective_from, effective_to, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10119 (class 0 OID 244912)
-- Dependencies: 244
-- Data for Name: agent_commissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_commissions (id, quotation_id, agent_id, commission_rate, commission_amount, payment_status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10464 (class 0 OID 249338)
-- Dependencies: 595
-- Data for Name: aggregate_covers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.aggregate_covers (id, agreement_id, cover_name, cover_type, attachment_point, limit_amount, premium, premium_percentage, cover_period_start, cover_period_end, reinstatements, reinstatement_premium_percentage, subject_business, exclusions, geographical_scope, currency, status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10121 (class 0 OID 244932)
-- Dependencies: 246
-- Data for Name: ai_conversations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_conversations (id, member_id, session_id, model_id, conversation_topic, conversation_transcript, sentiment_progression, resolution_status, customer_satisfaction_score, handoff_to_human, handoff_reason, total_tokens_used, conversation_cost, started_at, ended_at) FROM stdin;
\.


--
-- TOC entry 10122 (class 0 OID 244940)
-- Dependencies: 247
-- Data for Name: ai_feature_usage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_feature_usage (id, user_id, module, feature, triggered_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10123 (class 0 OID 244947)
-- Dependencies: 248
-- Data for Name: ai_image_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_image_analysis (id, model_id, image_url, analysis_type, detected_objects, damage_assessment, confidence_score, processing_time_ms, human_verification_required, verified_by, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10409 (class 0 OID 247771)
-- Dependencies: 535
-- Data for Name: ai_ocr_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_ocr_results (id, task_id, extracted_text, confidence_score, created_at) FROM stdin;
\.


--
-- TOC entry 10124 (class 0 OID 244955)
-- Dependencies: 249
-- Data for Name: ai_pricing_traces; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_pricing_traces (id, quotation_id, model_version, input_parameters, output_recommendation, confidence_score, processing_time_ms, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10437 (class 0 OID 248831)
-- Dependencies: 568
-- Data for Name: ai_task_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_task_templates (id, template_name, task_type, prompt_template, model_parameters, expected_output_format, is_active, usage_count, created_at, updated_at, created_by) FROM stdin;
\.


--
-- TOC entry 10408 (class 0 OID 247761)
-- Dependencies: 534
-- Data for Name: ai_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_tasks (id, task_type, status, input_source, output_result, error_log, created_at, completed_at, related_entity_type, related_entity_id) FROM stdin;
\.


--
-- TOC entry 10410 (class 0 OID 247785)
-- Dependencies: 536
-- Data for Name: ai_utils; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ai_utils (id, name, description, content, created_at) FROM stdin;
\.


--
-- TOC entry 10125 (class 0 OID 244962)
-- Dependencies: 250
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10126 (class 0 OID 244965)
-- Dependencies: 251
-- Data for Name: api_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.api_keys (key_name, api_key_hash, user_id, permissions, rate_limit_per_hour, expires_at, is_active, last_used, created_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10127 (class 0 OID 244974)
-- Dependencies: 252
-- Data for Name: api_rate_limits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.api_rate_limits (api_key_id, endpoint_pattern, requests_per_second, requests_per_minute, requests_per_hour, requests_per_day, burst_limit, burst_window_seconds, current_second_count, current_minute_count, current_hour_count, current_day_count, second_reset_at, minute_reset_at, hour_reset_at, day_reset_at, violations_count, last_violation_at, created_at, updated_at, id) FROM stdin;
\.


--
-- TOC entry 10452 (class 0 OID 249051)
-- Dependencies: 583
-- Data for Name: app_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_versions (id, platform, version_number, release_notes, release_date) FROM stdin;
\.


--
-- TOC entry 10128 (class 0 OID 244995)
-- Dependencies: 253
-- Data for Name: ar_damage_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ar_damage_assessments (id, claim_id, app_id, assessor_id, session_id, ar_session_data, captured_images, damage_measurements, repair_estimates, session_duration_minutes, accuracy_score, quality_rating, session_timestamp, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10129 (class 0 OID 245002)
-- Dependencies: 254
-- Data for Name: ar_vr_applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ar_vr_applications (app_name, platform_type, use_case, supported_devices, minimum_specifications, app_version, download_url, features, pricing_model, is_production_ready, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10130 (class 0 OID 245010)
-- Dependencies: 255
-- Data for Name: archived_policies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.archived_policies (id, original_policy_id, policy_number, policy_data, related_data, archival_reason, archived_by, archived_at, retention_period_years, legal_hold, legal_hold_reason, destruction_date, access_level, last_accessed, access_count, data_hash, compression_ratio, search_keywords, business_tags, created_at, created_by, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10131 (class 0 OID 245021)
-- Dependencies: 256
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (table_name, record_id, action, performed_by, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- TOC entry 10406 (class 0 OID 247690)
-- Dependencies: 531
-- Data for Name: audit_logs_template; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs_template (table_name, record_id, action, performed_by, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- TOC entry 10455 (class 0 OID 249084)
-- Dependencies: 586
-- Data for Name: audit_trail_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_trail_events (id, entity_type, entity_id, action, performed_by, performed_at, notes) FROM stdin;
\.


--
-- TOC entry 10459 (class 0 OID 249209)
-- Dependencies: 590
-- Data for Name: automation_workflows; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.automation_workflows (id, workflow_name, workflow_type, process_steps, trigger_conditions, automation_level, success_rate, time_saved_minutes, created_at) FROM stdin;
\.


--
-- TOC entry 10470 (class 0 OID 250013)
-- Dependencies: 601
-- Data for Name: behavior_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.behavior_scores (id, member_id, device_id, score_type, score_value, score_period_start, score_period_end, contributing_factors, improvement_suggestions, discount_eligibility, discount_percentage, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10426 (class 0 OID 248443)
-- Dependencies: 554
-- Data for Name: benefit_alert_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_alert_logs (id, member_benefit_usage_id, member_id, alert_type, threshold_percentage, alert_message, alert_message_ar, delivery_channels, sent_at, email_sent, sms_sent, push_sent, portal_notification_sent, member_acknowledged, acknowledged_at, member_response, alert_status, expires_at, created_at, created_by) FROM stdin;
\.


--
-- TOC entry 10416 (class 0 OID 247968)
-- Dependencies: 542
-- Data for Name: benefit_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_categories (id, code, name, name_ar, description, description_ar, icon, display_order, is_active, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10423 (class 0 OID 248127)
-- Dependencies: 549
-- Data for Name: benefit_change_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_change_log (id, benefit_schedule_id, change_type, table_name, record_id, old_values, new_values, changed_fields, change_reason, change_source, changed_at, changed_by, ip_address, user_agent) FROM stdin;
\.


--
-- TOC entry 10419 (class 0 OID 248035)
-- Dependencies: 545
-- Data for Name: benefit_conditions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_conditions (id, benefit_schedule_id, condition_type, condition_operator, condition_value, condition_group, group_operator, priority_order, is_active, notes, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10420 (class 0 OID 248054)
-- Dependencies: 546
-- Data for Name: benefit_preapproval_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_preapproval_rules (id, benefit_schedule_id, provider_type, service_category, threshold_amount, threshold_type, always_required, auto_approve_below_threshold, approval_workflow, effective_date, expiry_date, notes, is_active, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10418 (class 0 OID 248018)
-- Dependencies: 544
-- Data for Name: benefit_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.benefit_translations (id, benefit_schedule_id, language_code, translated_name, translated_description, translated_disclaimer, created_at, updated_at, created_by) FROM stdin;
\.


--
-- TOC entry 10476 (class 0 OID 250134)
-- Dependencies: 607
-- Data for Name: bi_dashboard_cache; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bi_dashboard_cache (id, widget_id, cache_key, cached_data, cached_at, expires_at, is_valid) FROM stdin;
\.


--
-- TOC entry 10474 (class 0 OID 250107)
-- Dependencies: 605
-- Data for Name: bi_dashboards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bi_dashboards (id, dashboard_name, dashboard_type, layout_config, refresh_frequency, access_permissions, filters_config, data_sources, is_active, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10475 (class 0 OID 250118)
-- Dependencies: 606
-- Data for Name: bi_widgets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bi_widgets (id, dashboard_id, widget_name, widget_type, data_query, visualization_config, position_config, refresh_interval, cache_duration, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10132 (class 0 OID 245029)
-- Dependencies: 257
-- Data for Name: billing_cycles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.billing_cycles (cycle_name, cycle_months, description, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10133 (class 0 OID 245037)
-- Dependencies: 258
-- Data for Name: billing_statements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.billing_statements (id, entity_type, entity_id, billing_period_start, billing_period_end, total_due, status, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10134 (class 0 OID 245047)
-- Dependencies: 259
-- Data for Name: blockchain_networks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.blockchain_networks (network_name, network_id, rpc_endpoint, explorer_url, native_currency, gas_price_gwei, is_testnet, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10135 (class 0 OID 245054)
-- Dependencies: 260
-- Data for Name: blockchain_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.blockchain_transactions (transaction_hash, smart_contract_id, from_address, to_address, value, gas_used, gas_price_gwei, transaction_fee, block_number, status, transaction_data, created_at, confirmed_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10465 (class 0 OID 249354)
-- Dependencies: 596
-- Data for Name: bordereau_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bordereau_reports (id, agreement_id, report_period_start, report_period_end, report_type, total_premium, total_claims, ceded_premium, ceded_claims, commission, profit_commission, balance_due, report_data, submission_date, due_date, status, submitted_by, acknowledged_by_reinsurer, acknowledgment_date, disputes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10460 (class 0 OID 249218)
-- Dependencies: 591
-- Data for Name: bot_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bot_executions (id, workflow_id, execution_start, execution_end, status, records_processed, errors_encountered, created_at) FROM stdin;
\.


--
-- TOC entry 10432 (class 0 OID 248687)
-- Dependencies: 563
-- Data for Name: broker_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.broker_assignments (id, broker_id, company_id, group_id, policy_id, assignment_type, effective_date, expiry_date, is_active, created_at, created_by) FROM stdin;
\.


--
-- TOC entry 10431 (class 0 OID 248664)
-- Dependencies: 562
-- Data for Name: brokers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brokers (id, broker_code, broker_name, contact_person, email, phone, address, license_number, license_expiry, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- TOC entry 10453 (class 0 OID 249058)
-- Dependencies: 584
-- Data for Name: browser_fingerprints; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.browser_fingerprints (id, user_id, fingerprint, created_at) FROM stdin;
\.


--
-- TOC entry 10503 (class 0 OID 250515)
-- Dependencies: 634
-- Data for Name: business_intelligence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_intelligence (id, analysis_name, analysis_type, analysis_period_start, analysis_period_end, data_sources, key_metrics, insights, recommendations, analysis_status, analysis_method, confidence_score, business_impact_score, stakeholders, refresh_frequency, is_active, created_by, created_at, updated_by, updated_at, archived_at, real_time_metrics, dashboard_subscriptions, alert_configurations) FROM stdin;
\.


--
-- TOC entry 10136 (class 0 OID 245062)
-- Dependencies: 261
-- Data for Name: business_processes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_processes (process_name, process_category, version, description, process_definition, input_requirements, output_specifications, sla_hours, escalation_rules, is_active, created_by, approved_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10137 (class 0 OID 245071)
-- Dependencies: 262
-- Data for Name: campaign_performance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.campaign_performance (campaign_id, reporting_date, impressions, reach, frequency, clicks, click_through_rate, opens, open_rate, conversions, conversion_rate, revenue, cost_per_conversion, return_on_ad_spend, new_customers_acquired, customers_retained, customer_lifetime_value_impact, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10138 (class 0 OID 245091)
-- Dependencies: 263
-- Data for Name: carbon_emission_sources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carbon_emission_sources (source_name, emission_scope, category, calculation_methodology, emission_factor, unit_of_measure, data_quality_rating, update_frequency, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10139 (class 0 OID 245096)
-- Dependencies: 264
-- Data for Name: carbon_emissions_tracking; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carbon_emissions_tracking (id, company_id, emission_source_id, measurement_period_start, measurement_period_end, activity_quantity, emission_factor_used, total_emissions_kgco2e, verification_status, offset_credits_applied, net_emissions, data_source, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10140 (class 0 OID 245101)
-- Dependencies: 265
-- Data for Name: cards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cards (card_number, policy_id, member_id, plan_id, company_id, effective_date, expiry_date, status, qr_code_data, qr_code_url, card_design_url, enabled, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10143 (class 0 OID 245127)
-- Dependencies: 268
-- Data for Name: catastrophe_detection_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.catastrophe_detection_models (model_name, detection_type, input_data_types, model_architecture, accuracy_metrics, false_positive_rate, false_negative_rate, processing_time_seconds, geographical_coverage, is_real_time, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10463 (class 0 OID 249328)
-- Dependencies: 594
-- Data for Name: catastrophe_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.catastrophe_models (id, model_name, vendor, model_version, peril_type, geographic_region, model_resolution, currency, model_data, annual_aggregate_exceedance, occurrence_exceedance, calibration_date, last_updated, is_active, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10488 (class 0 OID 250304)
-- Dependencies: 619
-- Data for Name: chaos_experiment_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chaos_experiment_runs (id, experiment_id, run_started_at, run_completed_at, run_status, chaos_applied_successfully, system_impact_metrics, resilience_score, issues_discovered, recovery_time_seconds, success_criteria_met, lessons_learned, improvements_identified, follow_up_actions, executed_by, created_at) FROM stdin;
\.


--
-- TOC entry 10487 (class 0 OID 250293)
-- Dependencies: 618
-- Data for Name: chaos_experiments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chaos_experiments (id, experiment_name, experiment_type, target_system, chaos_action, experiment_parameters, hypothesis, success_criteria, blast_radius, rollback_plan, safety_checks, schedule_config, is_active, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10144 (class 0 OID 245135)
-- Dependencies: 269
-- Data for Name: chat_contexts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_contexts (id, user_id, session_id, context_type, context_summary, key_entities, sentiment_history, intent_progression, short_term_memory, long_term_memory, episodic_memory, communication_style, knowledge_level, interests_and_concerns, last_interaction, context_strength, decay_rate, created_at, updated_at, user_id_uuid, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10145 (class 0 OID 245143)
-- Dependencies: 270
-- Data for Name: churn_predictions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.churn_predictions (member_id, prediction_date, churn_probability, risk_level, contributing_factors, recommended_actions, model_version, prediction_horizon_days, confidence_score, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10146 (class 0 OID 245152)
-- Dependencies: 271
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cities (name_en, country_id, geom, postal_code, region_id, is_active, name_ar, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10427 (class 0 OID 248470)
-- Dependencies: 555
-- Data for Name: claim_action_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_action_logs (id, claim_id, action_type, action_description, previous_status, new_status, previous_amount, new_amount, amount_difference, supporting_documents, internal_notes, member_visible_notes, reason_code, requires_approval, approved_by, approval_date, approval_notes, triggered_by, rule_id, confidence_score, action_taken_at, action_taken_by, ip_address, user_agent) FROM stdin;
\.


--
-- TOC entry 10436 (class 0 OID 248809)
-- Dependencies: 567
-- Data for Name: claim_approvers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_approvers (id, claim_type, min_amount, max_amount, approver_role, approval_level, created_at, is_active) FROM stdin;
dc069c48-16b8-46ee-bd37-8b85dfa3ee05	medical	0.00	1000.00	claims_officer	1	2025-09-02 12:35:15.052414+03	t
737840db-3189-424f-bbfd-d78bdbe8e380	medical	1000.00	5000.00	senior_claims_officer	2	2025-09-02 12:35:15.052414+03	t
b864ed2c-9577-4f51-a456-6afa98cc61de	medical	5000.00	\N	claims_manager	3	2025-09-02 12:35:15.052414+03	t
44f0f192-75a0-4dfc-b477-54192d9a3af9	dental	0.00	500.00	claims_officer	1	2025-09-02 12:35:15.052414+03	t
d6297f0e-36a5-4630-98f9-3f6bcfce10e0	dental	500.00	\N	senior_claims_officer	2	2025-09-02 12:35:15.052414+03	t
34a22081-003a-47c2-87ae-4c9530d26c73	maternity	0.00	2000.00	claims_officer	1	2025-09-02 12:35:15.052414+03	t
39c3cf63-9c3d-481f-a09e-a22714c714ce	maternity	2000.00	\N	claims_manager	2	2025-09-02 12:35:15.052414+03	t
\.


--
-- TOC entry 10147 (class 0 OID 245159)
-- Dependencies: 272
-- Data for Name: claim_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_assessments (claim_id, assessor_id, assessment_type, assessment_date, damage_description, estimated_cost, recommended_action, photos, report_file_path, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10435 (class 0 OID 248786)
-- Dependencies: 566
-- Data for Name: claim_checklists; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_checklists (id, claim_type, checklist_item, is_mandatory, display_order, description, created_at, created_by, is_active) FROM stdin;
745120bf-3633-4a12-93c5-71cb119e0c41	medical	Medical report from treating physician	t	1	\N	2025-09-02 12:35:15.052414+03	\N	t
1fdef2c0-5e58-4e30-8675-44f816b373c1	medical	Prescription receipts	t	2	\N	2025-09-02 12:35:15.052414+03	\N	t
c9348854-36cc-4812-a49b-865d47c74512	medical	Hospital discharge summary (if applicable)	f	3	\N	2025-09-02 12:35:15.052414+03	\N	t
3436e1e7-648b-44e1-a79b-01fc69fa5dab	medical	Lab test results	f	4	\N	2025-09-02 12:35:15.052414+03	\N	t
fcd22a68-f5be-4d78-ad81-8ae5267c72bf	dental	Dental treatment plan	t	1	\N	2025-09-02 12:35:15.052414+03	\N	t
52c1d92c-894f-4bcf-ac5d-89f1166a7568	dental	X-rays or imaging	f	2	\N	2025-09-02 12:35:15.052414+03	\N	t
f7b51ab2-f224-42e7-b4a8-2689e38dd7a6	maternity	Birth certificate	t	1	\N	2025-09-02 12:35:15.052414+03	\N	t
7352af5f-589a-4b21-bfcd-f8e6b129ae59	maternity	Hospital bills	t	2	\N	2025-09-02 12:35:15.052414+03	\N	t
47674ecc-b3c2-4f28-bd2d-efb9cdb89d20	maternity	Prenatal care records	f	3	\N	2025-09-02 12:35:15.052414+03	\N	t
\.


--
-- TOC entry 10148 (class 0 OID 245167)
-- Dependencies: 273
-- Data for Name: claim_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_documents (claim_id, document_type, file_name, file_path, file_size, mime_type, uploaded_by, is_verified, verification_notes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10149 (class 0 OID 245175)
-- Dependencies: 274
-- Data for Name: claim_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claim_history (id, customer_id, insurance_type, claim_date, claim_amount, claim_type, description, status, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10120 (class 0 OID 244918)
-- Dependencies: 245
-- Data for Name: claims; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.claims (claim_number, card_id, policy_id, claim_type, status, incident_date, reported_date, description, amount, currency, location, assigned_adjuster, priority, fraud_indicators, settlement_amount, settlement_date, created_at, updated_at, provider_id, claim_source, imported_at, import_batch_id, member_id, deleted_at, metadata, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10150 (class 0 OID 245185)
-- Dependencies: 275
-- Data for Name: climate_risk_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.climate_risk_assessments (company_id, scenario_id, assessment_date, physical_risk_score, transition_risk_score, overall_climate_risk, financial_impact_estimates, adaptation_strategies, stress_test_results, disclosure_requirements, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10151 (class 0 OID 245193)
-- Dependencies: 276
-- Data for Name: climate_scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.climate_scenarios (scenario_name, temperature_increase_celsius, time_horizon_years, probability_percentage, scenario_description, source_organization, last_updated, scenario_data, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10449 (class 0 OID 249019)
-- Dependencies: 580
-- Data for Name: cms_pages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cms_pages (id, slug, title, body, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10152 (class 0 OID 245200)
-- Dependencies: 277
-- Data for Name: cohort_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cohort_analysis (id, cohort_definition_id, cohort_period, analysis_period, cohort_size, active_customers, retention_rate, revenue_per_customer, total_revenue, cumulative_revenue, average_order_value, purchase_frequency, customer_lifetime_value, engagement_metrics, product_usage_patterns, channel_preferences, calculated_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10153 (class 0 OID 245207)
-- Dependencies: 278
-- Data for Name: cohort_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cohort_definitions (cohort_name, cohort_type, definition_criteria, time_period, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10429 (class 0 OID 248530)
-- Dependencies: 557
-- Data for Name: collections_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collections_logs (id, policy_id, invoice_id, member_id, collection_stage, days_overdue, outstanding_amount, action_type, communication_channel, communication_sent_at, message_template_used, personalized_message, recipient_contact_info, member_responded, response_received_at, response_type, response_details, payment_received, payment_amount, payment_date, payment_method, next_action_scheduled, next_action_date, escalation_required, escalation_reason, collection_status, resolution_date, resolution_notes, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- TOC entry 10154 (class 0 OID 245215)
-- Dependencies: 279
-- Data for Name: commission_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.commission_rules (id, plan_id, agent_type, commission_percent, min_premium, max_cap, payment_type, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10155 (class 0 OID 245222)
-- Dependencies: 280
-- Data for Name: commission_statements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.commission_statements (id, agent_id, period_start, period_end, total_commission, status, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10156 (class 0 OID 245230)
-- Dependencies: 281
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (name, registration_number, tax_id, email, phone, address, postal_code, website, logo_url, is_active, license_number, license_expiry_date, regulatory_rating, solvency_ratio, created_at, updated_at, geom, country_id, state_id, city_id, default_language, theme_color, timezone, subscription_status, custom_domain, notes, region_id, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10157 (class 0 OID 245243)
-- Dependencies: 282
-- Data for Name: company_esg_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_esg_scores (company_id, framework_id, reporting_period_start, reporting_period_end, overall_esg_score, environmental_score, social_score, governance_score, detailed_scores, peer_comparison, improvement_areas, certification_level, third_party_verified, verifier_organization, calculated_at, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10497 (class 0 OID 250433)
-- Dependencies: 628
-- Data for Name: competitor_intelligence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competitor_intelligence (id, competitor_name, intelligence_type, intelligence_summary, data_sources, credibility_score, competitive_threat_level, potential_customer_impact, recommended_response, monitoring_priority, intelligence_date, follow_up_required, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10158 (class 0 OID 245252)
-- Dependencies: 283
-- Data for Name: compliance_monitoring; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compliance_monitoring (company_id, requirement_id, monitoring_date, current_value, threshold_value, status, variance_percentage, remediation_plan, target_date, responsible_person, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10159 (class 0 OID 245260)
-- Dependencies: 284
-- Data for Name: computer_vision_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.computer_vision_models (model_name, model_type, model_version, accuracy_metrics, model_endpoints, training_dataset_info, inference_cost_per_request, max_requests_per_second, is_production_ready, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10160 (class 0 OID 245269)
-- Dependencies: 285
-- Data for Name: content_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.content_templates (template_name, content_type, template_structure, personalization_rules, a_b_test_variants, performance_metrics, target_personas, created_by, is_active, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10161 (class 0 OID 245277)
-- Dependencies: 286
-- Data for Name: conversation_memory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conversation_memory (user_id, memory_type, memory_key, memory_value, confidence_level, source_conversation_id, extraction_method, validation_status, first_mentioned, last_reinforced, reinforcement_count, contradiction_count, memory_strength, decay_function, half_life_days, is_active, created_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10162 (class 0 OID 245289)
-- Dependencies: 287
-- Data for Name: conversational_ai_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conversational_ai_models (model_name, model_type, language_capabilities, domain_specialization, context_window_size, response_quality_score, hallucination_rate, api_endpoint, cost_per_token, is_production, created_at, id) FROM stdin;
\.


--
-- TOC entry 10163 (class 0 OID 245298)
-- Dependencies: 288
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.countries (name, iso_code, phone_code, is_active, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10164 (class 0 OID 245303)
-- Dependencies: 289
-- Data for Name: coverage_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coverage_options (id, insurance_type, option_name, description, base_price, pricing_formula, is_optional, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10165 (class 0 OID 245311)
-- Dependencies: 290
-- Data for Name: coverages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.coverages (name, description, coverage_type, maximum_amount, currency, created_at, updated_at, type, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10166 (class 0 OID 245320)
-- Dependencies: 291
-- Data for Name: cpt_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cpt_codes (code, description, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10167 (class 0 OID 245326)
-- Dependencies: 292
-- Data for Name: cryptographic_algorithms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cryptographic_algorithms (algorithm_name, algorithm_type, quantum_resistant, key_size_bits, security_level, performance_benchmark, standardization_status, implementation_library, is_approved, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10168 (class 0 OID 245335)
-- Dependencies: 293
-- Data for Name: cultural_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cultural_preferences (locale_code, preference_category, preference_key, preference_value, cultural_notes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10443 (class 0 OID 248919)
-- Dependencies: 574
-- Data for Name: custom_field_values; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.custom_field_values (id, custom_field_id, entity_id, value, created_at) FROM stdin;
\.


--
-- TOC entry 10442 (class 0 OID 248910)
-- Dependencies: 573
-- Data for Name: custom_fields; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.custom_fields (id, entity_type, name, label, field_type, is_required, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10461 (class 0 OID 249232)
-- Dependencies: 592
-- Data for Name: customer_360_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_360_profiles (id, member_id, unified_profile, segment_ids, lifetime_value, churn_score, next_best_action, last_interaction, preference_profile, risk_profile, created_at) FROM stdin;
\.


--
-- TOC entry 10169 (class 0 OID 245342)
-- Dependencies: 294
-- Data for Name: customer_journey_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_journey_events (id, member_id, event_type, event_name, channel, touchpoint, event_data, session_id, user_agent, ip_address, conversion_value, event_timestamp) FROM stdin;
\.


--
-- TOC entry 10462 (class 0 OID 249246)
-- Dependencies: 593
-- Data for Name: customer_journey_touchpoints; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_journey_touchpoints (id, customer_id, touchpoint_type, channel, interaction_data, sentiment_score, conversion_event, touchpoint_timestamp, created_at) FROM stdin;
\.


--
-- TOC entry 10170 (class 0 OID 245349)
-- Dependencies: 295
-- Data for Name: customer_lifecycle_stages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_lifecycle_stages (stage_name, stage_description, stage_criteria, typical_duration_days, next_stages, actions, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10171 (class 0 OID 245356)
-- Dependencies: 296
-- Data for Name: customer_lifetime_value; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_lifetime_value (member_id, calculation_date, historical_value, predicted_value, total_ltv, confidence_interval, contributing_factors, model_version, valid_until, calculated_by, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10172 (class 0 OID 245364)
-- Dependencies: 297
-- Data for Name: customer_personas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_personas (persona_name, demographic_profile, behavioral_patterns, risk_tolerance, product_preferences, channel_preferences, life_stage, value_drivers, communication_style, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10173 (class 0 OID 245371)
-- Dependencies: 298
-- Data for Name: customer_risk_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_risk_profiles (id, customer_id, insurance_type, risk_score, risk_factors, medical_conditions, lifestyle_factors, occupation_risk_level, credit_based_insurance_score, last_assessed, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10174 (class 0 OID 245380)
-- Dependencies: 299
-- Data for Name: customer_segment_analytics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_segment_analytics (segment_id, analysis_period_start, analysis_period_end, total_customers, new_customers, churned_customers, net_growth, total_revenue, revenue_per_customer, profit_margin, customer_acquisition_cost, avg_session_duration, avg_sessions_per_customer, feature_adoption_rates, support_ticket_rate, churn_risk_distribution, upsell_opportunity_score, cross_sell_propensity, calculated_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10175 (class 0 OID 245387)
-- Dependencies: 300
-- Data for Name: customer_segments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_segments (segment_name, segment_description, segmentation_criteria, segment_type, is_active, created_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10176 (class 0 OID 245395)
-- Dependencies: 301
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, customer_code, first_name, last_name, email, phone, date_of_birth, address, national_id, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10177 (class 0 OID 245403)
-- Dependencies: 302
-- Data for Name: data_annotations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_annotations (id, dataset_id, sample_id, sample_path, annotation_type, annotations, confidence_score, quality_rating, needs_review, is_validated, annotated_by, annotation_time_seconds, annotation_method, reviewed_by, reviewed_at, review_comments, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10178 (class 0 OID 245412)
-- Dependencies: 303
-- Data for Name: data_exports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_exports (id, report_name, exported_by, exported_at, format, filters, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10179 (class 0 OID 245420)
-- Dependencies: 304
-- Data for Name: data_import_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_import_logs (file_name, imported_by, rows_imported, import_time, status, error_log, id) FROM stdin;
\.


--
-- TOC entry 10180 (class 0 OID 245427)
-- Dependencies: 305
-- Data for Name: data_quality_checks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_quality_checks (id, rule_id, check_date, total_records, failed_records, pass_percentage, status, error_details, sample_errors, execution_time_ms, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10181 (class 0 OID 245435)
-- Dependencies: 306
-- Data for Name: data_quality_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_quality_rules (rule_name, table_name, column_name, rule_type, rule_definition, severity, threshold_percentage, is_active, created_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10182 (class 0 OID 245444)
-- Dependencies: 307
-- Data for Name: data_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_requests (id, user_id, request_type, status, requested_at, processed_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10183 (class 0 OID 245452)
-- Dependencies: 308
-- Data for Name: decentralized_identities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.decentralized_identities (member_id, did_identifier, did_document, verification_methods, service_endpoints, controllers, created_timestamp, updated_timestamp, revoked, revocation_reason, blockchain_anchor, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10490 (class 0 OID 250328)
-- Dependencies: 621
-- Data for Name: decision_universes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.decision_universes (id, decision_name, decision_context, universe_count, decision_parameters, evaluation_criteria, time_horizon_months, simulation_complexity, stakeholders, decision_deadline, status, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10433 (class 0 OID 248723)
-- Dependencies: 564
-- Data for Name: delegates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.delegates (id, company_id, group_id, delegate_name, email, phone, "position", department, permissions, is_primary, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- TOC entry 10456 (class 0 OID 249100)
-- Dependencies: 587
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (id, name, code, description, parent_department_id, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10184 (class 0 OID 245460)
-- Dependencies: 309
-- Data for Name: dependents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dependents (member_id, full_name, full_name_ar, gender, date_of_birth, relation, national_id_number, insurance_id_card_number, photo_url, has_card, coverage_level, coverage_limit, status, address, address_ar, notes, is_active, is_test_account, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10483 (class 0 OID 250236)
-- Dependencies: 614
-- Data for Name: digital_twin_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.digital_twin_models (id, model_name, twin_type, model_scope, simulation_engine, model_parameters, calibration_data, validation_metrics, update_frequency, computational_complexity, is_production_ready, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10185 (class 0 OID 245472)
-- Dependencies: 310
-- Data for Name: discounts_promotions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.discounts_promotions (id, name, description, discount_type, discount_value, insurance_type, applicable_to, min_premium, max_discount, start_date, end_date, is_active, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10186 (class 0 OID 245481)
-- Dependencies: 311
-- Data for Name: document_expiry_alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_expiry_alerts (document_id, alert_sent_at, method, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10187 (class 0 OID 245488)
-- Dependencies: 312
-- Data for Name: document_intelligence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_intelligence (id, document_id, nlp_model_id, extracted_entities, sentiment_analysis, contract_clauses, risk_indicators, compliance_flags, confidence_scores, processing_timestamp, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10413 (class 0 OID 247883)
-- Dependencies: 539
-- Data for Name: document_public_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_public_tokens (id, document_id, public_token, qr_code_url, expires_at, usage_limit, access_count, created_by, updated_by, created_at, updated_at, archived_at, qr_style_id) FROM stdin;
\.


--
-- TOC entry 10188 (class 0 OID 245495)
-- Dependencies: 313
-- Data for Name: document_revisions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_revisions (id, document_id, revision_number, version_label, change_description, change_type, document_content, content_hash, file_size, mime_type, changes_from_previous, author_id, reviewer_id, approval_status, approval_date, approval_notes, download_count, last_downloaded, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10411 (class 0 OID 247857)
-- Dependencies: 537
-- Data for Name: document_signatures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_signatures (id, document_id, signer_id, signer_type, signature_type, signature_data, signed_at, status, notes, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10189 (class 0 OID 245504)
-- Dependencies: 314
-- Data for Name: document_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_templates (id, name, template_type, design_version, content, preview_image, description, created_by, created_at, is_active, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10190 (class 0 OID 245513)
-- Dependencies: 315
-- Data for Name: document_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_versions (document_id, version_number, file_url, uploaded_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10191 (class 0 OID 245520)
-- Dependencies: 316
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (document_name, document_type, file_path, file_size, mime_type, status, uploaded_by, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10499 (class 0 OID 250457)
-- Dependencies: 630
-- Data for Name: employee_skills; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_skills (id, employee_id, skill_id, current_proficiency, proficiency_score, assessment_method, last_assessed, assessment_validity_months, development_priority, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10192 (class 0 OID 245529)
-- Dependencies: 317
-- Data for Name: encryption_zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.encryption_zones (zone_name, classification_level, encryption_algorithm_id, key_rotation_interval_days, access_control_policy, compliance_requirements, geographic_restrictions, last_key_rotation, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10193 (class 0 OID 245537)
-- Dependencies: 318
-- Data for Name: endorsements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.endorsements (policy_id, endorsement_number, type, effective_date, details, document_url, created_at, member_id, status, reason, previous_value, new_value, approved_by, approved_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10194 (class 0 OID 245545)
-- Dependencies: 319
-- Data for Name: entities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entities (company_id, entity_type_id, name, code, registration_number, email, phone, contact_person, contact_position, address_line, city_id, region_id, country_id, postal_code, latitude, longitude, is_active, is_blacklisted, notes, created_by, updated_by, created_at, updated_at, id, archived_at) FROM stdin;
\.


--
-- TOC entry 10195 (class 0 OID 245555)
-- Dependencies: 320
-- Data for Name: entity_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entity_types (company_id, code, label, description, is_default, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10196 (class 0 OID 245565)
-- Dependencies: 321
-- Data for Name: esg_frameworks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.esg_frameworks (framework_name, version, issuing_organization, focus_area, scoring_methodology, industry_applicability, mandatory_disclosure, effective_date, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10197 (class 0 OID 245573)
-- Dependencies: 322
-- Data for Name: exchange_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exchange_rates (id, base_currency, target_currency, exchange_rate, effective_date, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10198 (class 0 OID 245578)
-- Dependencies: 323
-- Data for Name: exclusions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exclusions (text, type, notes, is_active, created_at, updated_at, cpt_code_id, icd10_code_id, motor_code_id, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10199 (class 0 OID 245588)
-- Dependencies: 324
-- Data for Name: external_data_sources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.external_data_sources (id, source_name, source_type, endpoint_url, api_key_encrypted, last_sync, sync_status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10512 (class 0 OID 250861)
-- Dependencies: 643
-- Data for Name: external_field_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.external_field_mappings (id, integration_id, internal_table, internal_field, external_field, data_type, transformation_rule, created_at) FROM stdin;
\.


--
-- TOC entry 10200 (class 0 OID 245595)
-- Dependencies: 325
-- Data for Name: external_service_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.external_service_status (id, service_name, service_category, endpoint_url, check_method, expected_status_code, timeout_seconds, current_status, last_check_timestamp, response_time_ms, uptime_percentage, avg_response_time_ms, error_rate, alert_threshold_ms, consecutive_failures, alert_sent, last_alert_sent, business_criticality, affected_features, fallback_available, fallback_service, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10511 (class 0 OID 250851)
-- Dependencies: 642
-- Data for Name: external_services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.external_services (id, name, system_type, base_url, api_version, auth_type, credentials, is_active, notes, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10450 (class 0 OID 249030)
-- Dependencies: 581
-- Data for Name: faq_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.faq_entries (id, question, answer, category, language, is_active) FROM stdin;
\.


--
-- TOC entry 10201 (class 0 OID 245610)
-- Dependencies: 326
-- Data for Name: financial_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.financial_accounts (account_code, account_name, account_type, parent_account_id, normal_balance, is_active, company_id, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10202 (class 0 OID 245616)
-- Dependencies: 327
-- Data for Name: financial_periods; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.financial_periods (company_id, period_name, period_type, start_date, end_date, status, closed_by, closed_at, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10203 (class 0 OID 245622)
-- Dependencies: 328
-- Data for Name: fiscal_periods; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fiscal_periods (period_name, start_date, end_date, is_closed, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10204 (class 0 OID 245629)
-- Dependencies: 329
-- Data for Name: forecasting_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forecasting_models (model_name, model_type, target_metric_id, model_parameters, training_period_start, training_period_end, validation_metrics, seasonal_patterns, trend_analysis, forecast_horizon_days, confidence_intervals, is_production, last_retrained, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10205 (class 0 OID 245639)
-- Dependencies: 330
-- Data for Name: forecasts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forecasts (id, model_id, entity_type, entity_id, forecast_timestamp, predicted_value, confidence_lower, confidence_upper, prediction_interval, influencing_factors, scenario_assumptions, generated_at, actual_value, forecast_accuracy, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10206 (class 0 OID 245646)
-- Dependencies: 331
-- Data for Name: fraud_detection_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fraud_detection_models (model_name, model_type, feature_set, model_weights, threshold_config, false_positive_rate, false_negative_rate, last_retrained, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10207 (class 0 OID 245654)
-- Dependencies: 332
-- Data for Name: gdpr_consent_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gdpr_consent_logs (id, user_id, consent_type, granted, granted_at) FROM stdin;
\.


--
-- TOC entry 10208 (class 0 OID 245661)
-- Dependencies: 333
-- Data for Name: general_ledger_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.general_ledger_accounts (code, name, category, is_active, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10209 (class 0 OID 245669)
-- Dependencies: 334
-- Data for Name: generated_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.generated_documents (id, template_id, generated_for_type, generated_for_id, file_url, format, generated_by, generated_at, is_final, notes, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10210 (class 0 OID 245678)
-- Dependencies: 335
-- Data for Name: geographic_pricing_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.geographic_pricing_factors (id, zip_code, state, city, insurance_type, risk_factor, description, effective_from, effective_to, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10211 (class 0 OID 245687)
-- Dependencies: 336
-- Data for Name: group_admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.group_admins (group_id, user_id, created_at, id, user_id_uuid, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10212 (class 0 OID 245692)
-- Dependencies: 337
-- Data for Name: group_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.group_audit_logs (group_id, action, performed_by, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- TOC entry 10213 (class 0 OID 245699)
-- Dependencies: 338
-- Data for Name: group_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.group_contacts (group_id, name, email, phone, role, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10214 (class 0 OID 245705)
-- Dependencies: 339
-- Data for Name: group_demographics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.group_demographics (id, quotation_id, age_bracket_id, member_count, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10215 (class 0 OID 245711)
-- Dependencies: 340
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.groups (name, description, company_id, parent_group_id, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10216 (class 0 OID 245720)
-- Dependencies: 341
-- Data for Name: health_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.health_metrics (id, wearable_device_id, metric_type, metric_value, unit_of_measure, quality_score, contextual_data, anomaly_detected, health_insights, recorded_at, synced_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10217 (class 0 OID 245728)
-- Dependencies: 342
-- Data for Name: icd10_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.icd10_codes (code, description, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10218 (class 0 OID 245734)
-- Dependencies: 343
-- Data for Name: integration_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.integration_logs (id, integration_name, endpoint_url, http_method, request_headers, request_body, request_size_bytes, response_status_code, response_headers, response_body, response_size_bytes, response_time_ms, error_message, error_code, retry_count, business_transaction_id, user_id, correlation_id, contains_pii, data_classification, created_at, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10469 (class 0 OID 249999)
-- Dependencies: 600
-- Data for Name: iot_alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iot_alerts (id, device_id, alert_type, severity, alert_message, alert_data, triggered_at, acknowledged_at, acknowledged_by, resolved_at, action_taken, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10219 (class 0 OID 245744)
-- Dependencies: 344
-- Data for Name: iot_data_streams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iot_data_streams (id, device_id, stream_type, sensor_data, processed_data, anomaly_detected, anomaly_details, location, "timestamp", ingestion_timestamp, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10220 (class 0 OID 245753)
-- Dependencies: 345
-- Data for Name: iot_device_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iot_device_types (device_type_name, category, manufacturer, model_name, connectivity_protocol, data_transmission_frequency, battery_life_hours, environmental_rating, sensor_capabilities, security_features, cost_usd, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10221 (class 0 OID 245760)
-- Dependencies: 346
-- Data for Name: iot_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iot_devices (device_type_id, member_id, device_serial_number, firmware_version, last_seen, location, battery_level, signal_strength, status, configuration, security_keys, installed_at, warranty_expires, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10222 (class 0 OID 245767)
-- Dependencies: 347
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.journal_entries (entry_number, company_id, period_id, entry_date, description, reference_type, reference_id, total_debit, total_credit, currency, exchange_rate, status, created_by, approved_by, posted_at, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10223 (class 0 OID 245777)
-- Dependencies: 348
-- Data for Name: journal_entry_lines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.journal_entry_lines (journal_entry_id, line_number, account_id, description, debit_amount, credit_amount, cost_center, department, project_code, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10448 (class 0 OID 249000)
-- Dependencies: 579
-- Data for Name: knowledge_articles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.knowledge_articles (id, category_id, title, content, language, is_published, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10447 (class 0 OID 248988)
-- Dependencies: 578
-- Data for Name: knowledge_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.knowledge_categories (id, name, description, parent_id) FROM stdin;
\.


--
-- TOC entry 10224 (class 0 OID 245785)
-- Dependencies: 349
-- Data for Name: language_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.language_keys (key_name, key_category, context, data_type, usage_count, last_used, is_deprecated, replacement_key, created_by, created_at, id) FROM stdin;
\.


--
-- TOC entry 10225 (class 0 OID 245795)
-- Dependencies: 350
-- Data for Name: language_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.language_settings (id, user_id, company_id, preferred_language, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10226 (class 0 OID 245802)
-- Dependencies: 351
-- Data for Name: languages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.languages (language_code, iso_639_code, language_name, native_name, text_direction, is_active, completion_percentage, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10227 (class 0 OID 245810)
-- Dependencies: 352
-- Data for Name: locales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.locales (locale_code, language_id, country_code, currency_code, date_format, time_format, number_format, is_default, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10228 (class 0 OID 245818)
-- Dependencies: 353
-- Data for Name: login_attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.login_attempts (id, username, user_id, ip_address, user_agent, attempt_result, failure_reason, location_data, device_fingerprint, session_id, attempted_at, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10451 (class 0 OID 249038)
-- Dependencies: 582
-- Data for Name: login_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.login_devices (id, user_id, device_fingerprint, user_agent, ip_address, last_used_at, is_trusted) FROM stdin;
\.


--
-- TOC entry 10229 (class 0 OID 245825)
-- Dependencies: 354
-- Data for Name: login_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.login_sessions (user_type, user_id, device_info, ip_address, started_at, ended_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10494 (class 0 OID 250389)
-- Dependencies: 625
-- Data for Name: market_data_sources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_data_sources (id, source_name, source_type, api_endpoint, authentication_config, data_extraction_rules, update_frequency, reliability_score, cost_per_api_call, is_active, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10496 (class 0 OID 250418)
-- Dependencies: 627
-- Data for Name: market_impact_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_impact_analysis (id, signal_id, analysis_type, impact_categories, quantified_impacts, probability_assessment, timeline_assessment, recommended_actions, urgency_level, assigned_analyst, analysis_completed_at, stakeholder_notifications, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10495 (class 0 OID 250401)
-- Dependencies: 626
-- Data for Name: market_signals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_signals (id, source_id, signal_type, signal_title, signal_description, raw_data, processed_data, confidence_score, impact_severity, affected_business_areas, detected_at, validation_status, validated_by, validated_at, created_at) FROM stdin;
\.


--
-- TOC entry 10230 (class 0 OID 245833)
-- Dependencies: 355
-- Data for Name: marketing_campaigns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketing_campaigns (campaign_name, campaign_type, channel, target_segment_ids, start_date, end_date, budget, currency, target_audience_size, inclusion_criteria, exclusion_criteria, campaign_assets, a_b_test_variants, status, created_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10141 (class 0 OID 245111)
-- Dependencies: 266
-- Data for Name: medical_cards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medical_cards (id, member_id, policy_id, company_id, issued_at, expires_at, status, plan_name, card_number, qr_code_url, notes, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10231 (class 0 OID 245842)
-- Dependencies: 356
-- Data for Name: member_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_audit_logs (member_id, action, performed_by, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- TOC entry 10425 (class 0 OID 248401)
-- Dependencies: 553
-- Data for Name: member_benefit_usage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_benefit_usage (id, member_id, policy_id, plan_id, coverage_id, benefit_type, period_type, period_start_date, period_end_date, benefit_limit, used_amount, remaining_amount, benefit_count_limit, used_count, remaining_count, alert_sent_at_80_percent, alert_sent_at_90_percent, is_exhausted, exhausted_date, last_used_date, last_claim_id, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- TOC entry 10422 (class 0 OID 248098)
-- Dependencies: 548
-- Data for Name: member_benefit_utilization; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_benefit_utilization (id, member_id, policy_id, benefit_schedule_id, period_type, period_start_date, period_end_date, utilized_amount, utilized_count, remaining_amount, remaining_count, last_utilized_at, is_exhausted, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10232 (class 0 OID 245849)
-- Dependencies: 357
-- Data for Name: member_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_history (member_id, field_name, old_value, new_value, changed_by, changed_at, id) FROM stdin;
\.


--
-- TOC entry 10233 (class 0 OID 245856)
-- Dependencies: 358
-- Data for Name: member_login_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_login_logs (member_id, login_time, ip_address, device_info, location, id) FROM stdin;
\.


--
-- TOC entry 10234 (class 0 OID 245863)
-- Dependencies: 359
-- Data for Name: member_persona_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_persona_mapping (member_id, persona_id, confidence_score, assignment_date, assignment_method, persona_evolution_history, last_updated, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10235 (class 0 OID 245871)
-- Dependencies: 360
-- Data for Name: member_signatures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_signatures (id, member_id, signature_url, signed_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10236 (class 0 OID 245878)
-- Dependencies: 361
-- Data for Name: member_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.member_tags (member_id, tag, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10237 (class 0 OID 245884)
-- Dependencies: 362
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.members (member_number, first_name, last_name, date_of_birth, gender, email, phone, address, city, state, country, postal_code, company_id, group_id, is_active, created_at, created_by, updated_at, geom, full_name, password_hash, last_login_at, login_method, national_id_number, insurance_id_card_number, preferred_language, dependents_count, full_name_ar, address_ar, city_ar, state_ar, country_ar, source_channel, referred_by, is_test_account, last_password_change_at, password_reset_token, reset_token_expires_at, two_fa_enabled, nationality, deleted_at, metadata, id, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10238 (class 0 OID 245897)
-- Dependencies: 363
-- Data for Name: mfa_methods; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mfa_methods (user_id, method_type, method_config, is_primary, is_active, backup_codes, verified_at, created_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10239 (class 0 OID 245906)
-- Dependencies: 364
-- Data for Name: mfa_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mfa_sessions (user_id, session_token, method_used, device_fingerprint, ip_address, expires_at, verified_at, created_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10240 (class 0 OID 245913)
-- Dependencies: 365
-- Data for Name: ml_experiments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ml_experiments (experiment_name, experiment_type, objective, base_model_version_id, dataset_version_id, experiment_config, hypothesis, success_criteria, expected_improvement, status, started_at, completed_at, total_runtime_minutes, results, conclusions, lessons_learned, recommended_actions, next_experiments, created_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10241 (class 0 OID 245921)
-- Dependencies: 366
-- Data for Name: ml_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ml_models (id, model_name, version, trained_at, accuracy, notes, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10242 (class 0 OID 245927)
-- Dependencies: 367
-- Data for Name: model_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.model_versions (model_name, version, parent_version, architecture_type, framework, model_size_mb, parameter_count, training_dataset_id, hyperparameters, training_duration_minutes, training_cost, compute_resources, training_metrics, validation_metrics, test_metrics, benchmark_results, model_file_path, model_hash, checkpoint_paths, export_formats, deployment_status, deployment_config, api_endpoint, inference_cost_per_request, drift_detection_enabled, performance_threshold, retraining_trigger_conditions, bias_testing_results, fairness_metrics, explainability_support, created_by, approved_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10142 (class 0 OID 245119)
-- Dependencies: 267
-- Data for Name: motor_cards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.motor_cards (id, member_id, policy_id, company_id, plate_number, car_model, chassis_number, insurance_type, issued_at, expires_at, status, insured_value, driver_name, license_number, license_expiry_date, color, year_of_manufacture, vehicle_make, notes, qr_code_url, policy_number, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10243 (class 0 OID 245937)
-- Dependencies: 368
-- Data for Name: motor_exclusion_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.motor_exclusion_categories (name, description, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10244 (class 0 OID 245943)
-- Dependencies: 369
-- Data for Name: motor_exclusion_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.motor_exclusion_codes (code, title, category_id, description, is_active, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10245 (class 0 OID 245950)
-- Dependencies: 370
-- Data for Name: nlp_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nlp_models (model_name, model_type, language_support, model_config, performance_metrics, api_endpoint, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10472 (class 0 OID 250067)
-- Dependencies: 603
-- Data for Name: notification_queue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_queue (id, recipient_id, recipient_type, notification_type, channel, title, message, data, priority, status, scheduled_at, sent_at, delivery_status, error_message, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10438 (class 0 OID 248854)
-- Dependencies: 569
-- Data for Name: notifications_read_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications_read_log (id, notification_id, user_id, read_at) FROM stdin;
\.


--
-- TOC entry 10246 (class 0 OID 245958)
-- Dependencies: 371
-- Data for Name: otp_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.otp_requests (id, user_id, otp_code, sent_via, created_at, expires_at, is_used) FROM stdin;
\.


--
-- TOC entry 10491 (class 0 OID 250341)
-- Dependencies: 622
-- Data for Name: parallel_scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parallel_scenarios (id, universe_id, scenario_name, scenario_number, decision_choices, environmental_assumptions, resource_allocations, risk_profile, expected_outcomes, success_probability, created_at) FROM stdin;
\.


--
-- TOC entry 10247 (class 0 OID 245966)
-- Dependencies: 372
-- Data for Name: password_policies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_policies (company_id, policy_name, min_length, max_length, require_uppercase, require_lowercase, require_numbers, require_symbols, forbidden_sequences, password_history_count, max_age_days, warning_days_before_expiry, max_failed_attempts, lockout_duration_minutes, is_active, created_at, updated_at, id) FROM stdin;
\.


--
-- TOC entry 10248 (class 0 OID 245987)
-- Dependencies: 373
-- Data for Name: payment_methods; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_methods (member_id, method_type, provider, account_identifier, is_default, is_active, expiry_date, billing_address, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10249 (class 0 OID 245997)
-- Dependencies: 374
-- Data for Name: payment_receipts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_receipts (id, payment_date, received_from, amount, method, reference, status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10250 (class 0 OID 246005)
-- Dependencies: 375
-- Data for Name: payment_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_transactions (invoice_id, payment_method_id, transaction_id, amount, currency, status, gateway_response, processed_at, failure_reason, retry_count, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10473 (class 0 OID 250090)
-- Dependencies: 604
-- Data for Name: performance_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.performance_metrics (id, metric_name, metric_value, metric_unit, table_name, query_type, execution_time_ms, recorded_at, created_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10251 (class 0 OID 246015)
-- Dependencies: 376
-- Data for Name: permission_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permission_audit_logs (user_id, role_before, role_after, changed_by, changed_at, id) FROM stdin;
\.


--
-- TOC entry 10458 (class 0 OID 249132)
-- Dependencies: 589
-- Data for Name: permission_restrictions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permission_restrictions (id, role_id, resource_type, action, access_level, conditions, created_at) FROM stdin;
\.


--
-- TOC entry 10252 (class 0 OID 246022)
-- Dependencies: 377
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (name, description, resource, action, created_at, id, created_by, updated_by, updated_at, archived_at, scope_department, scope_unit, scope_company, conditions) FROM stdin;
\.


--
-- TOC entry 10253 (class 0 OID 246029)
-- Dependencies: 378
-- Data for Name: personalized_content_delivery; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personalized_content_delivery (id, member_id, template_id, delivery_channel, personalized_content, delivery_timestamp, opened, clicked, converted, engagement_score, feedback_rating, optimization_feedback, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10417 (class 0 OID 247982)
-- Dependencies: 543
-- Data for Name: plan_benefit_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_benefit_schedules (id, plan_id, coverage_id, category_id, benefit_name, benefit_description, benefit_code, limit_amount, coinsurance_percent, deductible_amount, copay_amount, requires_preapproval, is_optional, is_active, network_tier, display_group, display_order, disclaimer, alert_threshold_percent, frequency_limit, waiting_period_days, ai_summary, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10254 (class 0 OID 246038)
-- Dependencies: 379
-- Data for Name: plan_coverage_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_coverage_links (plan_id, coverage_id, coverage_amount, deductible, copay_percentage, created_at, updated_at, notes, unit, frequency_limit, is_mandatory, approval_needed, limit_type, sub_category, condition_tag, specific_limit, is_excluded, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10255 (class 0 OID 246051)
-- Dependencies: 380
-- Data for Name: plan_exclusion_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_exclusion_links (plan_id, exclusion_id, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10256 (class 0 OID 246056)
-- Dependencies: 381
-- Data for Name: plan_exclusions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_exclusions (plan_id, plan_type, exclusion_text, cpt_code_id, icd10_code_id, motor_code_id, notes, created_at, updated_at, exclusion_text_ar, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10257 (class 0 OID 246065)
-- Dependencies: 382
-- Data for Name: plan_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plan_types (code, label, icon, order_index, language_labels, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10259 (class 0 OID 246085)
-- Dependencies: 384
-- Data for Name: plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plans (name, description, plan_type, company_id, product_id, premium_amount, currency, coverage_period_months, is_active, created_at, updated_at, version, start_date, end_date, is_default, visibility, tags, approval_required, created_by, archived_at, id, updated_by) FROM stdin;
\.


--
-- TOC entry 10258 (class 0 OID 246073)
-- Dependencies: 383
-- Data for Name: policies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policies (policy_number, member_id, plan_id, application_id, status, effective_date, expiry_date, premium_amount, total_sum_insured, currency, payment_frequency, agent_id, broker_id, underwriter_id, policy_terms, endorsements, created_at, updated_at, policy_channel_id, product_id, entity_id, endorsement_number, auto_renew_date, document_url, tags, underwriter_notes, policy_type_id, is_renewable, notes, group_id, name, company_id, deleted_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10421 (class 0 OID 248074)
-- Dependencies: 547
-- Data for Name: policy_benefit_overrides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_benefit_overrides (id, policy_id, benefit_schedule_id, override_limit_amount, override_coinsurance_percent, override_deductible_amount, override_copay_amount, override_preapproval_required, override_network_tier, effective_date, expiry_date, override_reason, approval_reference, notes, is_active, created_at, updated_at, created_by, updated_by, approved_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10424 (class 0 OID 248359)
-- Dependencies: 552
-- Data for Name: policy_cancellations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_cancellations (id, policy_id, cancellation_type, requested_date, effective_date, cancellation_reason, refund_amount, refund_processed, refund_date, requested_by, approved_by, approval_date, approval_notes, status, is_reversed, reversal_reason, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10260 (class 0 OID 246099)
-- Dependencies: 385
-- Data for Name: policy_channels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_channels (code, name, description, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10261 (class 0 OID 246107)
-- Dependencies: 386
-- Data for Name: policy_coverages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_coverages (policy_id, coverage_id, coverage_limit, co_insurance, is_active, is_override, notes, assigned_by, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10262 (class 0 OID 246117)
-- Dependencies: 387
-- Data for Name: policy_dependents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_dependents (policy_id, full_name, date_of_birth, relation, gender, national_id, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10263 (class 0 OID 246122)
-- Dependencies: 388
-- Data for Name: policy_endorsements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_endorsements (policy_id, change_type, old_value, new_value, approved_by, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10264 (class 0 OID 246129)
-- Dependencies: 389
-- Data for Name: policy_exclusion_links; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_exclusion_links (policy_id, exclusion_id, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10430 (class 0 OID 248573)
-- Dependencies: 558
-- Data for Name: policy_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_flags (id, policy_id, flag_type, flag_value, flag_severity, flag_reason, flag_description, reference_number, effective_date, expiry_date, is_active, auto_expire, blocks_renewals, blocks_endorsements, blocks_claims, blocks_cancellations, requires_manager_approval, is_resolved, resolved_date, resolved_by, resolution_notes, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10265 (class 0 OID 246134)
-- Dependencies: 390
-- Data for Name: policy_lifecycle_stages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_lifecycle_stages (stage_name, stage_order, description, typical_duration_days, required_actions, next_possible_stages, is_terminal, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10266 (class 0 OID 246142)
-- Dependencies: 391
-- Data for Name: policy_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_payments (id, policy_id, amount, payment_date, payment_method, status, receipt_number, is_refunded, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10267 (class 0 OID 246151)
-- Dependencies: 392
-- Data for Name: policy_renewals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_renewals (id, quotation_id, previous_policy_id, renewal_date, premium_before_renewal, renewal_premium, renewal_reason, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10268 (class 0 OID 246158)
-- Dependencies: 393
-- Data for Name: policy_schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_schedule (id, policy_id, event_type, scheduled_date, status, executed_at, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10269 (class 0 OID 246166)
-- Dependencies: 394
-- Data for Name: policy_status_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_status_logs (policy_id, old_status, new_status, changed_by, change_reason, changed_at, id) FROM stdin;
\.


--
-- TOC entry 10270 (class 0 OID 246173)
-- Dependencies: 395
-- Data for Name: policy_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_types (code, name, description, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10271 (class 0 OID 246181)
-- Dependencies: 396
-- Data for Name: policy_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.policy_versions (policy_id, version_number, change_reason, changes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10467 (class 0 OID 249391)
-- Dependencies: 598
-- Data for Name: pool_participations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pool_participations (id, pool_name, pool_type, participation_percentage, maximum_line, joining_date, exit_date, annual_deposit, profit_share_percentage, management_expense_percentage, pool_manager, pool_agreement_terms, currency, is_active, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10479 (class 0 OID 250177)
-- Dependencies: 610
-- Data for Name: prediction_batch_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prediction_batch_jobs (id, job_name, model_id, schedule_expression, target_entities, job_status, last_run_at, next_run_at, results_count, execution_time_seconds, error_message, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10477 (class 0 OID 250149)
-- Dependencies: 608
-- Data for Name: prediction_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prediction_models (id, model_name, prediction_type, algorithm_type, training_features, model_parameters, performance_metrics, prediction_horizon_days, confidence_threshold, model_file_path, model_version, deployment_status, last_retrained, retraining_frequency, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10478 (class 0 OID 250161)
-- Dependencies: 609
-- Data for Name: prediction_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.prediction_results (id, model_id, entity_type, entity_id, prediction_value, confidence_score, prediction_factors, prediction_date, actual_outcome, prediction_accuracy, feedback_provided, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10272 (class 0 OID 246188)
-- Dependencies: 397
-- Data for Name: premium_age_brackets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_age_brackets (pricing_profile_id, age_from, age_to, premium, gender, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10273 (class 0 OID 246194)
-- Dependencies: 398
-- Data for Name: premium_calculations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_calculations (policy_id, pricing_model_id, calculation_date, base_premium, risk_adjustments, final_premium, calculation_details, manual_override, override_reason, calculated_by, approved_by, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10274 (class 0 OID 246203)
-- Dependencies: 399
-- Data for Name: premium_coinsurance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_coinsurance (uuid, pricing_profile_id, service_type, percentage, notes, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10275 (class 0 OID 246213)
-- Dependencies: 400
-- Data for Name: premium_copay; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_copay (pricing_profile_id, service_type, copay_percent, copay_cap, notes, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10276 (class 0 OID 246221)
-- Dependencies: 401
-- Data for Name: premium_copayment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_copayment (uuid, pricing_profile_id, service_type, amount, notes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10277 (class 0 OID 246230)
-- Dependencies: 402
-- Data for Name: premium_deductible; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_deductible (uuid, pricing_profile_id, service_type, amount, notes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10278 (class 0 OID 246239)
-- Dependencies: 403
-- Data for Name: premium_deductibles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_deductibles (deductible_amount, factor, notes, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10279 (class 0 OID 246248)
-- Dependencies: 404
-- Data for Name: premium_industries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_industries (industry_name, load_factor, description, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10280 (class 0 OID 246257)
-- Dependencies: 405
-- Data for Name: premium_invoices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_invoices (invoice_number, policy_id, premium_schedule_id, billing_period_start, billing_period_end, premium_amount, taxes, fees, discounts, total_amount, due_date, invoice_date, status, payment_method, payment_reference, paid_amount, paid_at, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10281 (class 0 OID 246269)
-- Dependencies: 406
-- Data for Name: premium_networks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_networks (pricing_profile_id, network_type, surcharge, notes, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10282 (class 0 OID 246277)
-- Dependencies: 407
-- Data for Name: premium_override_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_override_logs (quotation_id, overridden_by, original_premium, new_premium, reason, overridden_at, id) FROM stdin;
\.


--
-- TOC entry 10283 (class 0 OID 246284)
-- Dependencies: 408
-- Data for Name: premium_regions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_regions (region_id, load_factor, notes, created_at, updated_at, pricing_profile_id, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10284 (class 0 OID 246292)
-- Dependencies: 409
-- Data for Name: premium_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_rules (pricing_profile_id, service_type, is_included, coinsurance_percent, coverage_limit, copayment_amount, notes, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10285 (class 0 OID 246300)
-- Dependencies: 410
-- Data for Name: premium_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_schedules (policy_id, billing_cycle_id, total_premium, installment_count, installment_amount, start_date, end_date, status, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10286 (class 0 OID 246308)
-- Dependencies: 411
-- Data for Name: premium_services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_services (pricing_profile_id, service_type, base_rate, notes, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10287 (class 0 OID 246316)
-- Dependencies: 412
-- Data for Name: premium_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premium_settings (smoker_multiplier, max_group_discount, min_premium, rounding_precision, notes, updated_at, key, value, description, id, created_by, updated_by, created_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10288 (class 0 OID 246327)
-- Dependencies: 413
-- Data for Name: pricing_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pricing_models (model_name, product_type, model_version, model_type, base_factors, adjustment_factors, model_coefficients, confidence_interval, accuracy_metrics, training_data_period, last_calibration_date, is_active, created_by, approved_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10289 (class 0 OID 246335)
-- Dependencies: 414
-- Data for Name: pricing_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pricing_profiles (name, insurance_type, base_premium, min_premium, max_premium, currency, description, created_at, updated_at, version, status, effective_date, uuid, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10290 (class 0 OID 246347)
-- Dependencies: 415
-- Data for Name: pricing_version_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pricing_version_logs (id, target_type, target_id, version_from, version_to, change_description, changed_by, changed_at) FROM stdin;
\.


--
-- TOC entry 10291 (class 0 OID 246355)
-- Dependencies: 416
-- Data for Name: process_instances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.process_instances (id, process_id, instance_name, status, current_step, input_data, context_data, priority, assigned_to, started_by, started_at, completed_at, sla_due_date, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10292 (class 0 OID 246364)
-- Dependencies: 417
-- Data for Name: process_step_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.process_step_executions (instance_id, step_name, step_type, status, input_data, output_data, executed_by, execution_time_ms, error_message, started_at, completed_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10293 (class 0 OID 246370)
-- Dependencies: 418
-- Data for Name: product_catalog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_catalog (product_code, product_name, product_category, product_type, description, target_market, distribution_channels, regulatory_approvals, pricing_model_id, underwriting_rules, policy_terms, coverage_options, exclusions, commission_structure, is_active, launch_date, sunset_date, created_by, created_at, id) FROM stdin;
\.


--
-- TOC entry 10294 (class 0 OID 246378)
-- Dependencies: 419
-- Data for Name: product_features; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_features (product_id, feature_name, feature_type, feature_description, feature_config, is_optional, additional_premium, eligibility_criteria, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10295 (class 0 OID 246388)
-- Dependencies: 420
-- Data for Name: provider_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_audit_logs (provider_id, action, performed_by, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- TOC entry 10296 (class 0 OID 246395)
-- Dependencies: 421
-- Data for Name: provider_availability_exceptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_availability_exceptions (provider_id, exception_date, reason, is_closed, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10297 (class 0 OID 246402)
-- Dependencies: 422
-- Data for Name: provider_claims; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_claims (provider_id, claim_id, handled_at, status, notes, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10298 (class 0 OID 246408)
-- Dependencies: 423
-- Data for Name: provider_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_contacts (provider_id, name, phone, email, "position", is_primary, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10299 (class 0 OID 246413)
-- Dependencies: 424
-- Data for Name: provider_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_documents (provider_id, document_type, file_url, expires_at, uploaded_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10300 (class 0 OID 246420)
-- Dependencies: 425
-- Data for Name: provider_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_flags (provider_id, flag_type, flag_reason, flagged_by, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10301 (class 0 OID 246427)
-- Dependencies: 426
-- Data for Name: provider_images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_images (provider_id, image_url, label, uploaded_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10302 (class 0 OID 246434)
-- Dependencies: 427
-- Data for Name: provider_network_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_network_assignments (provider_network_id, company_id, group_id, contract_id, member_id, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10303 (class 0 OID 246440)
-- Dependencies: 428
-- Data for Name: provider_network_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_network_members (provider_id, provider_network_id, status, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10304 (class 0 OID 246446)
-- Dependencies: 429
-- Data for Name: provider_networks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_networks (code, name, description, type, company_id, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10305 (class 0 OID 246456)
-- Dependencies: 430
-- Data for Name: provider_ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_ratings (provider_id, member_id, rating, comment, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10306 (class 0 OID 246464)
-- Dependencies: 431
-- Data for Name: provider_service_prices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_service_prices (provider_id, service_tag, price, currency, is_discounted, notes, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10307 (class 0 OID 246474)
-- Dependencies: 432
-- Data for Name: provider_services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_services (provider_id, service_tag, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10308 (class 0 OID 246479)
-- Dependencies: 433
-- Data for Name: provider_specialties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_specialties (provider_id, specialty, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10309 (class 0 OID 246485)
-- Dependencies: 434
-- Data for Name: provider_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_tags (provider_id, tag, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10310 (class 0 OID 246491)
-- Dependencies: 435
-- Data for Name: provider_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_types (code, label, description, category, icon, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10311 (class 0 OID 246501)
-- Dependencies: 436
-- Data for Name: provider_working_hours; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.provider_working_hours (provider_id, day_of_week, opens_at, closes_at, is_closed, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10312 (class 0 OID 246506)
-- Dependencies: 437
-- Data for Name: providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.providers (name, provider_type_id, email, phone, address, city_id, latitude, longitude, rating, logo_url, is_active, created_at, updated_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10412 (class 0 OID 247871)
-- Dependencies: 538
-- Data for Name: public_card_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.public_card_views (id, card_type, card_id, public_token, qr_code_url, expires_at, created_by, updated_by, created_at, updated_at, archived_at, qr_style_id) FROM stdin;
\.


--
-- TOC entry 10415 (class 0 OID 247906)
-- Dependencies: 541
-- Data for Name: qr_styles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qr_styles (id, owner_type, owner_id, foreground_color, background_color, logo_url, border_size, image_format, caption_text, created_at) FROM stdin;
\.


--
-- TOC entry 10414 (class 0 OID 247897)
-- Dependencies: 540
-- Data for Name: qr_view_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qr_view_logs (id, public_token, viewer_ip, viewer_user_agent, viewed_at, referrer_url, notes) FROM stdin;
\.


--
-- TOC entry 10313 (class 0 OID 246516)
-- Dependencies: 438
-- Data for Name: quantum_algorithms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quantum_algorithms (algorithm_name, quantum_advantage_type, qubit_requirements, circuit_depth, gate_count, error_tolerance, classical_complexity, quantum_complexity, use_cases, implementation_status, hardware_requirements, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10314 (class 0 OID 246523)
-- Dependencies: 439
-- Data for Name: quantum_computations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quantum_computations (algorithm_id, computation_type, input_parameters, quantum_circuit, execution_time_ms, quantum_advantage_factor, fidelity_score, error_rate, classical_benchmark_time, results, executed_on, executed_at, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10315 (class 0 OID 246531)
-- Dependencies: 440
-- Data for Name: quantum_safe_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quantum_safe_keys (key_id, algorithm_id, key_usage, public_key, private_key_reference, key_generation_timestamp, expiration_timestamp, revocation_timestamp, key_status, associated_entity_type, associated_entity_id, created_at, id) FROM stdin;
\.


--
-- TOC entry 10316 (class 0 OID 246541)
-- Dependencies: 441
-- Data for Name: quotation_attachments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_attachments (quotation_id, file_name, file_url, file_type, uploaded_at, uploaded_by, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10317 (class 0 OID 246548)
-- Dependencies: 442
-- Data for Name: quotation_audit_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_audit_log (id, quotation_id, user_id, action_type, action_details, changed_values, ip_address, created_at) FROM stdin;
\.


--
-- TOC entry 10318 (class 0 OID 246555)
-- Dependencies: 443
-- Data for Name: quotation_coverage_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_coverage_options (id, quotation_id, coverage_option_id, calculated_price, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10319 (class 0 OID 246560)
-- Dependencies: 444
-- Data for Name: quotation_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_documents (id, quotation_id, document_type, document_name, file_path, generated_at, version, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10320 (class 0 OID 246569)
-- Dependencies: 445
-- Data for Name: quotation_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_factors (id, quotation_id, key, value, factor_type, impact_description, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10321 (class 0 OID 246576)
-- Dependencies: 446
-- Data for Name: quotation_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_items (id, quotation_id, coverage_name, coverage_name_ar, limit_amount, notes, notes_ar, display_order, meta_data, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10322 (class 0 OID 246584)
-- Dependencies: 447
-- Data for Name: quotation_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_logs (id, quotation_id, status_from, status_to, actor_id, notes, created_at) FROM stdin;
\.


--
-- TOC entry 10323 (class 0 OID 246591)
-- Dependencies: 448
-- Data for Name: quotation_pricing_profile_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_profile_rules (id, profile_id, rule_id, order_index, is_active, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10324 (class 0 OID 246599)
-- Dependencies: 449
-- Data for Name: quotation_pricing_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_profiles (id, name, insurance_type, description, notes, currency_code, base_premium, min_premium, max_premium, risk_formula, is_default, version, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10325 (class 0 OID 246611)
-- Dependencies: 450
-- Data for Name: quotation_pricing_profiles_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_profiles_history (history_id, profile_id, operation, changed_at, changed_by, old_data, new_data) FROM stdin;
\.


--
-- TOC entry 10326 (class 0 OID 246619)
-- Dependencies: 451
-- Data for Name: quotation_pricing_rule_age_brackets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_rule_age_brackets (id, rule_id, age_bracket_id, multiplier, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10327 (class 0 OID 246625)
-- Dependencies: 452
-- Data for Name: quotation_pricing_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_rules (id, insurance_type, rule_name, description, base_premium, min_premium, max_premium, currency_code, applies_to, comparison_operator, value, adjustment_type, adjustment_value, formula_expression, formula_variables, is_active, effective_from, effective_to, priority, version, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10328 (class 0 OID 246642)
-- Dependencies: 453
-- Data for Name: quotation_pricing_rules_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_pricing_rules_history (history_id, rule_id, operation, changed_at, changed_by, old_data, new_data) FROM stdin;
\.


--
-- TOC entry 10329 (class 0 OID 246650)
-- Dependencies: 454
-- Data for Name: quotation_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_versions (id, quotation_id, version_number, data_snapshot, is_latest_version, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10330 (class 0 OID 246658)
-- Dependencies: 455
-- Data for Name: quotation_workflow_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotation_workflow_logs (quotation_id, event, notes, created_at, created_by, id) FROM stdin;
\.


--
-- TOC entry 10331 (class 0 OID 246665)
-- Dependencies: 456
-- Data for Name: quotations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quotations (id, quote_number, customer_name, customer_email, customer_phone, channel, lead_source, assigned_to_user_id, follow_up_date, last_contacted_at, auto_expire_at, is_locked, converted_policy_id, ai_score, risk_score, summary_generated, summary_text, quote_bundle_id, tags, metadata, status, created_by, updated_by, created_at, updated_at, customer_national_id, customer_date_of_birth, customer_address, campaign_id, referral_code, assigned_team_id, priority_level, policy_type_id, plan_id, product_code, base_premium, discount_amount, surcharge_amount, fees_amount, tax_amount, items_premium, total_premium, currency_code, valid_from, valid_to, quote_expires_at, submitted_at, approved_at, converted_at, lock_reason, locked_by, locked_at, parent_quotation_id, renewal_quotation_id, fraud_score, priority_score, terms_conditions, special_conditions, rejection_reason, cancellation_reason, external_ref_id, source_system, version, is_latest_version, reference_number, profile_id, final_premium, base_currency, converted_premium, exchange_rate_used, group_size, customer_id, version_notes, assigned_to_user_id_uuid, archived_at) FROM stdin;
\.


--
-- TOC entry 10332 (class 0 OID 246681)
-- Dependencies: 457
-- Data for Name: rating_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rating_factors (factor_name, factor_code, product_type, factor_type, data_type, min_value, max_value, default_value, relativities, is_mandatory, effective_from, effective_to, regulatory_filed, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10333 (class 0 OID 246691)
-- Dependencies: 458
-- Data for Name: real_time_catastrophe_monitoring; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.real_time_catastrophe_monitoring (id, model_id, detection_timestamp, event_type, severity_level, confidence_score, affected_area, estimated_damage_usd, population_at_risk, properties_at_risk, alert_level, source_data_references, automated_response_actions, human_verification_status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10334 (class 0 OID 246699)
-- Dependencies: 459
-- Data for Name: real_time_fraud_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.real_time_fraud_scores (id, entity_type, entity_id, model_id, fraud_probability, risk_level, contributing_factors, anomaly_indicators, investigation_priority, human_review_required, model_explanation, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10335 (class 0 OID 246707)
-- Dependencies: 460
-- Data for Name: real_time_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.real_time_recommendations (id, member_id, model_id, session_id, recommendation_type, recommended_items, confidence_scores, explanation, context_factors, presented, clicked, converted, feedback_score, generated_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10336 (class 0 OID 246717)
-- Dependencies: 461
-- Data for Name: recommendation_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recommendation_models (model_name, recommendation_type, algorithm_type, model_parameters, training_data_features, accuracy_metrics, real_time_capable, cold_start_strategy, explanation_capability, last_retrained, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10337 (class 0 OID 246726)
-- Dependencies: 462
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regions (country_id, name, code, is_active, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10338 (class 0 OID 246731)
-- Dependencies: 463
-- Data for Name: regulatory_compliance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regulatory_compliance (id, region, insurance_type, requirement_name, description, compliance_value, effective_date, end_date, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10339 (class 0 OID 246738)
-- Dependencies: 464
-- Data for Name: regulatory_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regulatory_flags (id, entity_type, entity_id, flag_type, flag_value, effective_date, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10340 (class 0 OID 246745)
-- Dependencies: 465
-- Data for Name: regulatory_frameworks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regulatory_frameworks (framework_name, jurisdiction, regulator, version, effective_date, description, reporting_requirements, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10341 (class 0 OID 246753)
-- Dependencies: 466
-- Data for Name: regulatory_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regulatory_reports (report_name, framework_id, report_type, company_id, reporting_period_start, reporting_period_end, due_date, filing_date, status, report_data, validation_results, submission_reference, prepared_by, reviewed_by, submitted_by, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10342 (class 0 OID 246761)
-- Dependencies: 467
-- Data for Name: regulatory_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regulatory_requirements (framework_id, requirement_code, requirement_name, requirement_type, description, calculation_method, frequency, threshold_values, is_mandatory, effective_from, effective_to, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10343 (class 0 OID 246769)
-- Dependencies: 468
-- Data for Name: reinsurance_agreements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reinsurance_agreements (id, reinsurer_name, agreement_type, quota_share, retention_limit, excess_limit, start_date, end_date, status, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10344 (class 0 OID 246778)
-- Dependencies: 469
-- Data for Name: reinsurance_claims; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reinsurance_claims (id, claim_id, agreement_id, ceded_amount, retained_amount, paid_by_reinsurer, recovery_status, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10345 (class 0 OID 246786)
-- Dependencies: 470
-- Data for Name: reinsurance_commissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reinsurance_commissions (id, agreement_id, commission_type, rate, cap, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10346 (class 0 OID 246794)
-- Dependencies: 471
-- Data for Name: reinsurance_partners; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reinsurance_partners (id, name, code, contact_email, rating, type, logo_url, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10509 (class 0 OID 250781)
-- Dependencies: 640
-- Data for Name: report_analytics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_analytics (id, template_id, report_instance_id, analytics_date, generation_count, view_count, download_count, share_count, average_generation_time_seconds, error_rate_percentage, user_satisfaction_score, popular_filters, performance_metrics, created_at) FROM stdin;
\.


--
-- TOC entry 10508 (class 0 OID 250758)
-- Dependencies: 639
-- Data for Name: report_comments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_comments (id, report_instance_id, component_id, user_id, comment_text, comment_type, position_data, parent_comment_id, is_resolved, resolved_by, resolved_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10504 (class 0 OID 250673)
-- Dependencies: 635
-- Data for Name: report_components; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_components (id, component_name, component_type, component_category, component_config, default_settings, data_binding_schema, styling_options, icon_url, is_active, created_at, updated_at) FROM stdin;
1a9a13ce-ba5b-4b61-95cf-add1659fc12a	Bar Chart	chart	visualization	{"chart_type": "bar", "orientations": ["horizontal", "vertical"]}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
6f64a8b8-0322-4aa0-a8d9-359d7d7606d2	Line Chart	chart	visualization	{"chart_type": "line", "supports_multiple_series": true}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
e872f85f-4d25-42b1-abcc-74448aa70643	Pie Chart	chart	visualization	{"chart_type": "pie", "supports_donut": true}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
f3087e47-2a3f-4f30-8635-3ebd97529138	KPI Card	kpi_card	visualization	{"supports_trend": true, "supports_comparison": true}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
724bf172-0312-4608-82e3-b04a081f4c22	Data Table	table	visualization	{"supports_sorting": true, "supports_filtering": true}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
9b16ec56-9ea1-48f2-9d05-1c96a0eb94b1	Date Filter	filter	input	{"filter_type": "date_range", "default_range": "last_30_days"}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
b1674bf0-4062-430d-a204-a835756fda7b	Text Block	text	layout	{"supports_html": true, "supports_markdown": true}	{}	{}	{}	\N	t	2025-09-03 08:45:19.681952+03	\N
\.


--
-- TOC entry 10510 (class 0 OID 250809)
-- Dependencies: 641
-- Data for Name: report_favorites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_favorites (id, user_id, template_id, report_instance_id, favorite_type, notes, created_at) FROM stdin;
\.


--
-- TOC entry 10505 (class 0 OID 250690)
-- Dependencies: 636
-- Data for Name: report_instances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_instances (id, template_id, report_name, generated_by, generation_method, parameters_used, filters_applied, data_snapshot_date, generation_status, file_format, file_path, file_size_bytes, generation_time_seconds, download_count, expires_at, is_cached, cache_key, created_at, completed_at, error_message) FROM stdin;
\.


--
-- TOC entry 10506 (class 0 OID 250715)
-- Dependencies: 637
-- Data for Name: report_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_schedules (id, template_id, schedule_name, schedule_expression, parameters, recipients, delivery_method, file_formats, is_active, last_run_at, next_run_at, success_count, failure_count, last_error_message, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10507 (class 0 OID 250739)
-- Dependencies: 638
-- Data for Name: report_shares; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_shares (id, report_instance_id, shared_by, shared_with_type, shared_with_id, access_level, share_token, expires_at, access_count, last_accessed_at, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10347 (class 0 OID 246801)
-- Dependencies: 472
-- Data for Name: report_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.report_templates (id, name, description, query, created_by, created_at, updated_by, updated_at, archived_at, template_name, template_category, template_type, template_description, visual_layout, data_sources, sql_query, parameters, default_filters, permissions, is_public, is_prebuilt, usage_count) FROM stdin;
\.


--
-- TOC entry 10348 (class 0 OID 246808)
-- Dependencies: 473
-- Data for Name: retention_forecasts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.retention_forecasts (company_id, forecast_model, customer_segment_id, forecast_period_start, forecast_period_end, predicted_retention_rate, confidence_interval_lower, confidence_interval_upper, month_1_retention, month_3_retention, month_6_retention, month_12_retention, month_24_retention, expected_revenue_retained, expected_customers_retained, retention_improvement_opportunities, model_accuracy, historical_validation, feature_importance, forecast_generated_at, valid_until, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10349 (class 0 OID 246816)
-- Dependencies: 474
-- Data for Name: risk_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.risk_assessments (entity_type, entity_id, assessment_date, overall_risk_score, risk_level, risk_factors, assessment_method, valid_until, assessed_by, created_at, factors, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10350 (class 0 OID 246824)
-- Dependencies: 475
-- Data for Name: risk_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.risk_factors (factor_name, factor_category, data_type, calculation_method, weight, min_value, max_value, is_active, created_at, impact_score, name, description, factor_type, applies_to, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10351 (class 0 OID 246833)
-- Dependencies: 476
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id, role_id_uuid, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10352 (class 0 OID 246836)
-- Dependencies: 477
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, old_id, name, description, created_at, created_by, updated_by, updated_at, archived_at, user_type, department, unit, access_level, is_manager) FROM stdin;
\.


--
-- TOC entry 10353 (class 0 OID 246843)
-- Dependencies: 478
-- Data for Name: roles_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles_backup (name, description, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10445 (class 0 OID 248962)
-- Dependencies: 576
-- Data for Name: saas_feature_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_feature_flags (id, code, name, description, is_active) FROM stdin;
\.


--
-- TOC entry 10446 (class 0 OID 248972)
-- Dependencies: 577
-- Data for Name: saas_plan_features; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_plan_features (id, saas_plan_id, feature_flag_id, is_enabled) FROM stdin;
\.


--
-- TOC entry 10444 (class 0 OID 248951)
-- Dependencies: 575
-- Data for Name: saas_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.saas_plans (id, code, name, description, price, billing_cycle, max_users, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10354 (class 0 OID 246848)
-- Dependencies: 479
-- Data for Name: satellite_imagery; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.satellite_imagery (id, provider_id, image_id, capture_timestamp, geographic_bounds, resolution_meters, cloud_coverage_percentage, image_url, metadata, processing_level, atmospheric_correction, quality_score, download_cost, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10355 (class 0 OID 246856)
-- Dependencies: 480
-- Data for Name: satellite_providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.satellite_providers (provider_name, satellite_constellation, resolution_meters, revisit_frequency_days, spectral_bands, data_types, api_endpoint, pricing_model, coverage_area, is_active, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10356 (class 0 OID 246864)
-- Dependencies: 481
-- Data for Name: scheduled_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scheduled_tasks (id, task_name, payload, status, scheduled_for, executed_at, result) FROM stdin;
\.


--
-- TOC entry 10357 (class 0 OID 246871)
-- Dependencies: 482
-- Data for Name: security_incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_incidents (incident_type, severity, user_id, ip_address, description, evidence, status, assigned_to, resolved_at, resolution_notes, created_at, id, user_id_uuid, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10358 (class 0 OID 246879)
-- Dependencies: 483
-- Data for Name: security_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_sessions (user_id, session_id, device_fingerprint, ip_address, user_agent, location_data, trust_score, risk_indicators, is_active, last_activity, expires_at, created_at, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10481 (class 0 OID 250204)
-- Dependencies: 612
-- Data for Name: serendipity_discoveries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.serendipity_discoveries (id, pattern_id, discovery_title, discovery_description, discovery_type, significance_score, confidence_level, supporting_data, affected_entities, potential_value_estimate, actionability_score, discovery_date, validation_status, validated_by, validated_at, business_impact_actual, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10480 (class 0 OID 250192)
-- Dependencies: 611
-- Data for Name: serendipity_patterns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.serendipity_patterns (id, pattern_name, pattern_type, discovery_algorithm, data_sources, pattern_definition, significance_threshold, discovery_frequency, is_active, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10482 (class 0 OID 250220)
-- Dependencies: 613
-- Data for Name: serendipity_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.serendipity_recommendations (id, discovery_id, recommendation_type, recommendation_title, recommendation_description, priority, estimated_effort, estimated_roi, implementation_complexity, target_deadline, assigned_to, status, implementation_notes, results_metrics, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10359 (class 0 OID 246889)
-- Dependencies: 484
-- Data for Name: session_embeddings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.session_embeddings (id, session_id, embedding_type, source_text, embedding, embedding_model, embedding_version, token_count, semantic_tags, importance_score, context_window, created_at) FROM stdin;
\.


--
-- TOC entry 10360 (class 0 OID 246896)
-- Dependencies: 485
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (id, user_id, ip_address, device, created_at, last_active_at, is_active) FROM stdin;
\.


--
-- TOC entry 10485 (class 0 OID 250264)
-- Dependencies: 616
-- Data for Name: simulation_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_results (id, scenario_id, simulation_run_id, run_started_at, run_completed_at, computation_time_minutes, results_summary, detailed_results, confidence_metrics, sensitivity_analysis, risk_metrics, recommendations, validation_score, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10484 (class 0 OID 250247)
-- Dependencies: 615
-- Data for Name: simulation_scenarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_scenarios (id, twin_model_id, scenario_name, scenario_type, scenario_description, input_parameters, simulation_duration_months, monte_carlo_iterations, scenario_assumptions, confidence_intervals, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10486 (class 0 OID 250278)
-- Dependencies: 617
-- Data for Name: simulation_validation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulation_validation (id, simulation_result_id, validation_period_start, validation_period_end, predicted_values, actual_values, accuracy_metrics, model_drift_indicators, calibration_adjustments_needed, validation_notes, validated_by, validated_at) FROM stdin;
\.


--
-- TOC entry 10500 (class 0 OID 250471)
-- Dependencies: 631
-- Data for Name: skills_demand_forecast; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.skills_demand_forecast (id, skill_id, forecast_date, forecast_horizon_years, demand_trend, demand_growth_rate, industry_demand_score, automation_threat_level, emergence_factors, confidence_level, data_sources, forecast_model, created_by, created_at) FROM stdin;
\.


--
-- TOC entry 10502 (class 0 OID 250498)
-- Dependencies: 633
-- Data for Name: skills_development_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.skills_development_plans (id, employee_id, gap_analysis_id, target_skills, development_methods, estimated_duration_months, estimated_cost, priority_ranking, success_metrics, progress_milestones, assigned_mentor, plan_status, start_date, target_completion_date, actual_completion_date, effectiveness_rating, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10501 (class 0 OID 250487)
-- Dependencies: 632
-- Data for Name: skills_gap_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.skills_gap_analysis (id, analysis_name, department_id, analysis_date, current_skills_inventory, future_skills_requirements, identified_gaps, gap_severity_assessment, affected_employee_count, estimated_impact, recommended_actions, implementation_timeline, budget_requirements, success_metrics, analysis_status, created_by, created_at, updated_by, updated_at) FROM stdin;
\.


--
-- TOC entry 10498 (class 0 OID 250444)
-- Dependencies: 629
-- Data for Name: skills_taxonomy; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.skills_taxonomy (id, skill_name, skill_category, skill_subcategory, skill_description, proficiency_levels, industry_relevance, technology_dependency, obsolescence_risk, learning_difficulty, average_acquisition_time_months, is_active, created_by, created_at, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10361 (class 0 OID 246904)
-- Dependencies: 486
-- Data for Name: smart_contracts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smart_contracts (contract_name, contract_address, network_id, contract_type, abi, bytecode, deployment_tx_hash, deployment_block_number, gas_used, deployment_cost, is_verified, deployed_by, deployed_at, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10362 (class 0 OID 246912)
-- Dependencies: 487
-- Data for Name: smart_home_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smart_home_events (id, system_id, event_type, severity, sensor_location, event_data, automated_response, human_verification_required, emergency_services_notified, insurance_claim_eligible, potential_claim_amount, event_timestamp, created_at) FROM stdin;
\.


--
-- TOC entry 10363 (class 0 OID 246922)
-- Dependencies: 488
-- Data for Name: smart_home_systems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smart_home_systems (member_id, property_address, system_type, brand, model, installation_date, monitoring_plan, monthly_fee, emergency_contacts, integration_status, api_credentials, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 7898 (class 0 OID 243203)
-- Dependencies: 227
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- TOC entry 10364 (class 0 OID 246929)
-- Dependencies: 489
-- Data for Name: speech_analytics_models; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.speech_analytics_models (model_name, analysis_type, language_support, model_accuracy, real_time_processing, api_endpoint, cost_per_minute, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10365 (class 0 OID 246937)
-- Dependencies: 490
-- Data for Name: states; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.states (name, country_id, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10366 (class 0 OID 246941)
-- Dependencies: 491
-- Data for Name: status_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status_logs (id, entity_type, entity_id, previous_status, new_status, changed_by, changed_at) FROM stdin;
\.


--
-- TOC entry 10441 (class 0 OID 248881)
-- Dependencies: 572
-- Data for Name: support_response_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.support_response_templates (id, category_id, title, body, language) FROM stdin;
\.


--
-- TOC entry 10367 (class 0 OID 246948)
-- Dependencies: 492
-- Data for Name: sustainability_indicators; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sustainability_indicators (framework_id, indicator_code, indicator_name, category, measurement_unit, calculation_method, data_source_requirements, target_setting_guidance, industry_benchmarks, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10407 (class 0 OID 247708)
-- Dependencies: 532
-- Data for Name: system_configuration; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_configuration (id, category, key, value, description, is_encrypted, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10428 (class 0 OID 248497)
-- Dependencies: 556
-- Data for Name: system_flags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_flags (id, flag_name, flag_category, is_enabled, flag_value, description, company_id, environment, conditions, rollout_percentage, target_user_segments, created_date, enabled_date, disabled_date, scheduled_removal_date, usage_count, last_accessed_at, performance_impact_ms, created_at, updated_at, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10489 (class 0 OID 250318)
-- Dependencies: 620
-- Data for Name: system_resilience_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_resilience_metrics (id, system_name, metric_date, availability_percentage, mean_time_to_recovery_minutes, mean_time_between_failures_hours, error_rate_percentage, response_time_percentiles, chaos_resilience_score, improvement_trend, created_at) FROM stdin;
\.


--
-- TOC entry 10368 (class 0 OID 246955)
-- Dependencies: 493
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (id, key, value, description, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10468 (class 0 OID 249893)
-- Dependencies: 599
-- Data for Name: telematics_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.telematics_data (id, device_id, trip_start, trip_end, distance_km, max_speed_kmh, harsh_braking_events, rapid_acceleration_events, night_driving_minutes, safety_score, created_at) FROM stdin;
\.


--
-- TOC entry 10369 (class 0 OID 246961)
-- Dependencies: 494
-- Data for Name: template_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.template_categories (id, name, description, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10370 (class 0 OID 246967)
-- Dependencies: 495
-- Data for Name: template_variables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.template_variables (id, template_id, variable_key, label, sample_value, description, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10440 (class 0 OID 248874)
-- Dependencies: 571
-- Data for Name: ticket_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ticket_categories (id, name, description) FROM stdin;
\.


--
-- TOC entry 10439 (class 0 OID 248860)
-- Dependencies: 570
-- Data for Name: ticket_requests; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ticket_requests (id, member_id, category, subject, status, created_at) FROM stdin;
\.


--
-- TOC entry 10371 (class 0 OID 246973)
-- Dependencies: 496
-- Data for Name: time_series_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.time_series_data (id, metric_id, entity_type, entity_id, "timestamp", value, labels, quality_score, is_anomaly, anomaly_score, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10372 (class 0 OID 246982)
-- Dependencies: 497
-- Data for Name: time_series_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.time_series_metrics (metric_name, metric_category, data_type, aggregation_method, unit_of_measure, collection_frequency, retention_period_days, anomaly_detection_enabled, forecasting_enabled, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10373 (class 0 OID 246990)
-- Dependencies: 498
-- Data for Name: training_datasets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.training_datasets (dataset_name, dataset_version, dataset_type, description, data_source, collection_method, total_samples, total_size_bytes, quality_score, completeness_percentage, accuracy_percentage, consistency_score, feature_schema, target_variables, data_distribution, preprocessing_steps, augmentation_techniques, storage_location, access_credentials_ref, format, contains_pii, privacy_level, consent_obtained, gdpr_compliant, status, created_by, approved_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10374 (class 0 OID 247001)
-- Dependencies: 499
-- Data for Name: translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.translations (id, entity_type, entity_id, language_code, field, translation) FROM stdin;
\.


--
-- TOC entry 10375 (class 0 OID 247007)
-- Dependencies: 500
-- Data for Name: translations_enhanced; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.translations_enhanced (key_id, language_code, translated_text, translation_status, quality_score, translated_by, translation_method, translation_engine, reviewed_by, reviewed_at, review_notes, version, is_current, created_at, updated_at, id) FROM stdin;
\.


--
-- TOC entry 10376 (class 0 OID 247018)
-- Dependencies: 501
-- Data for Name: treaty_cessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.treaty_cessions (id, agreement_id, period_start, period_end, total_premium, total_claims, net_retention, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10377 (class 0 OID 247023)
-- Dependencies: 502
-- Data for Name: treaty_programs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.treaty_programs (id, program_name, treaty_type_id, year, notes, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10466 (class 0 OID 249376)
-- Dependencies: 597
-- Data for Name: treaty_reinstatements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.treaty_reinstatements (id, agreement_id, reinstatement_number, trigger_event, trigger_date, reinstatement_premium, reinstatement_percentage, available_limit_before, available_limit_after, effective_date, expiry_date, terms_and_conditions, payment_status, payment_due_date, paid_date, paid_amount, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10378 (class 0 OID 247029)
-- Dependencies: 503
-- Data for Name: treaty_statements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.treaty_statements (id, agreement_id, statement_date, gross_premium, commission_deducted, loss_recovery, balance_due, status, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10379 (class 0 OID 247037)
-- Dependencies: 504
-- Data for Name: treaty_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.treaty_types (name, description, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10380 (class 0 OID 247043)
-- Dependencies: 505
-- Data for Name: underwriting_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_actions (id, profile_id, action_type, taken_by, notes, taken_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10381 (class 0 OID 247051)
-- Dependencies: 506
-- Data for Name: underwriting_applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_applications (application_number, member_id, product_type, application_data, submission_channel, status, assigned_underwriter, priority, sla_due_date, created_at, updated_at, policy_id, submitted_at, notes, source, channel, assigned_to, decision_at, estimated_premium, premium_score, pricing_model_used, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10382 (class 0 OID 247062)
-- Dependencies: 507
-- Data for Name: underwriting_decision_matrix; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_decision_matrix (id, factor_1, factor_2, score, decision, weight, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10383 (class 0 OID 247070)
-- Dependencies: 508
-- Data for Name: underwriting_decisions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_decisions (application_id, rule_id, decision, risk_score, premium_adjustment, conditions_applied, underwriter_notes, automated, reviewed_by, decision_date, created_at, notes, decided_by, decision_at, updated_at, decision_score, decision_notes, decided_at, id, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10384 (class 0 OID 247082)
-- Dependencies: 509
-- Data for Name: underwriting_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_documents (id, profile_id, document_type, file_url, uploaded_by, uploaded_at, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10385 (class 0 OID 247089)
-- Dependencies: 510
-- Data for Name: underwriting_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_logs (application_id, action, performed_by, notes, "timestamp", log_type, log_data, created_by, created_at, id) FROM stdin;
\.


--
-- TOC entry 10386 (class 0 OID 247096)
-- Dependencies: 511
-- Data for Name: underwriting_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_profiles (id, member_id, policy_id, plan_id, quote_id, risk_score, decision, notes, created_at, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10387 (class 0 OID 247104)
-- Dependencies: 512
-- Data for Name: underwriting_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_rules (rule_name, product_type, rule_category, priority, conditions, actions, decision_outcome, risk_score_impact, premium_adjustment_percentage, coverage_modifications, is_active, effective_from, effective_to, created_by, approved_by, created_at, updated_at, name, description, condition_json, target_score, rule_type, applies_to, id, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10388 (class 0 OID 247117)
-- Dependencies: 513
-- Data for Name: underwriting_workflow_steps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.underwriting_workflow_steps (id, name, description, order_index, step_type, is_required, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10457 (class 0 OID 249117)
-- Dependencies: 588
-- Data for Name: units; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.units (id, department_id, name, code, description, is_active, created_at) FROM stdin;
\.


--
-- TOC entry 10492 (class 0 OID 250355)
-- Dependencies: 623
-- Data for Name: universe_outcomes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.universe_outcomes (id, scenario_id, simulation_completed_at, financial_outcomes, operational_outcomes, risk_outcomes, strategic_outcomes, stakeholder_impact, unintended_consequences, overall_success_score, confidence_level, created_at) FROM stdin;
\.


--
-- TOC entry 10493 (class 0 OID 250369)
-- Dependencies: 624
-- Data for Name: universe_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.universe_recommendations (id, universe_id, recommended_scenario_id, recommendation_rationale, risk_assessment, implementation_plan, success_probability, expected_roi, implementation_timeline, contingency_plans, monitoring_kpis, decision_confidence, generated_at, reviewed_by, approved_for_implementation, approval_date) FROM stdin;
\.


--
-- TOC entry 10389 (class 0 OID 247125)
-- Dependencies: 514
-- Data for Name: usage_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usage_logs (id, user_id, module, action, metadata, created_at) FROM stdin;
\.


--
-- TOC entry 10390 (class 0 OID 247132)
-- Dependencies: 515
-- Data for Name: user_passwords; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_passwords (user_id, password_hash, created_at, expires_at, is_current, id, user_id_uuid) FROM stdin;
\.


--
-- TOC entry 10434 (class 0 OID 248759)
-- Dependencies: 565
-- Data for Name: user_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_preferences (id, user_id, member_id, preference_category, preference_key, preference_value, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 10391 (class 0 OID 247138)
-- Dependencies: 516
-- Data for Name: user_preferences_ai; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_preferences_ai (user_id, preference_category, preference_key, preference_value, confidence_score, learned_from, supporting_evidence, preference_stability, last_confirmed, business_impact, personalization_weight, created_at, updated_at, id, user_id_uuid, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10392 (class 0 OID 247146)
-- Dependencies: 517
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (user_id, role_id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10393 (class 0 OID 247149)
-- Dependencies: 518
-- Data for Name: user_roles_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles_backup (user_id, role_id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10394 (class 0 OID 247152)
-- Dependencies: 519
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, first_name, last_name, full_name, phone, is_active, last_login, failed_login_attempts, account_locked_until, password_changed_at, must_change_password, role_id, profile_image_url, language, theme, company_id, created_at, updated_at, role_id_uuid, created_by, updated_by, archived_at, user_type, department, unit, "position", manager_id) FROM stdin;
\.


--
-- TOC entry 10395 (class 0 OID 247166)
-- Dependencies: 520
-- Data for Name: users_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users_backup (id, username, email, password_hash, first_name, last_name, phone, is_active, last_login, failed_login_attempts, account_locked_until, password_changed_at, must_change_password, created_at, updated_at, full_name, role_id, profile_image_url, language, theme, company_id, id_uuid, created_by, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 10396 (class 0 OID 247172)
-- Dependencies: 521
-- Data for Name: uuid_conversion_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.uuid_conversion_log (table_name, phase, status, rows_affected, started_at, completed_at, error_message, execution_time_ms, id) FROM stdin;
\.


--
-- TOC entry 10397 (class 0 OID 247179)
-- Dependencies: 522
-- Data for Name: verifiable_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.verifiable_credentials (credential_id, holder_did, issuer_did, credential_type, credential_subject, proof, issued_at, expires_at, revoked, revocation_registry, schema_id, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10398 (class 0 OID 247187)
-- Dependencies: 523
-- Data for Name: versioned_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.versioned_documents (template_name, document_type, current_version, total_versions, base_template, variable_definitions, conditional_sections, regulatory_version, legal_review_required, last_legal_review, usage_count, last_used, status, replacement_template_id, created_by, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10399 (class 0 OID 247199)
-- Dependencies: 524
-- Data for Name: voice_analytics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.voice_analytics (interaction_id, model_id, sentiment_score, emotion_analysis, stress_indicators, speech_patterns, language_complexity, caller_mood_progression, insights, analyzed_at, id, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10400 (class 0 OID 247206)
-- Dependencies: 525
-- Data for Name: voice_assistants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.voice_assistants (assistant_name, platform_type, supported_languages, api_endpoint, authentication_config, capability_features, privacy_settings, integration_status, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10401 (class 0 OID 247213)
-- Dependencies: 526
-- Data for Name: voice_interactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.voice_interactions (id, member_id, assistant_id, session_id, intent, utterance_text, confidence_score, entity_extractions, response_text, response_audio_url, interaction_duration_seconds, user_satisfaction, handoff_required, privacy_compliance, interaction_timestamp, created_by, updated_by, created_at, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10402 (class 0 OID 247221)
-- Dependencies: 527
-- Data for Name: vr_training_modules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vr_training_modules (module_name, training_category, difficulty_level, duration_minutes, learning_objectives, assessment_criteria, immersive_scenarios, completion_requirements, certification_credits, created_by, is_active, created_at, id, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10403 (class 0 OID 247229)
-- Dependencies: 528
-- Data for Name: vr_training_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vr_training_sessions (id, module_id, trainee_id, session_id, started_at, completed_at, completion_percentage, performance_metrics, learning_progress, assessment_scores, feedback_rating, instructor_notes, certification_earned) FROM stdin;
\.


--
-- TOC entry 10404 (class 0 OID 247236)
-- Dependencies: 529
-- Data for Name: wearable_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wearable_devices (member_id, device_brand, device_model, device_id, health_permissions, data_sharing_consent, sync_frequency_minutes, last_sync_timestamp, privacy_settings, is_active, connected_at, created_at, id, created_by, updated_by, updated_at, archived_at) FROM stdin;
\.


--
-- TOC entry 10405 (class 0 OID 247246)
-- Dependencies: 530
-- Data for Name: webhook_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webhook_events (id, event_type, event_source, event_data, event_version, event_timestamp, processing_status, processing_attempts, max_retries, next_retry_at, webhook_deliverings, successful_deliveries, failed_deliveries, affects_entities, business_priority, idempotency_key, duplicate_of, created_at) FROM stdin;
\.


--
-- TOC entry 10471 (class 0 OID 250048)
-- Dependencies: 602
-- Data for Name: workflow_queue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.workflow_queue (id, entity_type, entity_id, workflow_type, priority, status, scheduled_at, started_at, completed_at, error_message, retry_count, max_retries, created_at, created_by, updated_at, updated_by, archived_at) FROM stdin;
\.


--
-- TOC entry 7900 (class 0 OID 243964)
-- Dependencies: 232
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
\.


--
-- TOC entry 7901 (class 0 OID 243976)
-- Dependencies: 233
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- TOC entry 10558 (class 0 OID 0)
-- Dependencies: 231
-- Name: topology_id_seq; Type: SEQUENCE SET; Schema: topology; Owner: postgres
--

SELECT pg_catalog.setval('topology.topology_id_seq', 1, false);


--
-- TOC entry 9672 (class 2606 OID 249078)
-- Name: activity_log activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_pkey PRIMARY KEY (id);


--
-- TOC entry 9696 (class 2606 OID 249348)
-- Name: aggregate_covers aggregate_covers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aggregate_covers
    ADD CONSTRAINT aggregate_covers_pkey PRIMARY KEY (id);


--
-- TOC entry 9516 (class 2606 OID 247779)
-- Name: ai_ocr_results ai_ocr_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_ocr_results
    ADD CONSTRAINT ai_ocr_results_pkey PRIMARY KEY (id);


--
-- TOC entry 9629 (class 2606 OID 248842)
-- Name: ai_task_templates ai_task_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_task_templates
    ADD CONSTRAINT ai_task_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 9514 (class 2606 OID 247770)
-- Name: ai_tasks ai_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_tasks
    ADD CONSTRAINT ai_tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 9518 (class 2606 OID 247795)
-- Name: ai_utils ai_utils_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_utils
    ADD CONSTRAINT ai_utils_name_key UNIQUE (name);


--
-- TOC entry 9520 (class 2606 OID 247793)
-- Name: ai_utils ai_utils_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_utils
    ADD CONSTRAINT ai_utils_pkey PRIMARY KEY (id);


--
-- TOC entry 9668 (class 2606 OID 249057)
-- Name: app_versions app_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_versions
    ADD CONSTRAINT app_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 9675 (class 2606 OID 249091)
-- Name: audit_trail_events audit_trail_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_trail_events
    ADD CONSTRAINT audit_trail_events_pkey PRIMARY KEY (id);


--
-- TOC entry 9685 (class 2606 OID 249217)
-- Name: automation_workflows automation_workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_workflows
    ADD CONSTRAINT automation_workflows_pkey PRIMARY KEY (id);


--
-- TOC entry 9712 (class 2606 OID 250022)
-- Name: behavior_scores behavior_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavior_scores
    ADD CONSTRAINT behavior_scores_pkey PRIMARY KEY (id);


--
-- TOC entry 9580 (class 2606 OID 248459)
-- Name: benefit_alert_logs benefit_alert_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_alert_logs
    ADD CONSTRAINT benefit_alert_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 9536 (class 2606 OID 247981)
-- Name: benefit_categories benefit_categories_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_categories
    ADD CONSTRAINT benefit_categories_code_key UNIQUE (code);


--
-- TOC entry 9538 (class 2606 OID 247979)
-- Name: benefit_categories benefit_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_categories
    ADD CONSTRAINT benefit_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 9563 (class 2606 OID 248136)
-- Name: benefit_change_log benefit_change_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_change_log
    ADD CONSTRAINT benefit_change_log_pkey PRIMARY KEY (id);


--
-- TOC entry 9550 (class 2606 OID 248048)
-- Name: benefit_conditions benefit_conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_conditions
    ADD CONSTRAINT benefit_conditions_pkey PRIMARY KEY (id);


--
-- TOC entry 9553 (class 2606 OID 248068)
-- Name: benefit_preapproval_rules benefit_preapproval_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_preapproval_rules
    ADD CONSTRAINT benefit_preapproval_rules_pkey PRIMARY KEY (id);


--
-- TOC entry 9545 (class 2606 OID 248029)
-- Name: benefit_translations benefit_translations_benefit_schedule_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_translations
    ADD CONSTRAINT benefit_translations_benefit_schedule_id_language_code_key UNIQUE (benefit_schedule_id, language_code);


--
-- TOC entry 9547 (class 2606 OID 248027)
-- Name: benefit_translations benefit_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_translations
    ADD CONSTRAINT benefit_translations_pkey PRIMARY KEY (id);


--
-- TOC entry 9727 (class 2606 OID 250143)
-- Name: bi_dashboard_cache bi_dashboard_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bi_dashboard_cache
    ADD CONSTRAINT bi_dashboard_cache_pkey PRIMARY KEY (id);


--
-- TOC entry 9723 (class 2606 OID 250117)
-- Name: bi_dashboards bi_dashboards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bi_dashboards
    ADD CONSTRAINT bi_dashboards_pkey PRIMARY KEY (id);


--
-- TOC entry 9725 (class 2606 OID 250128)
-- Name: bi_widgets bi_widgets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bi_widgets
    ADD CONSTRAINT bi_widgets_pkey PRIMARY KEY (id);


--
-- TOC entry 9699 (class 2606 OID 249370)
-- Name: bordereau_reports bordereau_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bordereau_reports
    ADD CONSTRAINT bordereau_reports_pkey PRIMARY KEY (id);


--
-- TOC entry 9687 (class 2606 OID 249226)
-- Name: bot_executions bot_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bot_executions
    ADD CONSTRAINT bot_executions_pkey PRIMARY KEY (id);


--
-- TOC entry 9614 (class 2606 OID 248695)
-- Name: broker_assignments broker_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_pkey PRIMARY KEY (id);


--
-- TOC entry 9609 (class 2606 OID 248676)
-- Name: brokers brokers_broker_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brokers
    ADD CONSTRAINT brokers_broker_code_key UNIQUE (broker_code);


--
-- TOC entry 9611 (class 2606 OID 248674)
-- Name: brokers brokers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brokers
    ADD CONSTRAINT brokers_pkey PRIMARY KEY (id);


--
-- TOC entry 9670 (class 2606 OID 249065)
-- Name: browser_fingerprints browser_fingerprints_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.browser_fingerprints
    ADD CONSTRAINT browser_fingerprints_pkey PRIMARY KEY (id);


--
-- TOC entry 9781 (class 2606 OID 250529)
-- Name: business_intelligence business_intelligence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_intelligence
    ADD CONSTRAINT business_intelligence_pkey PRIMARY KEY (id);


--
-- TOC entry 9693 (class 2606 OID 249337)
-- Name: catastrophe_models catastrophe_models_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catastrophe_models
    ADD CONSTRAINT catastrophe_models_pkey PRIMARY KEY (id);


--
-- TOC entry 9751 (class 2606 OID 250312)
-- Name: chaos_experiment_runs chaos_experiment_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chaos_experiment_runs
    ADD CONSTRAINT chaos_experiment_runs_pkey PRIMARY KEY (id);


--
-- TOC entry 9749 (class 2606 OID 250303)
-- Name: chaos_experiments chaos_experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chaos_experiments
    ADD CONSTRAINT chaos_experiments_pkey PRIMARY KEY (id);


--
-- TOC entry 9585 (class 2606 OID 248481)
-- Name: claim_action_logs claim_action_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_action_logs
    ADD CONSTRAINT claim_action_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 9627 (class 2606 OID 248818)
-- Name: claim_approvers claim_approvers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_approvers
    ADD CONSTRAINT claim_approvers_pkey PRIMARY KEY (id);


--
-- TOC entry 9625 (class 2606 OID 248797)
-- Name: claim_checklists claim_checklists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_checklists
    ADD CONSTRAINT claim_checklists_pkey PRIMARY KEY (id);


--
-- TOC entry 9660 (class 2606 OID 249027)
-- Name: cms_pages cms_pages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cms_pages
    ADD CONSTRAINT cms_pages_pkey PRIMARY KEY (id);


--
-- TOC entry 9662 (class 2606 OID 249029)
-- Name: cms_pages cms_pages_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cms_pages
    ADD CONSTRAINT cms_pages_slug_key UNIQUE (slug);


--
-- TOC entry 9597 (class 2606 OID 248547)
-- Name: collections_logs collections_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 9769 (class 2606 OID 250443)
-- Name: competitor_intelligence competitor_intelligence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competitor_intelligence
    ADD CONSTRAINT competitor_intelligence_pkey PRIMARY KEY (id);


--
-- TOC entry 9642 (class 2606 OID 248926)
-- Name: custom_field_values custom_field_values_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.custom_field_values
    ADD CONSTRAINT custom_field_values_pkey PRIMARY KEY (id);


--
-- TOC entry 9639 (class 2606 OID 248918)
-- Name: custom_fields custom_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.custom_fields
    ADD CONSTRAINT custom_fields_pkey PRIMARY KEY (id);


--
-- TOC entry 9689 (class 2606 OID 249240)
-- Name: customer_360_profiles customer_360_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_360_profiles
    ADD CONSTRAINT customer_360_profiles_pkey PRIMARY KEY (id);


--
-- TOC entry 9691 (class 2606 OID 249255)
-- Name: customer_journey_touchpoints customer_journey_touchpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_journey_touchpoints
    ADD CONSTRAINT customer_journey_touchpoints_pkey PRIMARY KEY (id);


--
-- TOC entry 9755 (class 2606 OID 250340)
-- Name: decision_universes decision_universes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.decision_universes
    ADD CONSTRAINT decision_universes_pkey PRIMARY KEY (id);


--
-- TOC entry 9617 (class 2606 OID 248734)
-- Name: delegates delegates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delegates
    ADD CONSTRAINT delegates_pkey PRIMARY KEY (id);


--
-- TOC entry 9677 (class 2606 OID 249111)
-- Name: departments departments_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);


--
-- TOC entry 9679 (class 2606 OID 249109)
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- TOC entry 9741 (class 2606 OID 250246)
-- Name: digital_twin_models digital_twin_models_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.digital_twin_models
    ADD CONSTRAINT digital_twin_models_pkey PRIMARY KEY (id);


--
-- TOC entry 9528 (class 2606 OID 247894)
-- Name: document_public_tokens document_public_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_public_tokens
    ADD CONSTRAINT document_public_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 9530 (class 2606 OID 247896)
-- Name: document_public_tokens document_public_tokens_public_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_public_tokens
    ADD CONSTRAINT document_public_tokens_public_token_key UNIQUE (public_token);


--
-- TOC entry 9522 (class 2606 OID 247868)
-- Name: document_signatures document_signatures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_signatures
    ADD CONSTRAINT document_signatures_pkey PRIMARY KEY (id);


--
-- TOC entry 9773 (class 2606 OID 250465)
-- Name: employee_skills employee_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_pkey PRIMARY KEY (id);


--
-- TOC entry 9820 (class 2606 OID 250869)
-- Name: external_field_mappings external_field_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.external_field_mappings
    ADD CONSTRAINT external_field_mappings_pkey PRIMARY KEY (id);


--
-- TOC entry 9818 (class 2606 OID 250860)
-- Name: external_services external_services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.external_services
    ADD CONSTRAINT external_services_pkey PRIMARY KEY (id);


--
-- TOC entry 9664 (class 2606 OID 249037)
-- Name: faq_entries faq_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faq_entries
    ADD CONSTRAINT faq_entries_pkey PRIMARY KEY (id);


--
-- TOC entry 9710 (class 2606 OID 250007)
-- Name: iot_alerts iot_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_alerts
    ADD CONSTRAINT iot_alerts_pkey PRIMARY KEY (id);


--
-- TOC entry 9469 (class 2606 OID 249832)
-- Name: iot_data_streams iot_data_streams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_data_streams
    ADD CONSTRAINT iot_data_streams_pkey PRIMARY KEY (id);


--
-- TOC entry 9471 (class 2606 OID 249638)
-- Name: iot_device_types iot_device_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_device_types
    ADD CONSTRAINT iot_device_types_pkey PRIMARY KEY (id);


--
-- TOC entry 9475 (class 2606 OID 249576)
-- Name: iot_devices iot_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_devices
    ADD CONSTRAINT iot_devices_pkey PRIMARY KEY (id);


--
-- TOC entry 9658 (class 2606 OID 249008)
-- Name: knowledge_articles knowledge_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_articles
    ADD CONSTRAINT knowledge_articles_pkey PRIMARY KEY (id);


--
-- TOC entry 9656 (class 2606 OID 248994)
-- Name: knowledge_categories knowledge_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_categories
    ADD CONSTRAINT knowledge_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 9666 (class 2606 OID 249045)
-- Name: login_devices login_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.login_devices
    ADD CONSTRAINT login_devices_pkey PRIMARY KEY (id);


--
-- TOC entry 9763 (class 2606 OID 250400)
-- Name: market_data_sources market_data_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_data_sources
    ADD CONSTRAINT market_data_sources_pkey PRIMARY KEY (id);


--
-- TOC entry 9767 (class 2606 OID 250427)
-- Name: market_impact_analysis market_impact_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_impact_analysis
    ADD CONSTRAINT market_impact_analysis_pkey PRIMARY KEY (id);


--
-- TOC entry 9765 (class 2606 OID 250412)
-- Name: market_signals market_signals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_signals
    ADD CONSTRAINT market_signals_pkey PRIMARY KEY (id);


--
-- TOC entry 9576 (class 2606 OID 248415)
-- Name: member_benefit_usage member_benefit_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_pkey PRIMARY KEY (id);


--
-- TOC entry 9559 (class 2606 OID 248111)
-- Name: member_benefit_utilization member_benefit_utilization_member_id_policy_id_benefit_sche_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_utilization
    ADD CONSTRAINT member_benefit_utilization_member_id_policy_id_benefit_sche_key UNIQUE (member_id, policy_id, benefit_schedule_id, period_type, period_start_date);


--
-- TOC entry 9561 (class 2606 OID 248109)
-- Name: member_benefit_utilization member_benefit_utilization_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_utilization
    ADD CONSTRAINT member_benefit_utilization_pkey PRIMARY KEY (id);


--
-- TOC entry 9719 (class 2606 OID 250084)
-- Name: notification_queue notification_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_pkey PRIMARY KEY (id);


--
-- TOC entry 9631 (class 2606 OID 248859)
-- Name: notifications_read_log notifications_read_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications_read_log
    ADD CONSTRAINT notifications_read_log_pkey PRIMARY KEY (id);


--
-- TOC entry 9757 (class 2606 OID 250349)
-- Name: parallel_scenarios parallel_scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parallel_scenarios
    ADD CONSTRAINT parallel_scenarios_pkey PRIMARY KEY (id);


--
-- TOC entry 9721 (class 2606 OID 250096)
-- Name: performance_metrics performance_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_metrics
    ADD CONSTRAINT performance_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 9683 (class 2606 OID 249140)
-- Name: permission_restrictions permission_restrictions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission_restrictions
    ADD CONSTRAINT permission_restrictions_pkey PRIMARY KEY (id);


--
-- TOC entry 9456 (class 2606 OID 247597)
-- Name: cities pk_cities; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT pk_cities PRIMARY KEY (id);


--
-- TOC entry 9454 (class 2606 OID 247587)
-- Name: claims pk_claims; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claims
    ADD CONSTRAINT pk_claims PRIMARY KEY (id);


--
-- TOC entry 9459 (class 2606 OID 247581)
-- Name: companies pk_companies; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT pk_companies PRIMARY KEY (id);


--
-- TOC entry 9461 (class 2606 OID 247593)
-- Name: countries pk_countries; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT pk_countries PRIMARY KEY (id);


--
-- TOC entry 9463 (class 2606 OID 247603)
-- Name: coverages pk_coverages; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coverages
    ADD CONSTRAINT pk_coverages PRIMARY KEY (id);


--
-- TOC entry 9465 (class 2606 OID 247870)
-- Name: document_versions pk_document_versions_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT pk_document_versions_id PRIMARY KEY (id);


--
-- TOC entry 9467 (class 2606 OID 247599)
-- Name: groups pk_groups; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT pk_groups PRIMARY KEY (id);


--
-- TOC entry 9482 (class 2606 OID 247583)
-- Name: members pk_members; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT pk_members PRIMARY KEY (id);


--
-- TOC entry 9490 (class 2606 OID 247601)
-- Name: plans pk_plans; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT pk_plans PRIMARY KEY (id);


--
-- TOC entry 9488 (class 2606 OID 247585)
-- Name: policies pk_policies; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT pk_policies PRIMARY KEY (id);


--
-- TOC entry 9495 (class 2606 OID 247595)
-- Name: regions pk_regions; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT pk_regions PRIMARY KEY (id);


--
-- TOC entry 9506 (class 2606 OID 247591)
-- Name: roles pk_roles; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT pk_roles PRIMARY KEY (id);


--
-- TOC entry 9508 (class 2606 OID 247589)
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- TOC entry 9543 (class 2606 OID 248002)
-- Name: plan_benefit_schedules plan_benefit_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_benefit_schedules
    ADD CONSTRAINT plan_benefit_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 9556 (class 2606 OID 248087)
-- Name: policy_benefit_overrides policy_benefit_overrides_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_benefit_overrides
    ADD CONSTRAINT policy_benefit_overrides_pkey PRIMARY KEY (id);


--
-- TOC entry 9570 (class 2606 OID 248375)
-- Name: policy_cancellations policy_cancellations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_pkey PRIMARY KEY (id);


--
-- TOC entry 9607 (class 2606 OID 248596)
-- Name: policy_flags policy_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_flags
    ADD CONSTRAINT policy_flags_pkey PRIMARY KEY (id);


--
-- TOC entry 9706 (class 2606 OID 249400)
-- Name: pool_participations pool_participations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pool_participations
    ADD CONSTRAINT pool_participations_pkey PRIMARY KEY (id);


--
-- TOC entry 9733 (class 2606 OID 250186)
-- Name: prediction_batch_jobs prediction_batch_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_batch_jobs
    ADD CONSTRAINT prediction_batch_jobs_pkey PRIMARY KEY (id);


--
-- TOC entry 9729 (class 2606 OID 250160)
-- Name: prediction_models prediction_models_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_models
    ADD CONSTRAINT prediction_models_pkey PRIMARY KEY (id);


--
-- TOC entry 9731 (class 2606 OID 250171)
-- Name: prediction_results prediction_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_results
    ADD CONSTRAINT prediction_results_pkey PRIMARY KEY (id);


--
-- TOC entry 9492 (class 2606 OID 248358)
-- Name: premium_invoices premium_invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premium_invoices
    ADD CONSTRAINT premium_invoices_pkey PRIMARY KEY (id);


--
-- TOC entry 9524 (class 2606 OID 247880)
-- Name: public_card_views public_card_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.public_card_views
    ADD CONSTRAINT public_card_views_pkey PRIMARY KEY (id);


--
-- TOC entry 9526 (class 2606 OID 247882)
-- Name: public_card_views public_card_views_public_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.public_card_views
    ADD CONSTRAINT public_card_views_public_token_key UNIQUE (public_token);


--
-- TOC entry 9534 (class 2606 OID 247918)
-- Name: qr_styles qr_styles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_styles
    ADD CONSTRAINT qr_styles_pkey PRIMARY KEY (id);


--
-- TOC entry 9532 (class 2606 OID 247905)
-- Name: qr_view_logs qr_view_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qr_view_logs
    ADD CONSTRAINT qr_view_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 9497 (class 2606 OID 249327)
-- Name: reinsurance_agreements reinsurance_agreements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reinsurance_agreements
    ADD CONSTRAINT reinsurance_agreements_pkey PRIMARY KEY (id);


--
-- TOC entry 9814 (class 2606 OID 250798)
-- Name: report_analytics report_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_analytics
    ADD CONSTRAINT report_analytics_pkey PRIMARY KEY (id);


--
-- TOC entry 9812 (class 2606 OID 250770)
-- Name: report_comments report_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_comments
    ADD CONSTRAINT report_comments_pkey PRIMARY KEY (id);


--
-- TOC entry 9791 (class 2606 OID 250689)
-- Name: report_components report_components_component_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_components
    ADD CONSTRAINT report_components_component_name_key UNIQUE (component_name);


--
-- TOC entry 9793 (class 2606 OID 250687)
-- Name: report_components report_components_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_components
    ADD CONSTRAINT report_components_pkey PRIMARY KEY (id);


--
-- TOC entry 9816 (class 2606 OID 250819)
-- Name: report_favorites report_favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_favorites
    ADD CONSTRAINT report_favorites_pkey PRIMARY KEY (id);


--
-- TOC entry 9798 (class 2606 OID 250709)
-- Name: report_instances report_instances_cache_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_instances
    ADD CONSTRAINT report_instances_cache_key_key UNIQUE (cache_key);


--
-- TOC entry 9800 (class 2606 OID 250707)
-- Name: report_instances report_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_instances
    ADD CONSTRAINT report_instances_pkey PRIMARY KEY (id);


--
-- TOC entry 9804 (class 2606 OID 250731)
-- Name: report_schedules report_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 9806 (class 2606 OID 250733)
-- Name: report_schedules report_schedules_schedule_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_schedule_name_key UNIQUE (schedule_name);


--
-- TOC entry 9808 (class 2606 OID 250750)
-- Name: report_shares report_shares_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_shares
    ADD CONSTRAINT report_shares_pkey PRIMARY KEY (id);


--
-- TOC entry 9810 (class 2606 OID 250752)
-- Name: report_shares report_shares_share_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_shares
    ADD CONSTRAINT report_shares_share_token_key UNIQUE (share_token);


--
-- TOC entry 9504 (class 2606 OID 250672)
-- Name: report_templates report_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 9650 (class 2606 OID 248971)
-- Name: saas_feature_flags saas_feature_flags_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_feature_flags
    ADD CONSTRAINT saas_feature_flags_code_key UNIQUE (code);


--
-- TOC entry 9652 (class 2606 OID 248969)
-- Name: saas_feature_flags saas_feature_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_feature_flags
    ADD CONSTRAINT saas_feature_flags_pkey PRIMARY KEY (id);


--
-- TOC entry 9654 (class 2606 OID 248977)
-- Name: saas_plan_features saas_plan_features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plan_features
    ADD CONSTRAINT saas_plan_features_pkey PRIMARY KEY (id);


--
-- TOC entry 9646 (class 2606 OID 248961)
-- Name: saas_plans saas_plans_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plans
    ADD CONSTRAINT saas_plans_code_key UNIQUE (code);


--
-- TOC entry 9648 (class 2606 OID 248959)
-- Name: saas_plans saas_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plans
    ADD CONSTRAINT saas_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 9737 (class 2606 OID 250214)
-- Name: serendipity_discoveries serendipity_discoveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serendipity_discoveries
    ADD CONSTRAINT serendipity_discoveries_pkey PRIMARY KEY (id);


--
-- TOC entry 9735 (class 2606 OID 250203)
-- Name: serendipity_patterns serendipity_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serendipity_patterns
    ADD CONSTRAINT serendipity_patterns_pkey PRIMARY KEY (id);


--
-- TOC entry 9739 (class 2606 OID 250230)
-- Name: serendipity_recommendations serendipity_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serendipity_recommendations
    ADD CONSTRAINT serendipity_recommendations_pkey PRIMARY KEY (id);


--
-- TOC entry 9745 (class 2606 OID 250272)
-- Name: simulation_results simulation_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_results
    ADD CONSTRAINT simulation_results_pkey PRIMARY KEY (id);


--
-- TOC entry 9743 (class 2606 OID 250258)
-- Name: simulation_scenarios simulation_scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_scenarios
    ADD CONSTRAINT simulation_scenarios_pkey PRIMARY KEY (id);


--
-- TOC entry 9747 (class 2606 OID 250287)
-- Name: simulation_validation simulation_validation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_validation
    ADD CONSTRAINT simulation_validation_pkey PRIMARY KEY (id);


--
-- TOC entry 9775 (class 2606 OID 250481)
-- Name: skills_demand_forecast skills_demand_forecast_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_demand_forecast
    ADD CONSTRAINT skills_demand_forecast_pkey PRIMARY KEY (id);


--
-- TOC entry 9779 (class 2606 OID 250507)
-- Name: skills_development_plans skills_development_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_development_plans
    ADD CONSTRAINT skills_development_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 9777 (class 2606 OID 250497)
-- Name: skills_gap_analysis skills_gap_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_gap_analysis
    ADD CONSTRAINT skills_gap_analysis_pkey PRIMARY KEY (id);


--
-- TOC entry 9771 (class 2606 OID 250456)
-- Name: skills_taxonomy skills_taxonomy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_taxonomy
    ADD CONSTRAINT skills_taxonomy_pkey PRIMARY KEY (id);


--
-- TOC entry 9637 (class 2606 OID 248887)
-- Name: support_response_templates support_response_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_response_templates
    ADD CONSTRAINT support_response_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 9510 (class 2606 OID 247720)
-- Name: system_configuration system_configuration_category_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_configuration
    ADD CONSTRAINT system_configuration_category_key_key UNIQUE (category, key);


--
-- TOC entry 9512 (class 2606 OID 247718)
-- Name: system_configuration system_configuration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_configuration
    ADD CONSTRAINT system_configuration_pkey PRIMARY KEY (id);


--
-- TOC entry 9593 (class 2606 OID 248514)
-- Name: system_flags system_flags_flag_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_flag_name_key UNIQUE (flag_name);


--
-- TOC entry 9595 (class 2606 OID 248512)
-- Name: system_flags system_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_pkey PRIMARY KEY (id);


--
-- TOC entry 9753 (class 2606 OID 250327)
-- Name: system_resilience_metrics system_resilience_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_resilience_metrics
    ADD CONSTRAINT system_resilience_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 9708 (class 2606 OID 249899)
-- Name: telematics_data telematics_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telematics_data
    ADD CONSTRAINT telematics_data_pkey PRIMARY KEY (id);


--
-- TOC entry 9635 (class 2606 OID 248880)
-- Name: ticket_categories ticket_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_categories
    ADD CONSTRAINT ticket_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 9633 (class 2606 OID 248868)
-- Name: ticket_requests ticket_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_requests
    ADD CONSTRAINT ticket_requests_pkey PRIMARY KEY (id);


--
-- TOC entry 9703 (class 2606 OID 249385)
-- Name: treaty_reinstatements treaty_reinstatements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.treaty_reinstatements
    ADD CONSTRAINT treaty_reinstatements_pkey PRIMARY KEY (id);


--
-- TOC entry 9578 (class 2606 OID 248417)
-- Name: member_benefit_usage unique_member_benefit_period; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT unique_member_benefit_period UNIQUE (member_id, policy_id, benefit_type, period_start_date, period_type);


--
-- TOC entry 9681 (class 2606 OID 249126)
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- TOC entry 9759 (class 2606 OID 250363)
-- Name: universe_outcomes universe_outcomes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universe_outcomes
    ADD CONSTRAINT universe_outcomes_pkey PRIMARY KEY (id);


--
-- TOC entry 9761 (class 2606 OID 250378)
-- Name: universe_recommendations universe_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universe_recommendations
    ADD CONSTRAINT universe_recommendations_pkey PRIMARY KEY (id);


--
-- TOC entry 9623 (class 2606 OID 248769)
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- TOC entry 9716 (class 2606 OID 250064)
-- Name: workflow_queue workflow_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_queue
    ADD CONSTRAINT workflow_queue_pkey PRIMARY KEY (id);


--
-- TOC entry 9673 (class 1259 OID 250104)
-- Name: idx_activity_log_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_activity_log_user_created ON public.activity_log USING btree (user_id, created_at);


--
-- TOC entry 9697 (class 1259 OID 249401)
-- Name: idx_aggregate_covers_agreement; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_aggregate_covers_agreement ON public.aggregate_covers USING btree (agreement_id);


--
-- TOC entry 9581 (class 1259 OID 248625)
-- Name: idx_benefit_alert_logs_alert_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_alert_logs_alert_type ON public.benefit_alert_logs USING btree (alert_type);


--
-- TOC entry 9582 (class 1259 OID 248624)
-- Name: idx_benefit_alert_logs_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_alert_logs_member_id ON public.benefit_alert_logs USING btree (member_id);


--
-- TOC entry 9583 (class 1259 OID 248626)
-- Name: idx_benefit_alert_logs_sent_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_alert_logs_sent_at ON public.benefit_alert_logs USING btree (sent_at DESC);


--
-- TOC entry 9564 (class 1259 OID 248150)
-- Name: idx_benefit_change_log_changed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_change_log_changed_at ON public.benefit_change_log USING btree (changed_at DESC);


--
-- TOC entry 9565 (class 1259 OID 248149)
-- Name: idx_benefit_change_log_schedule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_change_log_schedule_id ON public.benefit_change_log USING btree (benefit_schedule_id);


--
-- TOC entry 9551 (class 1259 OID 248146)
-- Name: idx_benefit_conditions_schedule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_conditions_schedule_id ON public.benefit_conditions USING btree (benefit_schedule_id);


--
-- TOC entry 9548 (class 1259 OID 248145)
-- Name: idx_benefit_translations_schedule_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_benefit_translations_schedule_lang ON public.benefit_translations USING btree (benefit_schedule_id, language_code);


--
-- TOC entry 9700 (class 1259 OID 249402)
-- Name: idx_bordereau_reports_agreement; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bordereau_reports_agreement ON public.bordereau_reports USING btree (agreement_id, report_period_start);


--
-- TOC entry 9615 (class 1259 OID 248849)
-- Name: idx_broker_assignments_broker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_broker_assignments_broker ON public.broker_assignments USING btree (broker_id);


--
-- TOC entry 9612 (class 1259 OID 248848)
-- Name: idx_brokers_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_brokers_active ON public.brokers USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 9782 (class 1259 OID 250535)
-- Name: idx_business_intelligence_alert_configurations; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_alert_configurations ON public.business_intelligence USING gin (alert_configurations);


--
-- TOC entry 9783 (class 1259 OID 250530)
-- Name: idx_business_intelligence_analysis_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_analysis_type ON public.business_intelligence USING btree (analysis_type);


--
-- TOC entry 9784 (class 1259 OID 250531)
-- Name: idx_business_intelligence_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_created_at ON public.business_intelligence USING btree (created_at);


--
-- TOC entry 9785 (class 1259 OID 250534)
-- Name: idx_business_intelligence_dashboard_subscriptions; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_dashboard_subscriptions ON public.business_intelligence USING gin (dashboard_subscriptions);


--
-- TOC entry 9786 (class 1259 OID 250537)
-- Name: idx_business_intelligence_insights; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_insights ON public.business_intelligence USING gin (insights);


--
-- TOC entry 9787 (class 1259 OID 250532)
-- Name: idx_business_intelligence_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_is_active ON public.business_intelligence USING btree (is_active);


--
-- TOC entry 9788 (class 1259 OID 250536)
-- Name: idx_business_intelligence_key_metrics; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_key_metrics ON public.business_intelligence USING gin (key_metrics);


--
-- TOC entry 9789 (class 1259 OID 250533)
-- Name: idx_business_intelligence_real_time_metrics; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_business_intelligence_real_time_metrics ON public.business_intelligence USING gin (real_time_metrics);


--
-- TOC entry 9694 (class 1259 OID 249404)
-- Name: idx_catastrophe_models_peril_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_catastrophe_models_peril_region ON public.catastrophe_models USING btree (peril_type, geographic_region);


--
-- TOC entry 9586 (class 1259 OID 248628)
-- Name: idx_claim_action_logs_action_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claim_action_logs_action_type ON public.claim_action_logs USING btree (action_type);


--
-- TOC entry 9587 (class 1259 OID 248627)
-- Name: idx_claim_action_logs_claim_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claim_action_logs_claim_id ON public.claim_action_logs USING btree (claim_id);


--
-- TOC entry 9588 (class 1259 OID 248629)
-- Name: idx_claim_action_logs_taken_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claim_action_logs_taken_at ON public.claim_action_logs USING btree (action_taken_at DESC);


--
-- TOC entry 9449 (class 1259 OID 247681)
-- Name: idx_claims_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claims_member_id ON public.claims USING btree (member_id);


--
-- TOC entry 9450 (class 1259 OID 250102)
-- Name: idx_claims_member_policy_status_concurrent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claims_member_policy_status_concurrent ON public.claims USING btree (member_id, policy_id, status);


--
-- TOC entry 9451 (class 1259 OID 247680)
-- Name: idx_claims_policy_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claims_policy_id ON public.claims USING btree (policy_id);


--
-- TOC entry 9452 (class 1259 OID 247685)
-- Name: idx_claims_status_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_claims_status_date ON public.claims USING btree (status, created_at DESC);


--
-- TOC entry 9598 (class 1259 OID 248636)
-- Name: idx_collections_logs_next_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collections_logs_next_action ON public.collections_logs USING btree (next_action_date);


--
-- TOC entry 9599 (class 1259 OID 248635)
-- Name: idx_collections_logs_overdue; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collections_logs_overdue ON public.collections_logs USING btree (days_overdue DESC);


--
-- TOC entry 9600 (class 1259 OID 248633)
-- Name: idx_collections_logs_policy_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collections_logs_policy_id ON public.collections_logs USING btree (policy_id);


--
-- TOC entry 9601 (class 1259 OID 248634)
-- Name: idx_collections_logs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collections_logs_status ON public.collections_logs USING btree (collection_status);


--
-- TOC entry 9457 (class 1259 OID 247689)
-- Name: idx_companies_name_search; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_companies_name_search ON public.companies USING gin (to_tsvector('english'::regconfig, (name)::text));


--
-- TOC entry 9643 (class 1259 OID 248934)
-- Name: idx_custom_field_values_entity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custom_field_values_entity ON public.custom_field_values USING btree (entity_id);


--
-- TOC entry 9644 (class 1259 OID 248933)
-- Name: idx_custom_field_values_field; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custom_field_values_field ON public.custom_field_values USING btree (custom_field_id);


--
-- TOC entry 9640 (class 1259 OID 248932)
-- Name: idx_custom_fields_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_custom_fields_entity_type ON public.custom_fields USING btree (entity_type);


--
-- TOC entry 9618 (class 1259 OID 248851)
-- Name: idx_delegates_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_delegates_active ON public.delegates USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 9619 (class 1259 OID 248850)
-- Name: idx_delegates_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_delegates_company ON public.delegates USING btree (company_id);


--
-- TOC entry 9472 (class 1259 OID 249699)
-- Name: idx_iot_devices_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_iot_devices_type ON public.iot_devices USING btree (device_type_id);


--
-- TOC entry 9473 (class 1259 OID 249700)
-- Name: idx_iot_devices_type_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_iot_devices_type_active ON public.iot_devices USING btree (device_type_id, status) WHERE ((status)::text = 'active'::text);


--
-- TOC entry 9571 (class 1259 OID 248621)
-- Name: idx_member_benefit_usage_benefit_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_member_benefit_usage_benefit_type ON public.member_benefit_usage USING btree (benefit_type);


--
-- TOC entry 9572 (class 1259 OID 248622)
-- Name: idx_member_benefit_usage_exhausted; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_member_benefit_usage_exhausted ON public.member_benefit_usage USING btree (is_exhausted) WHERE (is_exhausted = true);


--
-- TOC entry 9573 (class 1259 OID 248620)
-- Name: idx_member_benefit_usage_member_policy; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_member_benefit_usage_member_policy ON public.member_benefit_usage USING btree (member_id, policy_id);


--
-- TOC entry 9574 (class 1259 OID 248623)
-- Name: idx_member_benefit_usage_utilization; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_member_benefit_usage_utilization ON public.member_benefit_usage USING btree (utilization_percentage DESC);


--
-- TOC entry 9557 (class 1259 OID 248148)
-- Name: idx_member_utilization_member_policy; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_member_utilization_member_policy ON public.member_benefit_utilization USING btree (member_id, policy_id);


--
-- TOC entry 9476 (class 1259 OID 247687)
-- Name: idx_members_active_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_members_active_company ON public.members USING btree (is_active, company_id) WHERE (is_active = true);


--
-- TOC entry 9477 (class 1259 OID 250101)
-- Name: idx_members_company_active_concurrent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_members_company_active_concurrent ON public.members USING btree (company_id, is_active) WHERE (is_active = true);


--
-- TOC entry 9478 (class 1259 OID 247684)
-- Name: idx_members_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_members_company_id ON public.members USING btree (company_id);


--
-- TOC entry 9479 (class 1259 OID 247688)
-- Name: idx_members_name_search; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_members_name_search ON public.members USING gin (to_tsvector('english'::regconfig, (((first_name)::text || ' '::text) || (last_name)::text)));


--
-- TOC entry 9480 (class 1259 OID 250103)
-- Name: idx_members_search_concurrent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_members_search_concurrent ON public.members USING gin (to_tsvector('english'::regconfig, (((((COALESCE(full_name, ''::character varying))::text || ' '::text) || (COALESCE(email, ''::character varying))::text) || ' '::text) || (COALESCE(phone, ''::character varying))::text)));


--
-- TOC entry 9717 (class 1259 OID 250105)
-- Name: idx_notification_queue_recipient_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_queue_recipient_status ON public.notification_queue USING btree (recipient_id, status, scheduled_at);


--
-- TOC entry 9539 (class 1259 OID 248144)
-- Name: idx_plan_benefit_schedules_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_benefit_schedules_active ON public.plan_benefit_schedules USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 9540 (class 1259 OID 248143)
-- Name: idx_plan_benefit_schedules_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_benefit_schedules_category_id ON public.plan_benefit_schedules USING btree (category_id);


--
-- TOC entry 9541 (class 1259 OID 248142)
-- Name: idx_plan_benefit_schedules_plan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_benefit_schedules_plan_id ON public.plan_benefit_schedules USING btree (plan_id);


--
-- TOC entry 9483 (class 1259 OID 250099)
-- Name: idx_policies_active_status_concurrent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policies_active_status_concurrent ON public.policies USING btree (status) WHERE (status = 'active'::public.policy_status);


--
-- TOC entry 9484 (class 1259 OID 247682)
-- Name: idx_policies_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policies_member_id ON public.policies USING btree (member_id);


--
-- TOC entry 9485 (class 1259 OID 247683)
-- Name: idx_policies_plan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policies_plan_id ON public.policies USING btree (plan_id);


--
-- TOC entry 9486 (class 1259 OID 247686)
-- Name: idx_policies_status_effective; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policies_status_effective ON public.policies USING btree (status, effective_date);


--
-- TOC entry 9566 (class 1259 OID 248619)
-- Name: idx_policy_cancellations_effective_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_cancellations_effective_date ON public.policy_cancellations USING btree (effective_date);


--
-- TOC entry 9567 (class 1259 OID 248617)
-- Name: idx_policy_cancellations_policy_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_cancellations_policy_id ON public.policy_cancellations USING btree (policy_id);


--
-- TOC entry 9568 (class 1259 OID 248618)
-- Name: idx_policy_cancellations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_cancellations_status ON public.policy_cancellations USING btree (status);


--
-- TOC entry 9602 (class 1259 OID 248639)
-- Name: idx_policy_flags_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_flags_active ON public.policy_flags USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 9603 (class 1259 OID 248637)
-- Name: idx_policy_flags_policy_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_flags_policy_id ON public.policy_flags USING btree (policy_id);


--
-- TOC entry 9604 (class 1259 OID 248640)
-- Name: idx_policy_flags_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_flags_severity ON public.policy_flags USING btree (flag_severity);


--
-- TOC entry 9605 (class 1259 OID 248638)
-- Name: idx_policy_flags_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_flags_type ON public.policy_flags USING btree (flag_type);


--
-- TOC entry 9554 (class 1259 OID 248147)
-- Name: idx_policy_overrides_policy_benefit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_policy_overrides_policy_benefit ON public.policy_benefit_overrides USING btree (policy_id, benefit_schedule_id);


--
-- TOC entry 9704 (class 1259 OID 249405)
-- Name: idx_pool_participations_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pool_participations_type ON public.pool_participations USING btree (pool_type, is_active);


--
-- TOC entry 9493 (class 1259 OID 250100)
-- Name: idx_quotations_active_concurrent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quotations_active_concurrent ON public.quotations USING btree (status, created_at) WHERE ((status)::text = 'active'::text);


--
-- TOC entry 9794 (class 1259 OID 250837)
-- Name: idx_report_instances_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_instances_created_at ON public.report_instances USING btree (created_at);


--
-- TOC entry 9795 (class 1259 OID 250836)
-- Name: idx_report_instances_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_instances_status ON public.report_instances USING btree (generation_status);


--
-- TOC entry 9796 (class 1259 OID 250835)
-- Name: idx_report_instances_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_instances_template_id ON public.report_instances USING btree (template_id);


--
-- TOC entry 9801 (class 1259 OID 250839)
-- Name: idx_report_schedules_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_active ON public.report_schedules USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 9802 (class 1259 OID 250838)
-- Name: idx_report_schedules_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_template_id ON public.report_schedules USING btree (template_id);


--
-- TOC entry 9498 (class 1259 OID 250830)
-- Name: idx_report_templates_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_category ON public.report_templates USING btree (template_category);


--
-- TOC entry 9499 (class 1259 OID 250832)
-- Name: idx_report_templates_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_created_at ON public.report_templates USING btree (created_at);


--
-- TOC entry 9500 (class 1259 OID 250834)
-- Name: idx_report_templates_data_sources; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_data_sources ON public.report_templates USING gin (data_sources);


--
-- TOC entry 9501 (class 1259 OID 250831)
-- Name: idx_report_templates_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_type ON public.report_templates USING btree (template_type);


--
-- TOC entry 9502 (class 1259 OID 250833)
-- Name: idx_report_templates_visual_layout; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_visual_layout ON public.report_templates USING gin (visual_layout);


--
-- TOC entry 9589 (class 1259 OID 248632)
-- Name: idx_system_flags_company; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_flags_company ON public.system_flags USING btree (company_id);


--
-- TOC entry 9590 (class 1259 OID 248631)
-- Name: idx_system_flags_enabled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_flags_enabled ON public.system_flags USING btree (is_enabled) WHERE (is_enabled = true);


--
-- TOC entry 9591 (class 1259 OID 248630)
-- Name: idx_system_flags_flag_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_flags_flag_name ON public.system_flags USING btree (flag_name);


--
-- TOC entry 9701 (class 1259 OID 249403)
-- Name: idx_treaty_reinstatements_agreement; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_treaty_reinstatements_agreement ON public.treaty_reinstatements USING btree (agreement_id);


--
-- TOC entry 9620 (class 1259 OID 248853)
-- Name: idx_user_preferences_member; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_user_preferences_member ON public.user_preferences USING btree (member_id, preference_category, preference_key) WHERE (member_id IS NOT NULL);


--
-- TOC entry 9621 (class 1259 OID 248852)
-- Name: idx_user_preferences_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_user_preferences_user ON public.user_preferences USING btree (user_id, preference_category, preference_key) WHERE (user_id IS NOT NULL);


--
-- TOC entry 9713 (class 1259 OID 250106)
-- Name: idx_workflow_queue_entity_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_queue_entity_type_status ON public.workflow_queue USING btree (entity_type, status, scheduled_at);


--
-- TOC entry 9714 (class 1259 OID 250065)
-- Name: idx_workflow_queue_processing; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_queue_processing ON public.workflow_queue USING btree (status, priority, scheduled_at) WHERE ((status)::text = 'pending'::text);


--
-- TOC entry 9951 (class 2620 OID 247934)
-- Name: companies trg_sync_company_name_to_policies; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sync_company_name_to_policies AFTER UPDATE OF name ON public.companies FOR EACH ROW EXECUTE FUNCTION public.sync_company_name_to_policies();


--
-- TOC entry 9952 (class 2620 OID 247932)
-- Name: groups trg_sync_group_name_to_documents; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sync_group_name_to_documents AFTER UPDATE OF name ON public.groups FOR EACH ROW EXECUTE FUNCTION public.sync_group_name_to_documents();


--
-- TOC entry 9953 (class 2620 OID 247930)
-- Name: members trg_sync_member_name_to_claims; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sync_member_name_to_claims AFTER UPDATE OF full_name ON public.members FOR EACH ROW EXECUTE FUNCTION public.sync_member_name_to_claims();


--
-- TOC entry 9957 (class 2620 OID 247936)
-- Name: providers trg_sync_provider_name_to_claims; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_sync_provider_name_to_claims AFTER UPDATE OF name ON public.providers FOR EACH ROW EXECUTE FUNCTION public.sync_provider_name_to_claims();


--
-- TOC entry 9949 (class 2620 OID 250086)
-- Name: claims validate_claim_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER validate_claim_trigger BEFORE INSERT OR UPDATE ON public.claims FOR EACH ROW EXECUTE FUNCTION public.validate_claim_amounts();


--
-- TOC entry 9954 (class 2620 OID 250087)
-- Name: members validate_member_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER validate_member_trigger BEFORE INSERT OR UPDATE ON public.members FOR EACH ROW EXECUTE FUNCTION public.validate_member_data();


--
-- TOC entry 9955 (class 2620 OID 250085)
-- Name: policies validate_policy_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER validate_policy_trigger BEFORE INSERT OR UPDATE ON public.policies FOR EACH ROW EXECUTE FUNCTION public.validate_policy_dates();


--
-- TOC entry 9950 (class 2620 OID 250089)
-- Name: claims workflow_claims_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER workflow_claims_trigger AFTER INSERT OR UPDATE ON public.claims FOR EACH ROW EXECUTE FUNCTION public.trigger_workflow_automation();


--
-- TOC entry 9956 (class 2620 OID 250088)
-- Name: policies workflow_policies_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER workflow_policies_trigger AFTER UPDATE ON public.policies FOR EACH ROW EXECUTE FUNCTION public.trigger_workflow_automation();


--
-- TOC entry 9907 (class 2606 OID 249079)
-- Name: activity_log activity_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 9839 (class 2606 OID 247780)
-- Name: ai_ocr_results ai_ocr_results_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_ocr_results
    ADD CONSTRAINT ai_ocr_results_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.ai_tasks(id) ON DELETE CASCADE;


--
-- TOC entry 9896 (class 2606 OID 248843)
-- Name: ai_task_templates ai_task_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_task_templates
    ADD CONSTRAINT ai_task_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9864 (class 2606 OID 248460)
-- Name: benefit_alert_logs benefit_alert_logs_member_benefit_usage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_alert_logs
    ADD CONSTRAINT benefit_alert_logs_member_benefit_usage_id_fkey FOREIGN KEY (member_benefit_usage_id) REFERENCES public.member_benefit_usage(id) ON DELETE CASCADE;


--
-- TOC entry 9865 (class 2606 OID 248465)
-- Name: benefit_alert_logs benefit_alert_logs_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_alert_logs
    ADD CONSTRAINT benefit_alert_logs_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9853 (class 2606 OID 248137)
-- Name: benefit_change_log benefit_change_log_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_change_log
    ADD CONSTRAINT benefit_change_log_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE SET NULL;


--
-- TOC entry 9846 (class 2606 OID 248049)
-- Name: benefit_conditions benefit_conditions_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_conditions
    ADD CONSTRAINT benefit_conditions_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE CASCADE;


--
-- TOC entry 9847 (class 2606 OID 248069)
-- Name: benefit_preapproval_rules benefit_preapproval_rules_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_preapproval_rules
    ADD CONSTRAINT benefit_preapproval_rules_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE CASCADE;


--
-- TOC entry 9845 (class 2606 OID 248030)
-- Name: benefit_translations benefit_translations_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.benefit_translations
    ADD CONSTRAINT benefit_translations_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE CASCADE;


--
-- TOC entry 9921 (class 2606 OID 250144)
-- Name: bi_dashboard_cache bi_dashboard_cache_widget_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bi_dashboard_cache
    ADD CONSTRAINT bi_dashboard_cache_widget_id_fkey FOREIGN KEY (widget_id) REFERENCES public.bi_widgets(id);


--
-- TOC entry 9920 (class 2606 OID 250129)
-- Name: bi_widgets bi_widgets_dashboard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bi_widgets
    ADD CONSTRAINT bi_widgets_dashboard_id_fkey FOREIGN KEY (dashboard_id) REFERENCES public.bi_dashboards(id);


--
-- TOC entry 9911 (class 2606 OID 249227)
-- Name: bot_executions bot_executions_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bot_executions
    ADD CONSTRAINT bot_executions_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.automation_workflows(id);


--
-- TOC entry 9884 (class 2606 OID 248696)
-- Name: broker_assignments broker_assignments_broker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_broker_id_fkey FOREIGN KEY (broker_id) REFERENCES public.brokers(id);


--
-- TOC entry 9885 (class 2606 OID 248701)
-- Name: broker_assignments broker_assignments_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 9886 (class 2606 OID 248716)
-- Name: broker_assignments broker_assignments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9887 (class 2606 OID 248706)
-- Name: broker_assignments broker_assignments_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- TOC entry 9888 (class 2606 OID 248711)
-- Name: broker_assignments broker_assignments_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.broker_assignments
    ADD CONSTRAINT broker_assignments_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id);


--
-- TOC entry 9882 (class 2606 OID 248677)
-- Name: brokers brokers_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brokers
    ADD CONSTRAINT brokers_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9883 (class 2606 OID 248682)
-- Name: brokers brokers_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brokers
    ADD CONSTRAINT brokers_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9906 (class 2606 OID 249066)
-- Name: browser_fingerprints browser_fingerprints_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.browser_fingerprints
    ADD CONSTRAINT browser_fingerprints_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 9929 (class 2606 OID 250313)
-- Name: chaos_experiment_runs chaos_experiment_runs_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chaos_experiment_runs
    ADD CONSTRAINT chaos_experiment_runs_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.chaos_experiments(id);


--
-- TOC entry 9866 (class 2606 OID 248492)
-- Name: claim_action_logs claim_action_logs_action_taken_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_action_logs
    ADD CONSTRAINT claim_action_logs_action_taken_by_fkey FOREIGN KEY (action_taken_by) REFERENCES public.users(id);


--
-- TOC entry 9867 (class 2606 OID 248487)
-- Name: claim_action_logs claim_action_logs_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_action_logs
    ADD CONSTRAINT claim_action_logs_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- TOC entry 9868 (class 2606 OID 248482)
-- Name: claim_action_logs claim_action_logs_claim_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_action_logs
    ADD CONSTRAINT claim_action_logs_claim_id_fkey FOREIGN KEY (claim_id) REFERENCES public.claims(id) ON DELETE CASCADE;


--
-- TOC entry 9895 (class 2606 OID 248798)
-- Name: claim_checklists claim_checklists_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claim_checklists
    ADD CONSTRAINT claim_checklists_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9872 (class 2606 OID 248563)
-- Name: collections_logs collections_logs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9873 (class 2606 OID 248553)
-- Name: collections_logs collections_logs_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.premium_invoices(id) ON DELETE SET NULL;


--
-- TOC entry 9874 (class 2606 OID 248558)
-- Name: collections_logs collections_logs_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9875 (class 2606 OID 248548)
-- Name: collections_logs collections_logs_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9876 (class 2606 OID 248568)
-- Name: collections_logs collections_logs_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT collections_logs_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9899 (class 2606 OID 248927)
-- Name: custom_field_values custom_field_values_custom_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.custom_field_values
    ADD CONSTRAINT custom_field_values_custom_field_id_fkey FOREIGN KEY (custom_field_id) REFERENCES public.custom_fields(id) ON DELETE CASCADE;


--
-- TOC entry 9912 (class 2606 OID 249241)
-- Name: customer_360_profiles customer_360_profiles_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_360_profiles
    ADD CONSTRAINT customer_360_profiles_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- TOC entry 9889 (class 2606 OID 248735)
-- Name: delegates delegates_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delegates
    ADD CONSTRAINT delegates_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 9890 (class 2606 OID 248745)
-- Name: delegates delegates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delegates
    ADD CONSTRAINT delegates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9891 (class 2606 OID 248740)
-- Name: delegates delegates_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delegates
    ADD CONSTRAINT delegates_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- TOC entry 9892 (class 2606 OID 248750)
-- Name: delegates delegates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.delegates
    ADD CONSTRAINT delegates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9908 (class 2606 OID 249112)
-- Name: departments departments_parent_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_parent_department_id_fkey FOREIGN KEY (parent_department_id) REFERENCES public.departments(id);


--
-- TOC entry 9841 (class 2606 OID 247924)
-- Name: document_public_tokens document_public_tokens_qr_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_public_tokens
    ADD CONSTRAINT document_public_tokens_qr_style_id_fkey FOREIGN KEY (qr_style_id) REFERENCES public.qr_styles(id);


--
-- TOC entry 9936 (class 2606 OID 250466)
-- Name: employee_skills employee_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_skills
    ADD CONSTRAINT employee_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills_taxonomy(id);


--
-- TOC entry 9948 (class 2606 OID 250870)
-- Name: external_field_mappings external_field_mappings_integration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.external_field_mappings
    ADD CONSTRAINT external_field_mappings_integration_id_fkey FOREIGN KEY (integration_id) REFERENCES public.external_services(id);


--
-- TOC entry 9913 (class 2606 OID 249349)
-- Name: aggregate_covers fk_aggregate_covers_agreement; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aggregate_covers
    ADD CONSTRAINT fk_aggregate_covers_agreement FOREIGN KEY (agreement_id) REFERENCES public.reinsurance_agreements(id) ON DELETE SET NULL;


--
-- TOC entry 9918 (class 2606 OID 250028)
-- Name: behavior_scores fk_behavior_scores_device; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavior_scores
    ADD CONSTRAINT fk_behavior_scores_device FOREIGN KEY (device_id) REFERENCES public.iot_devices(id) ON DELETE CASCADE;


--
-- TOC entry 9919 (class 2606 OID 250023)
-- Name: behavior_scores fk_behavior_scores_member; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavior_scores
    ADD CONSTRAINT fk_behavior_scores_member FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9914 (class 2606 OID 249371)
-- Name: bordereau_reports fk_bordereau_reports_agreement; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bordereau_reports
    ADD CONSTRAINT fk_bordereau_reports_agreement FOREIGN KEY (agreement_id) REFERENCES public.reinsurance_agreements(id) ON DELETE SET NULL;


--
-- TOC entry 9823 (class 2606 OID 247609)
-- Name: cities fk_cities_country_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT fk_cities_country_id FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE;


--
-- TOC entry 9824 (class 2606 OID 247614)
-- Name: cities fk_cities_region_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT fk_cities_region_id FOREIGN KEY (region_id) REFERENCES public.regions(id) ON DELETE SET NULL;


--
-- TOC entry 9821 (class 2606 OID 247674)
-- Name: claims fk_claims_member_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claims
    ADD CONSTRAINT fk_claims_member_id FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9822 (class 2606 OID 247669)
-- Name: claims fk_claims_policy_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.claims
    ADD CONSTRAINT fk_claims_policy_id FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9877 (class 2606 OID 248654)
-- Name: collections_logs fk_collections_invoice; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections_logs
    ADD CONSTRAINT fk_collections_invoice FOREIGN KEY (invoice_id) REFERENCES public.premium_invoices(id) ON DELETE SET NULL;


--
-- TOC entry 9825 (class 2606 OID 247619)
-- Name: groups fk_groups_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT fk_groups_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 9917 (class 2606 OID 250008)
-- Name: iot_alerts fk_iot_alerts_device; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_alerts
    ADD CONSTRAINT fk_iot_alerts_device FOREIGN KEY (device_id) REFERENCES public.iot_devices(id) ON DELETE CASCADE;


--
-- TOC entry 9826 (class 2606 OID 249706)
-- Name: iot_data_streams fk_iot_data_streams_device_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_data_streams
    ADD CONSTRAINT fk_iot_data_streams_device_id FOREIGN KEY (device_id) REFERENCES public.iot_devices(id);


--
-- TOC entry 9827 (class 2606 OID 249701)
-- Name: iot_devices fk_iot_devices_member_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iot_devices
    ADD CONSTRAINT fk_iot_devices_member_id FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9828 (class 2606 OID 247644)
-- Name: members fk_members_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT fk_members_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 9829 (class 2606 OID 247649)
-- Name: members fk_members_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT fk_members_group_id FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE SET NULL;


--
-- TOC entry 9833 (class 2606 OID 247639)
-- Name: plans fk_plans_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT fk_plans_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 9830 (class 2606 OID 247664)
-- Name: policies fk_policies_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 9831 (class 2606 OID 247654)
-- Name: policies fk_policies_member_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_member_id FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9832 (class 2606 OID 247659)
-- Name: policies fk_policies_plan_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_plan_id FOREIGN KEY (plan_id) REFERENCES public.plans(id) ON DELETE RESTRICT;


--
-- TOC entry 9834 (class 2606 OID 247604)
-- Name: regions fk_regions_country_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT fk_regions_country_id FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE;


--
-- TOC entry 9915 (class 2606 OID 249386)
-- Name: treaty_reinstatements fk_treaty_reinstatements_agreement; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.treaty_reinstatements
    ADD CONSTRAINT fk_treaty_reinstatements_agreement FOREIGN KEY (agreement_id) REFERENCES public.reinsurance_agreements(id) ON DELETE SET NULL;


--
-- TOC entry 9835 (class 2606 OID 247634)
-- Name: user_roles fk_user_roles_role_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_role_id FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 9836 (class 2606 OID 247629)
-- Name: user_roles fk_user_roles_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_user_id FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 9837 (class 2606 OID 247624)
-- Name: users fk_users_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 9903 (class 2606 OID 249009)
-- Name: knowledge_articles knowledge_articles_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_articles
    ADD CONSTRAINT knowledge_articles_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.knowledge_categories(id);


--
-- TOC entry 9904 (class 2606 OID 249014)
-- Name: knowledge_articles knowledge_articles_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_articles
    ADD CONSTRAINT knowledge_articles_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9902 (class 2606 OID 248995)
-- Name: knowledge_categories knowledge_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_categories
    ADD CONSTRAINT knowledge_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.knowledge_categories(id);


--
-- TOC entry 9905 (class 2606 OID 249046)
-- Name: login_devices login_devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.login_devices
    ADD CONSTRAINT login_devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 9935 (class 2606 OID 250428)
-- Name: market_impact_analysis market_impact_analysis_signal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_impact_analysis
    ADD CONSTRAINT market_impact_analysis_signal_id_fkey FOREIGN KEY (signal_id) REFERENCES public.market_signals(id);


--
-- TOC entry 9934 (class 2606 OID 250413)
-- Name: market_signals market_signals_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_signals
    ADD CONSTRAINT market_signals_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.market_data_sources(id);


--
-- TOC entry 9859 (class 2606 OID 248433)
-- Name: member_benefit_usage member_benefit_usage_coverage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_coverage_id_fkey FOREIGN KEY (coverage_id) REFERENCES public.coverages(id) ON DELETE SET NULL;


--
-- TOC entry 9860 (class 2606 OID 248438)
-- Name: member_benefit_usage member_benefit_usage_last_claim_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_last_claim_id_fkey FOREIGN KEY (last_claim_id) REFERENCES public.claims(id);


--
-- TOC entry 9861 (class 2606 OID 248418)
-- Name: member_benefit_usage member_benefit_usage_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9862 (class 2606 OID 248428)
-- Name: member_benefit_usage member_benefit_usage_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans(id) ON DELETE CASCADE;


--
-- TOC entry 9863 (class 2606 OID 248423)
-- Name: member_benefit_usage member_benefit_usage_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_usage
    ADD CONSTRAINT member_benefit_usage_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9850 (class 2606 OID 248122)
-- Name: member_benefit_utilization member_benefit_utilization_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_utilization
    ADD CONSTRAINT member_benefit_utilization_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE CASCADE;


--
-- TOC entry 9851 (class 2606 OID 248112)
-- Name: member_benefit_utilization member_benefit_utilization_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_utilization
    ADD CONSTRAINT member_benefit_utilization_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id) ON DELETE CASCADE;


--
-- TOC entry 9852 (class 2606 OID 248117)
-- Name: member_benefit_utilization member_benefit_utilization_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.member_benefit_utilization
    ADD CONSTRAINT member_benefit_utilization_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9930 (class 2606 OID 250350)
-- Name: parallel_scenarios parallel_scenarios_universe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parallel_scenarios
    ADD CONSTRAINT parallel_scenarios_universe_id_fkey FOREIGN KEY (universe_id) REFERENCES public.decision_universes(id);


--
-- TOC entry 9910 (class 2606 OID 249141)
-- Name: permission_restrictions permission_restrictions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permission_restrictions
    ADD CONSTRAINT permission_restrictions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- TOC entry 9842 (class 2606 OID 248013)
-- Name: plan_benefit_schedules plan_benefit_schedules_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_benefit_schedules
    ADD CONSTRAINT plan_benefit_schedules_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.benefit_categories(id) ON DELETE SET NULL;


--
-- TOC entry 9843 (class 2606 OID 248008)
-- Name: plan_benefit_schedules plan_benefit_schedules_coverage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_benefit_schedules
    ADD CONSTRAINT plan_benefit_schedules_coverage_id_fkey FOREIGN KEY (coverage_id) REFERENCES public.coverages(id) ON DELETE SET NULL;


--
-- TOC entry 9844 (class 2606 OID 248003)
-- Name: plan_benefit_schedules plan_benefit_schedules_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plan_benefit_schedules
    ADD CONSTRAINT plan_benefit_schedules_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans(id) ON DELETE CASCADE;


--
-- TOC entry 9848 (class 2606 OID 248093)
-- Name: policy_benefit_overrides policy_benefit_overrides_benefit_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_benefit_overrides
    ADD CONSTRAINT policy_benefit_overrides_benefit_schedule_id_fkey FOREIGN KEY (benefit_schedule_id) REFERENCES public.plan_benefit_schedules(id) ON DELETE CASCADE;


--
-- TOC entry 9849 (class 2606 OID 248088)
-- Name: policy_benefit_overrides policy_benefit_overrides_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_benefit_overrides
    ADD CONSTRAINT policy_benefit_overrides_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9854 (class 2606 OID 248386)
-- Name: policy_cancellations policy_cancellations_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- TOC entry 9855 (class 2606 OID 248391)
-- Name: policy_cancellations policy_cancellations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9856 (class 2606 OID 248376)
-- Name: policy_cancellations policy_cancellations_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE RESTRICT;


--
-- TOC entry 9857 (class 2606 OID 248381)
-- Name: policy_cancellations policy_cancellations_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_requested_by_fkey FOREIGN KEY (requested_by) REFERENCES public.users(id);


--
-- TOC entry 9858 (class 2606 OID 248396)
-- Name: policy_cancellations policy_cancellations_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_cancellations
    ADD CONSTRAINT policy_cancellations_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9878 (class 2606 OID 248607)
-- Name: policy_flags policy_flags_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_flags
    ADD CONSTRAINT policy_flags_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9879 (class 2606 OID 248597)
-- Name: policy_flags policy_flags_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_flags
    ADD CONSTRAINT policy_flags_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- TOC entry 9880 (class 2606 OID 248602)
-- Name: policy_flags policy_flags_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_flags
    ADD CONSTRAINT policy_flags_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- TOC entry 9881 (class 2606 OID 248612)
-- Name: policy_flags policy_flags_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.policy_flags
    ADD CONSTRAINT policy_flags_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9923 (class 2606 OID 250187)
-- Name: prediction_batch_jobs prediction_batch_jobs_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_batch_jobs
    ADD CONSTRAINT prediction_batch_jobs_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.prediction_models(id);


--
-- TOC entry 9922 (class 2606 OID 250172)
-- Name: prediction_results prediction_results_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_results
    ADD CONSTRAINT prediction_results_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.prediction_models(id);


--
-- TOC entry 9840 (class 2606 OID 247919)
-- Name: public_card_views public_card_views_qr_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.public_card_views
    ADD CONSTRAINT public_card_views_qr_style_id_fkey FOREIGN KEY (qr_style_id) REFERENCES public.qr_styles(id);


--
-- TOC entry 9944 (class 2606 OID 250799)
-- Name: report_analytics report_analytics_report_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_analytics
    ADD CONSTRAINT report_analytics_report_instance_id_fkey FOREIGN KEY (report_instance_id) REFERENCES public.report_instances(id) ON DELETE CASCADE;


--
-- TOC entry 9945 (class 2606 OID 250804)
-- Name: report_analytics report_analytics_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_analytics
    ADD CONSTRAINT report_analytics_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id) ON DELETE CASCADE;


--
-- TOC entry 9942 (class 2606 OID 250776)
-- Name: report_comments report_comments_parent_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_comments
    ADD CONSTRAINT report_comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.report_comments(id) ON DELETE CASCADE;


--
-- TOC entry 9943 (class 2606 OID 250771)
-- Name: report_comments report_comments_report_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_comments
    ADD CONSTRAINT report_comments_report_instance_id_fkey FOREIGN KEY (report_instance_id) REFERENCES public.report_instances(id) ON DELETE CASCADE;


--
-- TOC entry 9946 (class 2606 OID 250820)
-- Name: report_favorites report_favorites_report_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_favorites
    ADD CONSTRAINT report_favorites_report_instance_id_fkey FOREIGN KEY (report_instance_id) REFERENCES public.report_instances(id) ON DELETE CASCADE;


--
-- TOC entry 9947 (class 2606 OID 250825)
-- Name: report_favorites report_favorites_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_favorites
    ADD CONSTRAINT report_favorites_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id) ON DELETE CASCADE;


--
-- TOC entry 9939 (class 2606 OID 250710)
-- Name: report_instances report_instances_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_instances
    ADD CONSTRAINT report_instances_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id) ON DELETE CASCADE;


--
-- TOC entry 9940 (class 2606 OID 250734)
-- Name: report_schedules report_schedules_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(id) ON DELETE CASCADE;


--
-- TOC entry 9941 (class 2606 OID 250753)
-- Name: report_shares report_shares_report_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_shares
    ADD CONSTRAINT report_shares_report_instance_id_fkey FOREIGN KEY (report_instance_id) REFERENCES public.report_instances(id) ON DELETE CASCADE;


--
-- TOC entry 9900 (class 2606 OID 248983)
-- Name: saas_plan_features saas_plan_features_feature_flag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plan_features
    ADD CONSTRAINT saas_plan_features_feature_flag_id_fkey FOREIGN KEY (feature_flag_id) REFERENCES public.saas_feature_flags(id);


--
-- TOC entry 9901 (class 2606 OID 248978)
-- Name: saas_plan_features saas_plan_features_saas_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saas_plan_features
    ADD CONSTRAINT saas_plan_features_saas_plan_id_fkey FOREIGN KEY (saas_plan_id) REFERENCES public.saas_plans(id);


--
-- TOC entry 9924 (class 2606 OID 250215)
-- Name: serendipity_discoveries serendipity_discoveries_pattern_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serendipity_discoveries
    ADD CONSTRAINT serendipity_discoveries_pattern_id_fkey FOREIGN KEY (pattern_id) REFERENCES public.serendipity_patterns(id);


--
-- TOC entry 9925 (class 2606 OID 250231)
-- Name: serendipity_recommendations serendipity_recommendations_discovery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serendipity_recommendations
    ADD CONSTRAINT serendipity_recommendations_discovery_id_fkey FOREIGN KEY (discovery_id) REFERENCES public.serendipity_discoveries(id);


--
-- TOC entry 9927 (class 2606 OID 250273)
-- Name: simulation_results simulation_results_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_results
    ADD CONSTRAINT simulation_results_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.simulation_scenarios(id);


--
-- TOC entry 9926 (class 2606 OID 250259)
-- Name: simulation_scenarios simulation_scenarios_twin_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_scenarios
    ADD CONSTRAINT simulation_scenarios_twin_model_id_fkey FOREIGN KEY (twin_model_id) REFERENCES public.digital_twin_models(id);


--
-- TOC entry 9928 (class 2606 OID 250288)
-- Name: simulation_validation simulation_validation_simulation_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulation_validation
    ADD CONSTRAINT simulation_validation_simulation_result_id_fkey FOREIGN KEY (simulation_result_id) REFERENCES public.simulation_results(id);


--
-- TOC entry 9937 (class 2606 OID 250482)
-- Name: skills_demand_forecast skills_demand_forecast_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_demand_forecast
    ADD CONSTRAINT skills_demand_forecast_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills_taxonomy(id);


--
-- TOC entry 9938 (class 2606 OID 250508)
-- Name: skills_development_plans skills_development_plans_gap_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills_development_plans
    ADD CONSTRAINT skills_development_plans_gap_analysis_id_fkey FOREIGN KEY (gap_analysis_id) REFERENCES public.skills_gap_analysis(id);


--
-- TOC entry 9898 (class 2606 OID 248888)
-- Name: support_response_templates support_response_templates_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.support_response_templates
    ADD CONSTRAINT support_response_templates_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.ticket_categories(id);


--
-- TOC entry 9869 (class 2606 OID 248515)
-- Name: system_flags system_flags_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 9870 (class 2606 OID 248520)
-- Name: system_flags system_flags_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 9871 (class 2606 OID 248525)
-- Name: system_flags system_flags_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_flags
    ADD CONSTRAINT system_flags_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 9916 (class 2606 OID 249900)
-- Name: telematics_data telematics_data_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telematics_data
    ADD CONSTRAINT telematics_data_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.iot_devices(id);


--
-- TOC entry 9897 (class 2606 OID 248869)
-- Name: ticket_requests ticket_requests_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_requests
    ADD CONSTRAINT ticket_requests_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- TOC entry 9909 (class 2606 OID 249127)
-- Name: units units_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- TOC entry 9931 (class 2606 OID 250364)
-- Name: universe_outcomes universe_outcomes_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universe_outcomes
    ADD CONSTRAINT universe_outcomes_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.parallel_scenarios(id);


--
-- TOC entry 9932 (class 2606 OID 250384)
-- Name: universe_recommendations universe_recommendations_recommended_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universe_recommendations
    ADD CONSTRAINT universe_recommendations_recommended_scenario_id_fkey FOREIGN KEY (recommended_scenario_id) REFERENCES public.parallel_scenarios(id);


--
-- TOC entry 9933 (class 2606 OID 250379)
-- Name: universe_recommendations universe_recommendations_universe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universe_recommendations
    ADD CONSTRAINT universe_recommendations_universe_id_fkey FOREIGN KEY (universe_id) REFERENCES public.decision_universes(id);


--
-- TOC entry 9893 (class 2606 OID 248775)
-- Name: user_preferences user_preferences_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- TOC entry 9894 (class 2606 OID 248770)
-- Name: user_preferences user_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 9838 (class 2606 OID 249093)
-- Name: users users_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


-- Completed on 2025-09-03 11:15:53

--
-- PostgreSQL database dump complete
--

