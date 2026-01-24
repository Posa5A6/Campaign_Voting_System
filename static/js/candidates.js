const container = document.getElementById("candidateList");
const campaignId = container.dataset.campaignId;

fetch(`/candidates/${campaignId}/`)
    .then(res => res.json())
    .then(data => {
        container.innerHTML = "";

        if (data.error) {
            container.innerHTML = `<p>${data.error}</p>`;
            return;
        }

        const hasVoted = data.has_voted;
        const votedCandidateId = data.voted_candidate_id;

        data.candidates.forEach(c => {
            const div = document.createElement("div");
            div.className = "candidate";

            let buttonText = "Vote";
            let disabled = "";

            if (hasVoted) {
                disabled = "disabled";
                if (c.id === votedCandidateId) {
                    buttonText = "✔ Voted";
                }
            }

            div.innerHTML = `
                <span>${c.name} (${c.party})</span>
                <button ${disabled} onclick="vote(${c.id})">
                    ${buttonText}
                </button>
            `;

            container.appendChild(div);
        });
    })
    .catch(() => {
        container.innerHTML = "<p>Error loading candidates</p>";
    });

function vote(candidateId) {
    fetch(`/vote/${campaignId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "same-origin",
        body: `candidate_id=${candidateId}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            location.reload(); // 🔥 reload → disables all buttons
        } else {
            alert(data.error);
        }
    })
    .catch(() => {
        alert("Network error");
    });
}

function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
