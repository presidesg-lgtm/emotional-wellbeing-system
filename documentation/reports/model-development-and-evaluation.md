# Model Development and Evaluation

## 1. Purpose

This document records the machine-learning model development and evaluation process for the Emotional Wellbeing Analysis System.

The project uses text classification to identify six categories of expressed emotion:

1. Sadness
2. Joy
3. Love
4. Anger
5. Fear
6. Surprise

These predictions represent patterns of emotional expression in text and are not intended to provide clinical or psychological diagnoses.

---

## 2. Dataset

The project uses the DAIR.AI Emotion dataset obtained through Hugging Face Datasets.

The original dataset contained:

- Training: 16,000 records
- Validation: 2,000 records
- Test: 2,000 records

Dataset quality analysis identified duplicate text, conflicting labels, and cross-split overlap.

All text examples that contained conflicting labels across the dataset were removed, along with exact duplicate records.

The final cleaned datasets contained:

- Training: 15,923 records
- Validation: 1,988 records
- Test: 1,986 records

The final datasets contained no missing text, empty text, invalid labels, exact duplicates, conflicting labels, or cross-split overlap.

---

## 3. Classical Baseline Model

### 3.1 Feature Extraction

The classical baseline uses Term Frequency-Inverse Document Frequency (TF-IDF) to convert text into numerical feature vectors.

The TF-IDF configuration used:

- Lower-case conversion
- English stop-word removal
- Maximum 20,000 features
- Unigrams and bigrams

The TF-IDF vectorizer was fitted only on the training dataset.

The validation and test datasets were transformed using the vocabulary and IDF values learned from the training dataset to avoid data leakage.

### 3.2 Standard Logistic Regression

The first baseline model used Logistic Regression with:

- Maximum iterations: 1,000
- Random state: 42
- No class weighting

Validation performance:

- Accuracy: 0.8934
- Macro Precision: 0.8992
- Macro Recall: 0.8253
- Macro F1-score: 0.8569
- Weighted F1-score: 0.8910

The model performed strongly on Sadness and Joy but showed lower recall for Love, Fear, and Surprise.

This was consistent with the class imbalance identified during dataset analysis.

### 3.3 Class-Weighted Logistic Regression

A second Logistic Regression model was trained using:

`class_weight="balanced"`

Validation performance:

- Accuracy: 0.9024
- Macro Precision: 0.8595
- Macro Recall: 0.9047
- Macro F1-score: 0.8788
- Weighted F1-score: 0.9035

Class weighting substantially improved recall for minority classes.

Examples include:

- Love recall: 0.7514 to 0.9653
- Fear recall: 0.7583 to 0.8341
- Surprise recall: 0.6750 to 0.9000

The increased recall was accompanied by reduced precision for some minority classes, particularly Love and Surprise.

Based on validation performance, the class-weighted Logistic Regression model was selected as the preferred classical baseline.

---

## 4. Transformer Model

### 4.1 Model Selection

The advanced model uses DistilBERT:

`distilbert-base-uncased`

DistilBERT was selected because it provides contextual transformer-based language representations while requiring fewer computational resources than full BERT.

This was particularly important because the available development GPU was an NVIDIA GeForce GTX 1650 Ti with approximately 4 GB of GPU memory.

### 4.2 Tokenization

The DistilBERT tokenizer was used with:

- Maximum sequence length: 64 tokens
- Truncation enabled
- Padding to maximum length

The sequence length was selected based on the earlier dataset text-length analysis and the available GPU memory.

### 4.3 Training Configuration

The transformer model was fine-tuned for six-class emotion classification.

Training settings included:

- Epochs: 3
- Per-device training batch size: 2
- Per-device evaluation batch size: 4
- Gradient accumulation steps: 8
- Effective training batch size: 16
- Learning rate: 2e-5
- Weight decay: 0.01
- Mixed-precision training (FP16)
- Random seed: 42

Validation evaluation was performed at the end of each epoch.

Macro F1-score was used as the checkpoint-selection metric because the dataset is imbalanced.

---

## 5. Transformer Validation Results

During the original development run, the best DistilBERT checkpoint was selected at Epoch 2.

Original best validation performance:

- Accuracy: 0.9427
- Macro Precision: 0.9290
- Macro Recall: 0.9050
- Macro F1-score: 0.9158
- Weighted Precision: 0.9423
- Weighted Recall: 0.9427
- Weighted F1-score: 0.9420

