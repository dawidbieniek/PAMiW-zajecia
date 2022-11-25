
document.addEventListener("DOMContentLoaded", async function () {
    if (await isLogged()) {
        console.log(await getNumberOfMessages());
        setBadge(await getNumberOfMessages());
    }
});

async function getNumberOfMessages() {
    return await fetch("/api/messageCount", {
        method: "GET",
    })
        .then((response) => response.text())
        .then((text) => {
            return parseInt(text);
        });
}

function setBadge(number) {
    badge = document.getElementById("badge");
    if (number > 0) {
        badge.style.display = "inline";
    }
    else {
        badge.style.display = "none";
    }
    badge.innerText = number;
}

async function isLogged() {
    return await fetch("/api/isLoggedIn", {
        method: "GET",
    }).then((response) => response.text())
        .then((text) => {
            return (text == "True");
        });
}