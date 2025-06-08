from flask import current_app
from sqlalchemy import text

#좋아요 자동 증감 트리거
def register_triggers(db):
    try:
        trigger_sql = """
        DROP TRIGGER IF EXISTS trg_increment_like ON "PostLike";
        DROP FUNCTION IF EXISTS increment_post_like_count();

        DROP TRIGGER IF EXISTS trg_decrement_like ON "PostLike";
        DROP FUNCTION IF EXISTS decrement_post_like_count();

        CREATE OR REPLACE FUNCTION increment_post_like_count()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE "Post"
            SET like_count = like_count + 1
            WHERE post_id = NEW.post_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_increment_like
        AFTER INSERT ON "PostLike"
        FOR EACH ROW
        EXECUTE FUNCTION increment_post_like_count();

        CREATE OR REPLACE FUNCTION decrement_post_like_count()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE "Post"
            SET like_count = like_count - 1
            WHERE post_id = OLD.post_id;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_decrement_like
        AFTER DELETE ON "PostLike"
        FOR EACH ROW
        EXECUTE FUNCTION decrement_post_like_count();
        """

        with db.engine.begin() as conn:
            conn.execute(text(trigger_sql))

        current_app.logger.info("✔️ Triggers registered successfully.")

    except Exception as e:
        current_app.logger.error(f"Error registering triggers: {e}")
