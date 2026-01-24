document.addEventListener("DOMContentLoaded", function () {
    const campaignList = document.getElementById("campaignList");

    fetch("/campaigns/")
        .then(res => res.json())
        .then(data => {
            if (!data.length) {
                campaignList.innerHTML = "<p>No campaigns available.</p>";
                return;
            }

            let html = "";

            data.forEach(c => {
                const start = new Date(c.start_date).toLocaleDateString();
                const end = new Date(c.end_date).toLocaleDateString();

                html += `
                    <div class="campaign-card">
                        <h3>${c.title}</h3>

                        <p>${c.description}</p>

                        <p class="campaign-dates">
                            ${start} → ${end}
                        </p>

                        <div class="campaign-actions">
                            <a href="/campaign/${c.id}/candidates/" 
                               class="campaign-btn">
                                View Campaign
                            </a>

                        <a href="/results-page/${c.id}/" class="campaign-btn result-btn">
                            Results
                        </a>

                        </div>  
                    </div>
                `;
            });

            campaignList.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            campaignList.innerHTML = "<p>Failed to load campaigns</p>";
        });
});
