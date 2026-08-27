const analysisForm =
    document.getElementById("analysis-form");

const emotionText =
    document.getElementById("emotion-text");

const analyseButton =
    document.getElementById("analyse-button");

const characterCount =
    document.getElementById("character-count");

const resultCard =
    document.getElementById("result-card");

const emotionResult =
    document.getElementById("emotion-result");

const confidenceResult =
    document.getElementById("confidence-result");

const confidenceBar =
    document.getElementById("confidence-bar");

const supportiveMessage =
    document.getElementById("supportive-message");

const supportiveHeading =
    document.getElementById("supportive-heading");

const supportiveFeedback =
    document.getElementById("supportive-feedback");

const riskNotice =
    document.getElementById("risk-notice");

const riskNoticeTitle =
    document.getElementById("risk-notice-title");

const riskNoticeText =
    document.getElementById("risk-notice-text");

const disclaimerResult =
    document.getElementById("disclaimer-result");

const errorMessage =
    document.getElementById("error-message");

const csrfToken =
    document.querySelector(
        'input[name="csrf_token"]'
    ).value;


const supportiveMessages = {
    Sadness:
        "It sounds like your words carry some sadness. "
        + "Consider giving yourself some space and reaching out "
        + "to someone you trust if that feels helpful.",

    Joy:
        "Your words reflect a positive emotional tone. "
        + "It may be helpful to notice what is contributing "
        + "to this positive feeling.",

    Love:
        "Your words appear to express warmth, care, or affection. "
        + "Positive connections with others can be an important "
        + "part of emotional wellbeing.",

    Anger:
        "Your words appear to carry frustration or anger. "
        + "Taking time before reacting and identifying what is "
        + "driving the feeling may be useful.",

    Fear:
        "Your words appear to express worry or fear. "
        + "Breaking concerns into smaller steps and speaking "
        + "with someone supportive may help.",

    Surprise:
        "Your words appear to express surprise or an unexpected "
        + "emotional response. Giving yourself time to process "
        + "what happened may be helpful."
};


function resetRiskNotice() {
    riskNotice.classList.add("hidden");
    riskNotice.classList.remove(
        "risk-notice-elevated",
        "risk-notice-immediate"
    );

    riskNoticeTitle.textContent = "";
    riskNoticeText.textContent = "";
}


function displayRiskAwareSupport(
    riskSupport
) {
    resetRiskNotice();

    if (
        !riskSupport
        || riskSupport.level === "standard"
    ) {
        supportiveMessage.classList.remove(
            "support-message-muted"
        );

        supportiveHeading.textContent =
            "Supportive reflection";

        return;
    }

    supportiveMessage.classList.add(
        "support-message-muted"
    );

    supportiveHeading.textContent =
        "Emotional reflection";

    riskNotice.classList.remove("hidden");

    if (riskSupport.level === "immediate") {
        riskNotice.classList.add(
            "risk-notice-immediate"
        );
    }
    else {
        riskNotice.classList.add(
            "risk-notice-elevated"
        );
    }

    riskNoticeTitle.textContent =
        riskSupport.title;

    riskNoticeText.textContent =
        riskSupport.message;
}


emotionText.addEventListener(
    "input",
    () => {
        characterCount.textContent =
            `${emotionText.value.length} / 1000`;
    }
);


analysisForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const text =
            emotionText.value.trim();

        resultCard.classList.add("hidden");
        errorMessage.classList.add("hidden");

        resetRiskNotice();

        if (!text) {
            errorMessage.textContent =
                "Please enter some text before analysing.";

            errorMessage.classList.remove("hidden");

            return;
        }

        analyseButton.disabled = true;
        analyseButton.textContent =
            "Analysing...";

        try {
            const response = await fetch(
                "/api/analyse",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                        "X-CSRF-Token":
                            csrfToken
                    },

                    body: JSON.stringify({
                        text: text
                    })
                }
            );

            const data =
                await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error
                    || "Unable to analyse the text."
                );
            }

            const confidencePercentage =
                Math.round(
                    data.confidence * 100
                );

            emotionResult.textContent =
                data.emotion;

            confidenceResult.textContent =
                `${confidencePercentage}%`;

            confidenceBar.style.width =
                `${confidencePercentage}%`;

            supportiveFeedback.textContent =
                supportiveMessages[
                    data.emotion
                ]
                || (
                    "Take a moment to reflect "
                    + "on what you are feeling."
                );

            displayRiskAwareSupport(
                data.risk_support
            );

            disclaimerResult.textContent =
                data.disclaimer;

            resultCard.classList.remove(
                "hidden"
            );
        }
        catch (error) {
            errorMessage.textContent =
                error.message;

            errorMessage.classList.remove(
                "hidden"
            );
        }
        finally {
            analyseButton.disabled = false;

            analyseButton.textContent =
                "Analyse Emotion";
        }
    }
);
