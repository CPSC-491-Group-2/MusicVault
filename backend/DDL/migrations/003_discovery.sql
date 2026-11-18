
-- ============================================================
-- MUSICVAULT DATABASE MIGRATION
-- 003_discovery.sql
--
-- Purpose:
-- Add the discovery engine: provider IDs and similarity edges
-- for artists, Deezer preview playback on songs, the crawler
-- job queue, and swipe-deck events.
--
-- artists.mbid and songs.deezer_track_id are made unique with
-- CREATE UNIQUE INDEX IF NOT EXISTS, not ADD CONSTRAINT, because
-- PostgreSQL has no ADD CONSTRAINT IF NOT EXISTS and this file
-- must stay re-runnable.
-- ============================================================

BEGIN;

-- ============================================================
-- 1. ARTIST DISCOVERY METADATA
-- ============================================================

ALTER TABLE artists
ADD COLUMN IF NOT EXISTS mbid VARCHAR(36);

ALTER TABLE artists
ADD COLUMN IF NOT EXISTS fans INTEGER;

ALTER TABLE artists
ADD COLUMN IF NOT EXISTS fans_source VARCHAR(100);

ALTER TABLE artists
ADD COLUMN IF NOT EXISTS last_expanded_at TIMESTAMPTZ;

-- ============================================================
-- 2. SONG PREVIEW PLAYBACK
-- ============================================================

ALTER TABLE songs
ADD COLUMN IF NOT EXISTS deezer_track_id VARCHAR(255);

ALTER TABLE songs
ADD COLUMN IF NOT EXISTS preview_url TEXT;

-- ============================================================
-- 3. ARTIST EXTERNAL IDS
-- ============================================================

CREATE TABLE IF NOT EXISTS artist_external_ids (
    artist_id UUID NOT NULL
        REFERENCES artists(id)
        ON DELETE CASCADE,

    provider VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,

    PRIMARY KEY (artist_id, provider),

    CONSTRAINT uq_artist_external_ids_provider_external
        UNIQUE (provider, external_id)
);

-- ============================================================
-- 4. ARTIST EDGES
-- ============================================================

CREATE TABLE IF NOT EXISTS artist_edges (
    src_artist_id UUID NOT NULL
        REFERENCES artists(id)
        ON DELETE CASCADE,

    dst_artist_id UUID NOT NULL
        REFERENCES artists(id)
        ON DELETE CASCADE,

    provider VARCHAR(50) NOT NULL,
    weight DOUBLE PRECISION NOT NULL,

    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (src_artist_id, dst_artist_id, provider),

    CONSTRAINT chk_artist_edges_weight_range
        CHECK (weight >= 0 AND weight <= 1),

    CONSTRAINT chk_artist_edges_no_self
        CHECK (src_artist_id <> dst_artist_id),

    CONSTRAINT chk_artist_edges_provider
        CHECK (
            provider IN (
                'deezer_related',
                'lastfm_similar',
                'mb_relation',
                'co_credit'
            )
        )
);

-- ============================================================
-- 5. ARTIST TAGS
-- ============================================================

CREATE TABLE IF NOT EXISTS artist_tags (
    artist_id UUID NOT NULL
        REFERENCES artists(id)
        ON DELETE CASCADE,

    tag VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,

    weight DOUBLE PRECISION,

    PRIMARY KEY (artist_id, tag, provider)
);

-- ============================================================
-- 6. CRAWL JOBS
-- ============================================================

CREATE TABLE IF NOT EXISTS crawl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    kind VARCHAR(50) NOT NULL,
    lane VARCHAR(50) NOT NULL,
    target VARCHAR(255) NOT NULL,

    payload JSONB,

    priority INTEGER NOT NULL DEFAULT 50,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    attempts INTEGER NOT NULL DEFAULT 0,

    run_after TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_error TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_crawl_jobs_kind_target
        UNIQUE (kind, target),

    CONSTRAINT chk_crawl_jobs_status
        CHECK (
            status IN (
                'queued',
                'running',
                'done',
                'failed'
            )
        )
);

-- ============================================================
-- 7. SWIPE EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS swipe_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    song_id UUID NOT NULL
        REFERENCES songs(id)
        ON DELETE CASCADE,

    action VARCHAR(20) NOT NULL,
    deck_position INTEGER,
    algorithm_version VARCHAR(100),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_swipe_events_action
        CHECK (
            action IN (
                'keep',
                'pass',
                'skip'
            )
        )
);

-- ============================================================
-- 8. INDEXES
-- ============================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_artists_mbid
    ON artists(mbid);

CREATE UNIQUE INDEX IF NOT EXISTS uq_songs_deezer_track_id
    ON songs(deezer_track_id);

CREATE INDEX IF NOT EXISTS idx_artist_edges_src_artist_id
    ON artist_edges(src_artist_id);

CREATE INDEX IF NOT EXISTS idx_artist_edges_dst_artist_id
    ON artist_edges(dst_artist_id);

CREATE INDEX IF NOT EXISTS idx_artist_external_ids_artist_id
    ON artist_external_ids(artist_id);

CREATE INDEX IF NOT EXISTS idx_crawl_jobs_claim
    ON crawl_jobs(lane, status, priority DESC, run_after);

CREATE INDEX IF NOT EXISTS idx_swipe_events_user_id
    ON swipe_events(user_id);

CREATE INDEX IF NOT EXISTS idx_swipe_events_song_id
    ON swipe_events(song_id);

COMMIT;
