(function () {
    const emailEl = document.getElementById("user-email");
    if (!emailEl) {
        return;
    }

    const loadingText = emailEl.dataset.loading || "Loading...";
    const loggedOutText = emailEl.dataset.loggedOut || "Not logged in.";

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return null;
    }

    const token = getCookie("access_token");
    if (!token) {
        emailEl.textContent = loggedOutText;
        return;
    }

    emailEl.textContent = loadingText;

    fetch("/api/auth/me", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Unauthorized");
            }
            return response.json();
        })
        .then((data) => {
            emailEl.textContent = data.email || loggedOutText;
        })
        .catch(() => {
            emailEl.textContent = loggedOutText;
        });
})();
