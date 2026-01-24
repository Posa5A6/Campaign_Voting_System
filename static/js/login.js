document.getElementById("loginForm")?.addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(res => res.text())
    .then(data => {
        if (data.toLowerCase().includes("success")) {
            window.location.href = "/campaigns-page/";
        } else {
            document.getElementById("msg").innerText = data;
            document.getElementById("msg").className = "error";
        }
    })
    .catch(err => {
        console.error(err);
    });
});
