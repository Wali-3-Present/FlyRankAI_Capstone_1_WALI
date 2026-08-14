(function () {
    const scriptTag = document.currentScript;
    const urlParams = new URLSearchParams(scriptTag.src.split('?')[1]);
    const widgetId = urlParams.get('id');

    if (!widgetId) {
        console.error("Widget Error: Missing ID parameter.");
        return;
    }

    const API_BASE = "http://localhost:8000";

    // Fetch Widget Config
    fetch(`${API_BASE}/api/widgets/${widgetId}/config`)
        .then(res => res.json())
        .then(config => {
            renderWidget(config);
        })
        .catch(err => console.error("Widget Loading Failed:", err));

    function renderWidget(config) {
        const container = document.createElement("div");
        container.style.fontFamily = "sans-serif";
        container.style.border = "1px solid #ccc";
        container.style.padding = "16px";
        container.style.borderRadius = "8px";
        container.style.maxWidth = "350px";
        container.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";

        container.innerHTML = `
            <h3>${config.title}</h3>
            <p>${config.description || ''}</p>
            <form id="flyrank-widget-form">
                <input type="text" name="hp_field" style="display:none;" tabindex="-1" autocomplete="off"/>
                <div style="margin-bottom: 8px;">
                    <input type="email" id="fr-email" placeholder="Your Email" required style="width: 100%; padding: 8px;" />
                </div>
                <button type="submit" style="width: 100%; padding: 8px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    ${config.button_text}
                </button>
            </form>
            <div id="fr-msg" style="margin-top: 8px; font-size: 14px;"></div>
        `;

        document.body.appendChild(container);

        document.getElementById("flyrank-widget-form").addEventListener("submit", function (e) {
            e.preventDefault();
            const email = document.getElementById("fr-email").value;
            const hp = e.target.elements.hp_field.value;

            fetch(`${API_BASE}/api/submissions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    widget_id: widgetId,
                    data: { email: email },
                    hp_field: hp
                })
            })
            .then(res => {
                if (res.ok) {
                    document.getElementById("fr-msg").innerText = "Thank you for submitting!";
                    document.getElementById("fr-msg").style.color = "green";
                } else {
                    document.getElementById("fr-msg").innerText = "Submission failed.";
                    document.getElementById("fr-msg").style.color = "red";
                }
            })
            .catch(() => {
                document.getElementById("fr-msg").innerText = "Network error.";
                document.getElementById("fr-msg").style.color = "red";
            });
        });
    }
})();