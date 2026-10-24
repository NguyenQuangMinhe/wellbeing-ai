import pytest
from unittest.mock import patch

from app.classifier.stage_gate import (
    evaluate_gate,
    STAGE_SEQUENCE,
    detect_decline,
    detect_close,
    detect_topic_change,
    _cosine_similarity,
)


class TestEvaluateGate:
    def test_advances_one_stage_on_long_enough_message(self):
        result = evaluate_gate("Start", "I've been feeling pretty anxious about work lately")
        assert result == "Explore"

    def test_does_not_advance_on_short_message(self):
        result = evaluate_gate("Start", "hi there")
        assert result == "Start"

    def test_stays_at_finish_when_already_at_finish(self):
        result = evaluate_gate("Finish", "This is a long enough message to pass the threshold")
        assert result == "Finish"

    def test_unknown_stage_resets_to_start(self):
        result = evaluate_gate("NotARealStage", "This is a long enough message to pass the threshold")
        assert result == "Start"

    def test_boundary_word_count_four_words_does_not_advance(self):
        result = evaluate_gate("Explore", "one two three four")
        assert result == "Explore"

    def test_boundary_word_count_five_words_advances(self):
        result = evaluate_gate("Explore", "one two three four five")
        assert result == "Reflect"

    @pytest.mark.parametrize("stage", STAGE_SEQUENCE)
    def test_every_defined_stage_is_handled_without_error(self, stage):
        evaluate_gate(stage, "a sufficiently long message to count as evidence")


class TestDetectDecline:
    def test_direct_refusal(self):
        assert detect_decline("I don't want to answer that") is True

    def test_listening_preference(self):
        assert detect_decline("I only want you to listen") is True

    def test_case_insensitive(self):
        assert detect_decline("I'D RATHER NOT") is True

    def test_normal_message_not_flagged(self):
        assert detect_decline("My presentation is on Friday and I'm nervous") is False


class TestDetectClose:
    def test_explicit_stop(self):
        assert detect_close("Let's stop here") is True

    def test_goodbye(self):
        assert detect_close("Thanks, goodbye") is True

    def test_normal_message_not_flagged(self):
        assert detect_close("I've been avoiding checking my email") is False


class TestCosineSimilarity:
    def test_identical_vectors(self):
        assert _cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_zero_vector_returns_zero(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


class TestDetectTopicChange:
    def test_no_previous_message_returns_false(self):
        assert detect_topic_change("Some message", None) is False

    def test_similar_messages_not_flagged(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            mock_embedding.get_text_embedding.side_effect = [[1.0, 0.0], [1.0, 0.0]]
            assert detect_topic_change("current text", "previous text") is False

    def test_dissimilar_messages_flagged(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            mock_embedding.get_text_embedding.side_effect = [[1.0, 0.0], [0.0, 1.0]]
            assert detect_topic_change("current text", "previous text") is True


class TestEvaluateGateConversationalControl:

    def test_decline_does_not_advance(self):
        assert evaluate_gate("Explore", "I don't want to answer that") == "Explore"

    def test_decline_does_not_reset_to_start(self):
        assert evaluate_gate("Reflect", "I'd rather not, thanks") == "Reflect"

    def test_reworded_decline_still_does_not_advance(self):
        assert evaluate_gate("Explore", "I only want you to listen, nothing more") == "Explore"

    def test_close_does_not_advance(self):
        assert evaluate_gate("Finish", "Let's stop here, that's enough for today") == "Finish"

    def test_close_from_early_stage_does_not_advance(self):
        assert evaluate_gate("Start", "I'm done, thank you for listening") == "Start"

    def test_topic_change_resets_to_start(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            mock_embedding.get_text_embedding.side_effect = [[1.0, 0.0], [0.0, 1.0]]
            result = evaluate_gate(
                "Explore",
                "actually I'd rather talk about something completely different",
                "the previous on-topic message",
            )
        assert result == "Start"

    def test_same_topic_continues_to_advance(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            mock_embedding.get_text_embedding.side_effect = [[1.0, 0.0], [1.0, 0.0]]
            result = evaluate_gate(
                "Explore",
                "still the same concern, five plus words here",
                "the previous on-topic message",
            )
        assert result == "Reflect"

    def test_topic_change_check_skipped_at_start(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            result = evaluate_gate("Start", "a brand new concern with enough words", "irrelevant prior text")
        mock_embedding.get_text_embedding.assert_not_called()
        assert result == "Explore"

    def test_topic_change_wins_over_embedded_decline_wording(self):
        with patch("app.classifier.stage_gate.embedding_model") as mock_embedding:
            mock_embedding.get_text_embedding.side_effect = [[1.0, 0.0], [0.0, 1.0]]
            result = evaluate_gate(
                "Explore",
                "I do not want to answer that. I would rather talk about my friend cancelling dinner.",
                "Thinking of Friday makes me nervous because I might go blank.",
            )
        assert result == "Start"