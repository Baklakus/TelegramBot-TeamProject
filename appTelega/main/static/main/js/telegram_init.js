document.addEventListener("DOMContentLoaded", function () {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.expand();

        const user = tg.initDataUnsafe.user;
        if (user) {
            fetch("/api/login_telegram/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: user.id,
                    first_name: user.first_name,
                    last_name: user.last_name,
                }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.error) {
                        alert("Ошибка: " + data.error);
                    }
                })
                .catch((err) => {
                    console.error("Ошибка авторизации:", err);
                });
        }
    }
});
