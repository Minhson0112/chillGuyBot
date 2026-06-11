document.addEventListener("DOMContentLoaded", function () {
    const gameDetailBtn = document.getElementById("gameDetail");
    const gameDialog = document.getElementById("gameDialog");
    const overlay = document.getElementById("overlay");
    const closeDialog = document.getElementById("closeDialog");

    if (gameDetailBtn && gameDialog && overlay && closeDialog) {
        gameDetailBtn.addEventListener("click", function () {
            gameDialog.classList.add("show");
            overlay.classList.add("show");
        });

        closeDialog.addEventListener("click", function () {
            gameDialog.classList.remove("show");
            overlay.classList.remove("show");
        });

        overlay.addEventListener("click", function () {
            gameDialog.classList.remove("show");
            overlay.classList.remove("show");
        });
    } else {
        console.warn("⚠️ Modal luật chơi không khởi tạo được!");
    }

    const isMobile = window.innerWidth < 768;
    if (isMobile) {
        // Ẩn các phần tử không cần thiết
        const hideIds = ["header", "gameRule", "gameNote", "overlay", "gameDialog"];
        hideIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = "none";
        });

        // Căn giữa #gameContainer
        const main = document.getElementById("main");
        if (main) {
            main.style.display = "flex";
            main.style.justifyContent = "center";
            main.style.alignItems = "center";
            main.style.flexDirection = "column";
        }

        // Cho #gameContainer full viewport
        const gameContainer = document.getElementById("gameContainer");
        if (gameContainer) {
            gameContainer.style.width = "100vw";
            gameContainer.style.height = "100vh";
        }

        // Resize các canvas trong gameContainer
        const canvases = gameContainer.querySelectorAll("canvas");
        canvases.forEach(canvas => {
            canvas.style.width = "100%";
            canvas.style.height = "auto";
        });
    }
});