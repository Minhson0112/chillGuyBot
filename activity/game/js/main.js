import $ from "jquery";
import Matter from "matter-js";
import tingle from "tingle.js";
import "tingle.js/dist/tingle.css";

window.$ = $;
window.jQuery = $;
window.Matter = Matter;
window.tingle = tingle;

function loadClassicScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
    });
}

async function bootstrap() {
    await import("./discord-auth.js");
    await loadClassicScript("js/ball-game.js");
    await loadClassicScript("js/common.js");
}

bootstrap();
