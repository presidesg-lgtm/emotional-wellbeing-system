# Emotion Label Decision

## Proposed Initial Labels

The initial emotion labels selected for model development are:

- Sadness
- Joy
- Love
- Anger
- Fear
- Surprise

## Rationale

The system will classify expressed emotional language rather than diagnose
mental-health conditions. The selected labels must therefore describe textual
emotional expression and must not be presented as clinical conclusions.

These six categories are supported by the selected DAIR.AI Emotion dataset.
A neutral category has not been included because the dataset does not provide
labelled neutral examples. Adding an unsupported neutral class would create a
mismatch between the application requirements and the data used to train the
model.

## Initial Dataset Decision

The initial model-development dataset selected for evaluation is the DAIR.AI
Emotion dataset. It contains English textual statements labelled using six
emotion categories:

- Sadness
- Joy
- Love
- Anger
- Fear
- Surprise

The dataset was selected because it supports multiclass emotion
classification and is suitable for establishing a baseline model using
TF-IDF and Logistic Regression.

The dataset does not include a neutral class. Therefore, the initial model
will use the six labels supported by the training data rather than creating an
unsupported neutral category.

## Dataset Licensing Note

The publicly hosted dataset card does not currently present sufficiently clear
licensing information. The dataset will initially be used for academic
experimentation while its original source and usage conditions are reviewed.
This uncertainty will be documented and resolved before the final project
submission.

## Ethical Interpretation

The labels describe emotional expression in text. They must not be interpreted
or displayed as clinical diagnoses. For example, the `fear` label indicates
fear-related language and does not establish that the user has an anxiety
disorder.

## Final Decision

Following dataset inspection and quality analysis, the project will use the
following six emotion classes:

- Sadness
- Joy
- Love
- Anger
- Fear
- Surprise

A neutral class will not be included because the selected dataset does not
contain labelled neutral examples.

The six classes will be treated as categories of expressed emotional language
rather than clinical mental-health diagnoses.