Per-class F1-scores:

- Sadness: 0.9638
- Joy: 0.9624
- Love: 0.8875
- Anger: 0.9485
- Fear: 0.8926
- Surprise: 0.8400

The transformer model substantially outperformed the preferred class-weighted Logistic Regression baseline on accuracy, macro precision, macro F1-score, and weighted F1-score.

---

## 6. Reproducibility Rerun

During preparation for final test evaluation, the training notebook was unintentionally rerun.

The same dataset, preprocessing configuration, model architecture, training configuration, random seed, validation split, and model-selection criterion were used.

The rerun again selected Epoch 2 as the best checkpoint according to macro F1-score.

Rerun best validation performance:

- Accuracy: 0.9442
- Macro Precision: 0.9344
- Macro Recall: 0.9031
- Macro F1-score: 0.9164
- Weighted F1-score: 0.9434

These values are very close to the original development run and demonstrate that the model-development process produced highly similar results when repeated.

The original Stage 5 validation evidence remains preserved in the project documentation and Git history.

The locally saved selected model used for final testing corresponds to the reproducibility rerun.

---

## 7. Final Test Evaluation

The cleaned test dataset contained 1,986 records.

The test dataset was not used during training, validation-stage model selection, or baseline-versus-transformer comparison.

The selected DistilBERT model was evaluated on the test dataset only after model development and selection had been completed.

Final test performance:

- Accuracy: 0.9275
- Macro Precision: 0.9024
- Macro Recall: 0.8605
- Macro F1-score: 0.8770
- Weighted Precision: 0.9269
- Weighted Recall: 0.9275
- Weighted F1-score: 0.9260

Per-class results:

| Emotion | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Sadness | 0.9720 | 0.9585 | 0.9652 | 579 |
| Joy | 0.9335 | 0.9593 | 0.9462 | 688 |
| Love | 0.8403 | 0.7756 | 0.8067 | 156 |
| Anger | 0.8919 | 0.9635 | 0.9263 | 274 |
| Fear | 0.9103 | 0.9062 | 0.9083 | 224 |
| Surprise | 0.8667 | 0.6000 | 0.7091 | 65 |

---

## 8. Final Error Analysis

The final test confusion matrix identified several important error patterns.

The largest confusion occurred between Love and Joy:

- 33 Love records were predicted as Joy.
- 22 Joy records were predicted as Love.

Surprise remained the most difficult class:

- 17 Surprise records were predicted as Fear.
- 6 Surprise records were predicted as Joy.

Other notable errors included:

- 17 Sadness records predicted as Anger.
- 10 Fear records predicted as Anger.
- 7 Fear records predicted as Sadness.

These results suggest that emotional categories with overlapping semantic context remain difficult to distinguish perfectly.

The lower performance of Surprise and Love also reflects their smaller representation in the dataset.

---

## 9. Final Model Selection

DistilBERT is selected as the machine-learning model for integration into the Emotional Wellbeing Analysis System.

The decision is based on its stronger validation performance compared with the classical TF-IDF and Logistic Regression baseline and its strong final performance on the untouched test dataset.

The final test accuracy of 0.9275 and weighted F1-score of 0.9260 demonstrate strong overall classification performance.

However, the macro F1-score of 0.8770 and lower performance for minority classes demonstrate that the model should not be considered equally reliable for every emotion category.

The model output will therefore be presented as an estimate of expressed emotional language rather than as a clinical diagnosis.

---

## 10. Limitations

The following limitations were identified:

1. The dataset is class-imbalanced, particularly for Surprise and Love.
2. Some emotion classes contain semantically overlapping language.
3. The model is trained using a single public English-language dataset.
4. Performance may differ for text from populations or contexts not represented in the training data.
5. Emotion classification does not represent clinical assessment or diagnosis.
6. The final test results show weaker generalisation for minority classes compared with larger classes.
7. Transformer training required GPU acceleration and additional computational resources compared with the classical baseline.

---

## 11. Integration Decision

The selected DistilBERT model and tokenizer are stored locally under:

`ml/saved_models/selected-distilbert-emotion`

The model will be integrated into the Flask backend through a dedicated machine-learning service layer.

The web application will provide users with:

- An estimated emotion label
- Model prediction confidence
- Supportive, non-diagnostic feedback
- Appropriate wellbeing disclaimers

The system will not present model predictions as medical or psychological diagnoses.