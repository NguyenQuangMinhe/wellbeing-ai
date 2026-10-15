
#provisional stage advancement logic for four stage CBT conversation flow 
#advances one stage when stage has a successor and user message clears 5 word threshold 

STAGE_SEQUENCE = ["Start", "Explore", "Reflect", "Finish"]


def evaluate_gate(current_stage: str, user_message: str) -> str:
    if current_stage not in STAGE_SEQUENCE:
        return "Start"

    current_index = STAGE_SEQUENCE.index(current_stage)
    if current_index == len(STAGE_SEQUENCE) - 1:
        return current_stage  # already at Finish, nothing further to advance to

    word_count = len(user_message.split())
    if word_count < 5:
        return current_stage  # too short to count as real evidence, stay put

    return STAGE_SEQUENCE[current_index + 1]