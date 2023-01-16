
document.addEventListener("DOMContentLoaded", async function () {
    await initSpecialNavbarButtons();

    if (await isLogged()) {
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

async function isAdmin() {
    return await fetch("/api/isAdmin", {
        method: "GET"
    }).then((response) => response.text())
        .then((text) => {
            return (text == "True")
        });
}

async function initSpecialNavbarButtons() {
    if (await isAdmin()) {
        const parent = document.getElementById("navbarList")

        let newElement = document.createElement("li");
        newElement.innerHTML = "<a href='/userList'>Lista użytkowników</a>";
        const refNode = parent.childNodes[5];
        console.log(parent.childNodes);

        parent.insertBefore(newElement, refNode);
    }
}