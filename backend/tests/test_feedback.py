# TODO: review
import json


def test_feedback_table_created(test_db):
    with test_db.get_connection() as conn:
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert "feedback" in tables


def test_feedback_schema_columns(test_db):
    with test_db.get_connection() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(feedback)").fetchall()
        }

    assert {
        "session_id",
        "flagged_message",
        "category",
        "comment",
        "created_at",
    }.issubset(columns)


def test_feedback_write(test_db):
    categories = ["Unhelpful", "Inaccurate"]

    test_db.add_feedback(
        session_id="session-001",
        flagged_message="response-123",
        category=json.dumps(categories),
        comment="This response is incorrect.",
    )

    with test_db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM feedback WHERE session_id = ?",
            ("session-001",),
        ).fetchone()

    assert row is not None
    assert row["flagged_message"] == "response-123"
    assert json.loads(row["category"]) == categories
    assert row["comment"] == "This response is incorrect."


def test_feedback_empty_comment(test_db):
    test_db.add_feedback(
        session_id="session-002",
        flagged_message="response-456",
        category=json.dumps(["Unhelpful"]),
        comment="",
    )

    with test_db.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM feedback WHERE session_id = ?",
            ("session-002",),
        ).fetchone()

    assert row is not None
    assert row["comment"] == ""

    def test_delete_history_clears_feedback(test_db):
        session_id = "session-003"

        test_db.add_entry(
            session_id=session_id,
            user_message="Hello",
            system_message="Hi there",
            response_type="normal",
            risk_level="low",
        )

        test_db.add_feedback(
            session_id=session_id,
            flagged_message="response-789",
            category='["Unhelpful"]',
            comment="",
        )

        test_db.delete_history(session_id)

        with test_db.get_connection() as conn:
            history_count = conn.execute(
                "SELECT COUNT(*) FROM history WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

            feedback_count = conn.execute(
                "SELECT COUNT(*) FROM feedback WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

        assert history_count == 0
        assert feedback_count == 0


def test_delete_history_preserves_other_sessions(test_db):
    test_db.add_feedback(
        "session-A", "response-A", '["Unhelpful"]', ""
    )
    test_db.add_feedback(
        "session-B", "response-B", '["Inaccurate"]', ""
    )

    test_db.delete_history("session-A")

    with test_db.get_connection() as conn:
        remaining = conn.execute(
            "SELECT session_id FROM feedback"
        ).fetchall()

    assert [row["session_id"] for row in remaining] == ["session-B"]

    def test_post_feedback_returns_success(client, test_db):
        response = client.post(
            "/api/feedback",
            json={
                "session_id": "session-api-001",
                "message_id": "response-123",
                "category": ["Unhelpful", "Inaccurate"],
                "additional": "The answer was incorrect.",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "success"}

        with test_db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM feedback WHERE session_id = ?",
                ("session-api-001",),
            ).fetchone()

        assert row is not None
        assert row["flagged_message"] == "response-123"
        assert json.loads(row["category"]) == ["Unhelpful", "Inaccurate"]
        assert row["comment"] == "The answer was incorrect."


def test_post_feedback_accepts_empty_comment(client, test_db):
    response = client.post(
        "/api/feedback",
        json={
            "session_id": "session-api-002",
            "message_id": "response-456",
            "category": ["Unhelpful"],
            "additional": "",
        },
    )

    assert response.status_code == 200

    with test_db.get_connection() as conn:
        row = conn.execute(
            "SELECT comment FROM feedback WHERE session_id = ?",
            ("session-api-002",),
        ).fetchone()

    assert row is not None
    assert row["comment"] == ""


def test_post_feedback_accepts_omitted_comment(client, test_db):
    response = client.post(
        "/api/feedback",
        json={
            "session_id": "session-api-003",
            "message_id": "response-789",
            "category": ["Inaccurate"],
        },
    )

    assert response.status_code == 200

    with test_db.get_connection() as conn:
        row = conn.execute(
            "SELECT comment FROM feedback WHERE session_id = ?",
            ("session-api-003",),
        ).fetchone()

    assert row is not None
    assert row["comment"] in ("", None)


def test_post_feedback_rejects_missing_required_fields(client):
    response = client.post(
        "/api/feedback",
        json={
            "session_id": "session-api-004",
        },
    )

    assert response.status_code == 422

    def test_delete_history_clears_feedback(test_db):
        session_id = "session-003"

        test_db.add_entry(
            session_id=session_id,
            user_message="Hello",
            system_message="Hi there",
            response_type="normal",
            risk_level="low",
        )

        test_db.add_feedback(
            session_id=session_id,
            flagged_message="response-789",
            category='["Unhelpful"]',
            comment="",
        )

        test_db.delete_history(session_id)

        with test_db.get_connection() as conn:
            history_count = conn.execute(
                "SELECT COUNT(*) FROM history WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

            feedback_count = conn.execute(
                "SELECT COUNT(*) FROM feedback WHERE session_id = ?",
                (session_id,),
            ).fetchone()[0]

        assert history_count == 0
        assert feedback_count == 0


def test_delete_history_preserves_other_sessions(test_db):
    test_db.add_feedback(
        "session-A", "response-A", '["Unhelpful"]', ""
    )
    test_db.add_feedback(
        "session-B", "response-B", '["Inaccurate"]', ""
    )

    test_db.delete_history("session-A")

    with test_db.get_connection() as conn:
        remaining = conn.execute(
            "SELECT session_id FROM feedback"
        ).fetchall()

    assert [row["session_id"] for row in remaining] == ["session-B"]