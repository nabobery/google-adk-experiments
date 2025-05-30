# Configuration file for Subreddit-Specific Content Tailoring Agent

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

# Maximum iterations for refinement loop
MAX_ITERATIONS_REFINE = 5

# State Keys
STATE_USER_TOPIC_OR_URL = "user_topic_or_url"
STATE_TARGET_SUBREDDIT = "target_subreddit"
STATE_SUBREDDIT_RULES_AND_TONE = "subreddit_rules_and_tone"
STATE_GOOD_POST_EXAMPLES = "good_post_examples"
STATE_CURRENT_DRAFT = "current_draft"
STATE_FEEDBACK_OR_OK_SIGNAL = "feedback_or_ok_signal"

# Completion Phrases
COMPLETION_PHRASE_QUALITY_CHECK = "POST_OK"
COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE = "SUBREDDIT_INFO_UNAVAILABLE"

# Optional: Predefined subreddit information for common subreddits
PREDEFINED_SUBREDDIT_INFO = {
    "r/python": {
        "rules_and_tone": "Technical programming discussions about Python. Posts should be informative, well-formatted with code blocks, and relate to Python programming. Avoid beginner questions that belong in r/learnpython. Tone is professional and helpful.",
        "good_examples": [
            "Title: New Python 3.12 Feature: PEP 692 - Using TypedDict for kwargs\nBody: The new kwargs syntax in Python 3.12 allows...",
            "Title: Performance comparison: List comprehensions vs Generator expressions\nBody: I benchmarked different approaches for data processing..."
        ]
    },
    "r/MachineLearning": {
        "rules_and_tone": "Research-focused ML discussions. Posts should cite papers, include technical details, and contribute meaningfully to ML discourse. Avoid basic questions. Tone is academic and rigorous.",
        "good_examples": [
            "Title: [R] New SOTA on ImageNet with 0.1% fewer parameters\nBody: Paper: arxiv.org/abs/... Our method achieves...",
            "Title: [D] Why attention mechanisms work better than RNNs for sequence modeling\nBody: After implementing both approaches, I noticed..."
        ]
    },
    "r/webdev": {
        "rules_and_tone": "Web development discussions. Posts should be practical, include code examples or live demos when relevant. Mix of questions, showcases, and discussions. Tone is casual but informative.",
        "good_examples": [
            "Title: Built a CSS Grid generator tool - feedback welcome!\nBody: Live demo: mydemo.com After struggling with grid layouts...",
            "Title: Should I use React or Vue for my next project?\nBody: Currently deciding between frameworks for a medium-sized SaaS..."
        ]
    }
} 