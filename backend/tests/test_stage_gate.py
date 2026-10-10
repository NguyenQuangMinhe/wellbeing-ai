import pytest
from app.classifier.stage_gate import evaluate_gate, STAGE_SEQUENCE


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
        # just confirms no exception for any real stage, advance or not
        evaluate_gate(stage, "a sufficiently long message to count as evidence")