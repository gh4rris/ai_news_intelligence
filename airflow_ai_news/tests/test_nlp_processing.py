from nlp_processing import classify_topics

import pytest


@pytest.mark.parametrize("text, expected", [
    ("Training Data SUPERVISED classification", ["Machine Learning"]),
    ("generative gpt llm claude", ["Generative AI"]),
    ("Robot government sensor ethics embodied ai privacy", ["Robotics", "Ethics & Safety"]),
    ("ecommerce amazon gdp shopping app segmentation computer vision economy tax object detection", ["Politics & Economy", "ecommerce", "Computer Vision"]),
    ("machine learning data centers nlp natural language", ["Other"]),
    ("Training Data SUPERVISEDclassification", ["Other"]),
    ("Something completely irrelivent", ["Other"]),
    ("", ["Other"])
])
def test_classify_topics(text, expected):
    assert classify_topics(text) == expected
