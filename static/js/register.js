document.getElementById("registerForm")?.addEventListener("submit", function (e) {
    // e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector(".btn-auth");

    let msgBox = document.getElementById("formMessage");
    if (!msgBox) {
        msgBox = document.createElement("div");
        msgBox.id = "formMessage";
        msgBox.className = "form-message";
        form.prepend(msgBox);
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Sending OTP...";
    msgBox.style.display = "none";

    fetch(form.action || window.location.href, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": form.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(res => res.text())
    .then(data => {

        if (data.toLowerCase().includes("otp")) {
            msgBox.innerText = "OTP sent successfully. Redirecting to verification...";
            msgBox.className = "form-message success";
            msgBox.style.display = "block";

            setTimeout(() => {
                window.location.href = "/verify-otp/";
            }, 1200);

        } else {
            msgBox.innerText = data || "Registration failed";
            msgBox.className = "form-message error";
            msgBox.style.display = "block";

            submitBtn.disabled = false;
            submitBtn.innerText = "Register & Send OTP";
        }
    })
    .catch(() => {
        msgBox.innerText = "Something went wrong. Please try again.";
        msgBox.className = "form-message error";
        msgBox.style.display = "block";

        submitBtn.disabled = false;
        submitBtn.innerText = "Register & Send OTP";
    });
});
