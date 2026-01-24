document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("results");
    const campaignId = container.dataset.campaignId;

    fetch(`/results/${campaignId}/`, { credentials: "same-origin" })
        .then(async res => {
            const data = await res.json();
            return { status: res.status, data };
        })
        .then(({ status, data }) => {
            container.innerHTML = "";

            // 🔒 Campaign not ended
            if (status === 403) {
                container.innerHTML = `
                    <div class="results-locked">
                        🔒 ${data.message}
                    </div>
                `;
                return;
            }

            if (status !== 200 || !data.length) {
                container.innerHTML = `<p>No results available</p>`;
                return;
            }

            // 📊 Find max votes
            const maxVotes = Math.max(...data.map(c => c.total_votes));

            // 🧮 Sort descending
            data.sort((a, b) => b.total_votes - a.total_votes);

            data.forEach((c, index) => {
                const percent = maxVotes === 0
                    ? 0
                    : Math.round((c.total_votes / maxVotes) * 100);

                // 🧮 Tie logic
                const isWinner = c.total_votes === maxVotes && maxVotes > 0;

                // 🥇 Ranking
                let rankClass = "normal";
                let medal = "";

                if (index === 0) { rankClass = "gold"; medal = "🥇"; }
                else if (index === 1) { rankClass = "silver"; medal = "🥈"; }
                else if (index === 2) { rankClass = "bronze"; medal = "🥉"; }

                if (isWinner && index > 0 && c.total_votes === data[0].total_votes) {
                    medal = "🏆";
                    rankClass = "winner";
                }

                const card = document.createElement("div");
                card.className = `result-card ${rankClass}`;

                card.innerHTML = `
                    <div class="result-header">
                        <span class="candidate-name">
                            ${medal} ${c.name} (${c.party})
                        </span>
                        <span class="vote-count">
                            ${c.total_votes} votes
                        </span>
                    </div>

                    <div class="vote-bar">
                        <div class="vote-fill"
                             style="width: ${percent}%">
                        </div>
                    </div>
                `;

                container.appendChild(card);
            });
        })
        .catch(() => {
            container.innerHTML =
                `<p class="error">Failed to load results</p>`;
        });
});
