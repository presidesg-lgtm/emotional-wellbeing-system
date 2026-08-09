# Dataset Documentation

## 1. Dataset Identification

- Dataset name: DAIR.AI Emotion
- Dataset type: Labelled English text
- Intended task: Multiclass emotion classification
- Retrieval method: Hugging Face `datasets` library
- Dataset splits:
  - Training: 16,000 records
  - Validation: 2,000 records
  - Test: 2,000 records
- Emotion classes:
  - Sadness
  - Joy
  - Love
  - Anger
  - Fear
  - Surprise

## 2. Dataset Structure

The dataset contains two original fields:

- `text`: the English-language textual input
- `label`: an integer representing the emotion class

The label mapping used in the project is:

| Label | Emotion |
|---:|---|
| 0 | Sadness |
| 1 | Joy |
| 2 | Love |
| 3 | Anger |
| 4 | Fear |
| 5 | Surprise |

## 3. Initial Data Quality Assessment

The original dataset was evaluated before model training.

The following results were observed:

- Missing text values: 0
- Missing labels: 0
- Empty or whitespace-only text: 0
- Invalid label values: 0
- Exact duplicate training rows: 1
- Exact duplicate validation rows: 0
- Exact duplicate test rows: 0

The dataset also contained duplicated text values with inconsistent emotion
annotations.

Thirty conflicting text values were identified within the training split,
two within the validation split, and no within-test conflicts were found.

A global consistency check across all three dataset splits identified
51 unique text values that were associated with more than one emotion label.

## 4. Cross-Split Consistency

Initial cross-split comparison identified:

- 5 overlapping text values between training and validation
- 11 overlapping text values between training and test
- 3 overlapping text values between validation and test

The inspected overlapping records showed inconsistent emotion labels,
indicating both data leakage and annotation inconsistency.

## 5. Cleaning Method

The following cleaning rules were applied:

1. The original raw dataset files were preserved unchanged.
2. All text values associated with more than one label anywhere in the dataset
   were identified globally.
3. All occurrences of globally conflicting text were removed because there was
   no objective basis for choosing one annotation as correct.
4. Exact duplicate rows were removed.
5. Cross-split overlap was checked again after cleaning.
6. Dataset indices were reset.
7. Final validation checks were performed.

The number of records removed because of conflicting annotations was:

- Training: 76
- Validation: 12
- Test: 14

One additional exact duplicate was removed from the training split.

## 6. Cleaned Dataset Size

| Split | Original Rows | Cleaned Rows | Removed Rows | Removed Percentage |
|---|---:|---:|---:|---:|
| Training | 16,000 | 15,923 | 77 | 0.48% |
| Validation | 2,000 | 1,988 | 12 | 0.60% |
| Test | 2,000 | 1,986 | 14 | 0.70% |

## 7. Post-Cleaning Validation

After cleaning:

- Missing text values: 0
- Missing labels: 0
- Empty text records: 0
- Invalid labels: 0
- Exact duplicate rows: 0
- Conflicting text values: 0
- Training-validation overlap: 0
- Training-test overlap: 0
- Validation-test overlap: 0

This confirms that the cleaned dataset provides separated training,
validation, and test partitions.

## 8. Class Distribution

The cleaned training split contains:

| Emotion | Records |
|---|---:|
| Sadness | 4,661 |
| Joy | 5,340 |
| Love | 1,283 |
| Anger | 2,152 |
| Fear | 1,923 |
| Surprise | 564 |

The dataset is imbalanced. Joy and sadness have substantially more examples
than surprise and love.

Therefore, model evaluation will not rely on accuracy alone. Precision,
recall, macro F1-score, weighted F1-score, per-class metrics, and confusion
matrices will also be used.

## 9. Text-Length Characteristics

The training data has a median length of approximately 17 words and a mean
length of approximately 19 words.

Approximately:

- 95% of training records contain 41 words or fewer
- 99% contain 52 words or fewer
- the longest observed record contains 66 words

Very short entries were retained because text length alone does not provide a
sufficiently objective reason for removal.

## 10. Ethical and Interpretive Considerations

The dataset labels describe expressed emotional language and must not be
treated as clinical diagnoses.

The presence of annotation conflicts in the original dataset demonstrates
that emotional interpretation can be subjective.

Potential limitations include:

- ambiguous emotional expressions
- incomplete context
- informal language
- cultural differences
- annotation subjectivity
- class imbalance

These limitations will be considered when interpreting model performance.

## 11. Suitability Decision

Following data-quality analysis and cleaning, the dataset is considered
suitable for baseline multiclass emotion-classification experiments.

The final model will classify emotional expression into the six supported
categories and will not be presented as a medical or psychological diagnostic
system.