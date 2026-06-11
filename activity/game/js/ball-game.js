/**
 * Get the core Matter.js modules
 */
const { Engine, Render, Runner, World, Body, Bodies, Composite, Mouse, Events } =
    Matter;

/**
 * Constants
 */

// Gravity acceleration
const GRAVITY = 2;

// Game area width and height in pixels
const GAME_AREA_WIDTH = 430;
const GAME_AREA_HEIGHT = 720;

// Colors used by the game
const COLOR = {
    red: "#FF0000"
};

// Ball type definitions
const BALL_TYPES = [
    { name: "stone", size: 15, color: "rgb(233,52,97)", texture: "assets/ballTexture/stone.png" },
    { name: "moon", size: 24, color: "rgb(233,52,97)", texture: "assets/ballTexture/moon.png"},
    { name: "mercury", size: 32, color: "rgb(224,119,249)", texture: "assets/ballTexture/mercury.png" },
    { name: "mars", size: 35, color: "rgb(255,166,57)", texture: "assets/ballTexture/mars.png" },
    { name: "venus", size: 44, color: "rgb(229,139,85)", texture: "assets/ballTexture/venus.png" },
    { name: "earth", size: 55, color: "rgb(255,124,126)", texture: "assets/ballTexture/earth.png" },
    { name: "neptune", size: 56, color: "rgb(255, 255, 124)", texture: "assets/ballTexture/neptune.png" },
    { name: "uranus", size: 77, color: "rgb(239,126,231)", texture: "assets/ballTexture/uranus.png" },
    { name: "saturn", size: 90, color: "rgb(252,243,14)", texture: "assets/ballTexture/saturn.png" },
    { name: "jupiter", size: 124, color: "rgb(213,255,56)", texture: "assets/ballTexture/jupiter.png" },
    { name: "sun", size: 129, color: "rgb(114,207,0)", texture: "assets/ballTexture/sun.png" },
    { name: "blackhole", size: 90, color: "rgb(0, 0, 0)", texture: "assets/ballTexture/blackhole.png" },
];

// Ball preview display size
const DISPLAY_BALL_SIZE = "20px";

// Ball density, which affects mass
const DENSITY = 0.001;

// Air friction; higher values make falling slower
const FRICTION_AIR = 0.03;

// Restitution; values closer to 0 bounce less
const RESTITUTION = 0.4;

// Surface friction against the floor and walls
const FRICTION = 0.1;

// Collision slop tolerance; smaller values are more precise
const SLOP = 0.3;

// General collision and timing interval
const INTERVAL_TIME = 1000;

// Animation frame update interval
const ANIMATION_TIMEOUT = 16;

// Velocity threshold for stillness checks
const STILLNESS_VELOCITY = 0.1;

// Wall positions and dimensions
const WALL_X = {
    left: -9,
    right: 439,
};

// Wall center Y coordinate
const WALL_Y = 370;

// Wall height
const WALL_HEIGHT = 740;

// Wall thickness
const THICKNESS = 20;

// Floor X coordinate
const FLOOR_X = 215;

// Floor Y coordinate
const FLOOR_Y = 729;

// Floor width
const FLOOR_WIDTH = 430;

// Ceiling Y coordinate
const CELLING_Y = -9;

// Game-over line Y coordinate
const GAME_OVER_LINE_Y = 110;

// Sensor line Y coordinate
const SENS_LINE_Y = 160;

// Sensor line thickness
const LINE_THICKNESS = 1;

// Score table
const SCORE_TABLE = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55];

// Ball spawn rate table
const SPAWN_RATE = [
    0, 0, 0, 0, 0,  // stone 30%
    1, 1, 1, 1,     // moon 25%
    2, 2, 2,        // mercury 20%
    3, 3,           // mars 15%
    4               // venus 10%
];

// Ball texture sizes
const TEXTURESIZE = {};

/**
 * State variables
 */

// All balls currently in the game
let balls = [];

// The ball currently controlled by the player
let currentBall = null;

// Interval ID for blinking the game-over line
let blinkInterval;

// Player score
let score = 0;

let sunCreateTime = null;
let gameStartTime = null;
let mergeGamePlayHistoryId = null;
let gameProgressSaveInterval = null;
let isSavingGameProgress = false;
let gameProgressSavePromise = null;

// Tracks whether the game-over alert has already been shown
let alertFlag = false;

// Total number of balls spawned in this game
let ballCount = 0;

// Index of the next ball to spawn in BALL_TYPES
let nextBallIndex = 0;

// Whether the current ball can be moved
let canMoveBall = true;

// Game-over state
let gameOver = false;

// Effect canvas element
let $effectCanvas = $("#effectCanvas");

// Canvas drawing context
let effectCtx = $effectCanvas[0].getContext("2d");

// Match the effect canvas size to the game area
$effectCanvas.attr({ width: GAME_AREA_WIDTH, height: GAME_AREA_HEIGHT });

/**
 * Preload ball texture assets
 */
const preloadTextures = (() => {
    return new Promise((resolve) => {
        let loadedImages = 0;
        const textures = BALL_TYPES.map(ball => ball.texture);

        textures.forEach(texture => {
            let img = new Image();
            img.src = texture;
            img.onload = function() {
                TEXTURESIZE[texture] = { width: img.width, height: img.height };
                loadedImages++;
                if (loadedImages === textures.length) {
                    resolve();
                }
            };
            img.onerror = function() {
                console.error("load error:", texture);
                loadedImages++;
                if (loadedImages === textures.length) {
                    resolve();
                }
            };
        });

        if (textures.length === 0) {
            resolve();
        }
    });
})();

function getDiscordIdFromAuth() {
    return window.chillGuyDiscordAuth?.user?.id || null;
}
function getDiscordUserNameFromAuth() {
    const user = window.chillGuyDiscordAuth?.user;
    return user?.global_name || user?.username || null;
}
function getDiscordGuildIdFromAuth() {
    return window.chillGuyDiscordAuth?.guildId || null;
}

function getGameProgressRequestHeaders() {
    let accessToken = window.chillGuyDiscordAuth?.accessToken;

    if (!accessToken) {
        return null;
    }

    return {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
    };
}

function buildGameProgressPayload() {
    let payload = {
        score: score,
        sun_time: sunCreateTime,
    };

    if (mergeGamePlayHistoryId !== null) {
        payload.id = mergeGamePlayHistoryId;
    }

    return payload;
}

function saveGameProgress(force = false) {
    let requestHeaders = getGameProgressRequestHeaders();

    if (requestHeaders === null) {
        return Promise.resolve(null);
    }

    if (isSavingGameProgress) {
        if (!force) {
            return gameProgressSavePromise || Promise.resolve(null);
        }

        return (gameProgressSavePromise || Promise.resolve(null)).then(() => saveGameProgress(false));
    }

    isSavingGameProgress = true;

    gameProgressSavePromise = fetch("/api/game-progress", {
        method: "POST",
        headers: requestHeaders,
        body: JSON.stringify(buildGameProgressPayload()),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Game progress save failed: " + response.status);
        }

        return response.json();
    })
    .then(data => {
        if (data && data.id) {
            mergeGamePlayHistoryId = data.id;
        }

        return data;
    })
    .catch(error => {
        console.error("Error saving game progress:", error);
        return null;
    })
    .finally(() => {
        isSavingGameProgress = false;
        gameProgressSavePromise = null;
    });

    return gameProgressSavePromise;
}

function startGameProgressAutoSave() {
    if (gameProgressSaveInterval !== null) {
        return;
    }

    gameProgressSaveInterval = setInterval(() => {
        if (!gameOver) {
            saveGameProgress();
        }
    }, 20000);
}

function stopGameProgressAutoSave() {
    if (gameProgressSaveInterval === null) {
        return;
    }

    clearInterval(gameProgressSaveInterval);
    gameProgressSaveInterval = null;
}

/**
 * Initialize the engine and world
 */
let engine, world;
try {
    engine = Engine.create();
    world = engine.world;
    engine.world.gravity.y = GRAVITY;
} catch (error) {
    console.error("Error initializing Matter.js Engine and World:", error);
}

/**
 * Initialize DOM elements and renderer
 */
let gameArea, render, ctx;
try {
    gameArea = document.getElementById("gameArea");
    if (!gameArea) {
        throw new Error("gameArea element not found");
    }
    render = Render.create({
        canvas: gameArea,
        engine: engine,
        options: {
            width: GAME_AREA_WIDTH,
            height: GAME_AREA_HEIGHT,
            wireframes: false,
            background: "assets/ballTexture/background.png",
        },
    });
    ctx = gameArea.getContext("2d");
} catch (error) {
    console.error("Error initializing DOM elements and Render:", error);
}

/**
 * Container for game objects
 */
const gameWorld = World.create();
World.add(engine.world, gameWorld);

/**
 * Create static objects: walls, floor, ceiling, game-over line, and sensor line
 */
try {
    World.add(engine.world, [
        Bodies.rectangle(WALL_X.left, WALL_Y, THICKNESS, WALL_HEIGHT, {
            isStatic: true,
            render: { visible: false },
        }),
        Bodies.rectangle(WALL_X.right, WALL_Y, THICKNESS, WALL_HEIGHT, {
            isStatic: true,
            render: { visible: false },
        }),
        Bodies.rectangle(FLOOR_X, FLOOR_Y, FLOOR_WIDTH, THICKNESS, {
            isStatic: true,
            render: { visible: false },
        }),
        Bodies.rectangle(FLOOR_X, CELLING_Y, FLOOR_WIDTH, THICKNESS, {
            isStatic: true,
            render: { visible: false },
        }),
    ]);

    var gameOverLine = Bodies.rectangle(
        GAME_AREA_WIDTH / 2,
        GAME_OVER_LINE_Y,
        GAME_AREA_WIDTH,
        LINE_THICKNESS,
        {
            isStatic: true,
            isSensor: true,
            label: "limit",
            render: { visible: false },
        },
    );
    var sensLine = Bodies.rectangle(
        GAME_AREA_WIDTH / 2,
        SENS_LINE_Y,
        GAME_AREA_WIDTH,
        LINE_THICKNESS,
        {
            isStatic: true,
            isSensor: true,
            label: "sens",
            render: { visible: false },
        },
    );
    World.add(engine.world, [gameOverLine, sensLine]);
} catch (error) {
    console.error("Error creating static game objects:", error);
}

/**
 * Function definitions
 */

/**
 * Update the next-ball preview
 *
 * @function updateNextDisplay
 */
const updateNextDisplay = () => {
    try {
        $("#nextBall").css({
            width: DISPLAY_BALL_SIZE,
            height: DISPLAY_BALL_SIZE,
            backgroundImage: `url(${BALL_TYPES[nextBallIndex].texture})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
        });
    } catch (error) {
        console.error("Error in updateNextDisplay:", error);
    }
};

/**
 * Create a movable ball of the given type
 *
 * @function createMovingBall
 * @param {number} typeIndex Index in the BALL_TYPES array
 */
function createMovingBall(typeIndex) {
    try {
        const ballType = BALL_TYPES[typeIndex];
        if (!ballType) {
            throw new Error("Invalid ball type index: " + typeIndex);
        }
        let scaleX = (2 * ballType.size) / TEXTURESIZE[ballType.texture].width;
        let scaleY = (2 * ballType.size) / TEXTURESIZE[ballType.texture].height;
        currentBall = Bodies.circle(gameArea.width / 2, 50, ballType.size, {
            density: DENSITY,
            frictionAir: FRICTION_AIR,
            restitution: RESTITUTION,
            friction: FRICTION,
            slop: SLOP,
            render: {
                fillStyle: ballType.color,
                sprite: {
                    texture: ballType.texture,
                    xScale: scaleX,
                    yScale: scaleY
                },
            },
            isStatic: true,
            label: `ball_${ballType.name}`,
        });
        World.add(engine.world, currentBall);
    } catch (error) {
        console.error("Error in createMovingBall:", error);
    }
}

/**
 * Start blinking the game-over line
 *
 * @function startBlinking
 */
function startBlinking() {
    try {
        if (!blinkInterval) {
            blinkInterval = setInterval(() => {
                try {
                    gameOverLine.render.visible = !gameOverLine.render.visible;
                    if (gameOverLine.render.visible) {
                        gameOverLine.render.fillStyle = COLOR.red;
                    }
                } catch (error) {
                    console.error("Error in blink interval callback:", error);
                }
            }, INTERVAL_TIME / 2);
        }
    } catch (error) {
        console.error("Error in startBlinking:", error);
    }
}

/**
 * Stop blinking the game-over line
 *
 * @function stopBlinking
 */
function stopBlinking() {
    try {
        if (blinkInterval) {
            clearInterval(blinkInterval);
            blinkInterval = null;
            gameOverLine.render.visible = false;
        }
    } catch (error) {
        console.error("Error in stopBlinking:", error);
    }
}

/**
 * Draw the preview ball at the given x coordinate
 *
 * @function drawPreviewBall
 * @param {number} x X coordinate for the preview ball
 */
function drawPreviewBall(x) {
    try {
        ctx.clearRect(0, 0, GAME_AREA_WIDTH, GAME_AREA_HEIGHT);
        const previewY = 50;
        ctx.beginPath();
        const ballType = BALL_TYPES[nextBallIndex];
        ctx.arc(x, previewY, ballType.size, 0, Math.PI * 2);
        ctx.fillStyle = ballType.color;
        ctx.fill();
        ctx.closePath();
    } catch (error) {
        console.error("Error in drawPreviewBall:", error);
    }
}

/**
 * Restart the game by reloading the page
 *
 * @function restartGame
 */
function restartGame() {
    try {
        location.reload();
    } catch (error) {
        console.error("Error in restartGame:", error);
    }
}

/**
 * Update the score
 *
 * @function updateScore
 * @param {number} [points=0] Points to add
 */
const updateScore = (points = 0) => {
    try {
        score += points;
        $("p.bodyCounter span").text(score);
    } catch (error) {
        console.error("Error in updateScore:", error);
    }
};

/**
 * Play the specified sound file
 *
 * @function playSound
 * @param {string} soundFile Path to the sound file to play
 */
function playSound(soundFile) {
    let audio = new Audio(soundFile);
    audio.volume = 1;
    audio.play().catch(error => console.error("Error playing sound:", error));
}

/**
 * Convert an RGB string to an object
 *
 * @function rgbStringToObject
 * @param {string} rgbString RGB color string
 * @returns {object} Object with r, g, and b values
 */
function rgbStringToObject(rgbString) {
    let match = rgbString.match(/\d+/g);
    if (match && match.length === 3) {
        return {
            r: parseInt(match[0]),
            g: parseInt(match[1]),
            b: parseInt(match[2])
        };
    }
    return { r: 255, g: 255, b: 255 };
}

/**
 * Merge animation for colliding matching planets
 *
 * @function mergeAnimation
 * @param {object} newer First colliding planet, usually the upper one
 * @param {object} older Second colliding planet, usually the lower one
 */
function mergeAnimation (newer, older) {
    Matter.Body.setStatic(newer, true);
    Matter.Body.setStatic(older, true);
    let mergeAnimation = setInterval(() => {
        let dx = older.position.x - newer.position.x;
        let dy = older.position.y - newer.position.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 1) {
            clearInterval(mergeAnimation);
            Matter.Body.setPosition(newer, {
                x: older.position.x,
                y: older.position.y
            });
            return;
        }
        Matter.Body.setPosition(newer, {
            x: newer.position.x + dx * 0.1,
            y: newer.position.y + dy * 0.1
        });
    }, ANIMATION_TIMEOUT);
}

/**
 * Create a firework animation at the given coordinates
 *
 * @function fireworkAnimation
 * @param {number} x Effect origin X coordinate
 * @param {number} y Effect origin Y coordinate
 * @param {string|object} color Effect color
 */
function fireworkAnimation(x, y, color) {
    if (typeof color === "string") {
        color = rgbStringToObject(color);
    }
    let particles = [];

    for (let i = 0; i < 15; i++) {
        let angle = Math.random() * Math.PI * 2;
        let speed = Math.random() * 5 + 2;
        let size = Math.random() * 5 + 2;

        particles.push({
            x: x,
            y: y,
            dx: Math.cos(angle) * speed,
            dy: Math.sin(angle) * speed,
            size: size,
            alpha: 1
        });
    }

    function animate() {
        effectCtx.clearRect(0, 0, effectCanvas.width, effectCanvas.height);
        particles.forEach(p => {
            p.x += p.dx;
            p.y += p.dy;
            p.alpha -= 0.02;

            effectCtx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${p.alpha})`;
            effectCtx.beginPath();
            effectCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            effectCtx.fill();
        });

        if (particles.some(p => p.alpha > 0)) {
            requestAnimationFrame(animate);
        }
    }

    animate();
}

/**
 * Zoom animation for the newly merged planet
 *
 * @function zoomAnimation
 * @param {object} newBall New planet created by merging
 * @param {number} finalSize Final size of the new planet
 */
function zoomAnimation (newBall, finalSize) {
    let growAnimation = setInterval(() => {
        let currentSize = newBall.circleRadius;
        if (currentSize >= finalSize) {
            clearInterval(growAnimation);
            return;
        }
        let scaleFactor = 1.05;
        Matter.Body.scale(newBall, scaleFactor, scaleFactor);
        newBall.render.sprite.xScale *= scaleFactor;
        newBall.render.sprite.yScale *= scaleFactor;
    }, ANIMATION_TIMEOUT);
}

/**
 * Black hole animation after merging suns
 *
 * @function blackHoleAnimation
 * @param {object} newer First sun pulled into the black hole
 * @param {object} older Second sun pulled into the black hole
 */
function blackHoleAnimation(newer, older) {
    Matter.Body.setStatic(newer, true);
    Matter.Body.setStatic(older, true);
    newer.isSensor = true;
    older.isSensor = true;

    const ballType = BALL_TYPES[BALL_TYPES.length - 1];
    let scaleX = (2 * ballType.size) / TEXTURESIZE[ballType.texture].width;
    let scaleY = (2 * ballType.size) / TEXTURESIZE[ballType.texture].height;

    const blackHole = Bodies.circle(
        GAME_AREA_WIDTH / 2,
        GAME_AREA_HEIGHT / 2,
        ballType.size,
        {
            isStatic: true,
            isSensor: true,
            render: {
                sprite: {
                    texture: ballType.texture,
                    xScale: scaleX,
                    yScale: scaleY
                }
            },
            label: "black_hole"
        }
    );
    World.add(engine.world, blackHole);

    let rotationSpeed = -0.05;
    let blackHoleRotate = setInterval(() => {
        Matter.Body.rotate(blackHole, rotationSpeed);
    }, 30);

    function moveToBlackHole(body) {
        let moveAnimation = setInterval(() => {
            let dx = blackHole.position.x - body.position.x;
            let dy = blackHole.position.y - body.position.y;
            let distance = Math.sqrt(dx * dx + dy * dy);

            let scaleFactor = 0.96;
            let moveSpeed = 0.06;

            Matter.Body.setPosition(body, {
                x: body.position.x + dx * moveSpeed,
                y: body.position.y + dy * moveSpeed
            });

            Matter.Body.scale(body, scaleFactor, scaleFactor);
            body.render.sprite.xScale *= scaleFactor;
            body.render.sprite.yScale *= scaleFactor;

            if (distance < 20) {
                clearInterval(moveAnimation);
                World.remove(engine.world, body);
            }
        }, 40);
    }

    moveToBlackHole(older);
    moveToBlackHole(newer);

    setTimeout(() => {
        clearInterval(blackHoleRotate);
        World.remove(engine.world, blackHole);
        balls = balls.filter(ball => ball !== older && ball !== newer);
        updateScore(SCORE_TABLE[SCORE_TABLE.length - 1]);
    }, 2000);
}

/**
 * Collision event handlers
 */

/**
 * Merge matching balls and update score when collisions start
 *
 * @event collisionStart
 */
Events.on(engine, "collisionStart", (event) => {
    try {
        const pairs = event.pairs;
        pairs.forEach((pair) => {
            try {
                if (
                    !pair.bodyA.label.startsWith("ball_") ||
                    !pair.bodyB.label.startsWith("ball_")
                ) {
                    return;
                }
                if (pair.bodyA.isMerging || pair.bodyB.isMerging) {
                    return;
                }
                const typeA = pair.bodyA.label.replace("ball_", "");
                const typeB = pair.bodyB.label.replace("ball_", "");
                if (typeA === typeB) {
                    let older, newer;
                    if (pair.bodyA.id < pair.bodyB.id) {
                        older = pair.bodyA;
                        newer = pair.bodyB;
                    } else {
                        older = pair.bodyB;
                        newer = pair.bodyA;
                    }
                    newer.isMerging = true;

                    const ballIndex = BALL_TYPES.findIndex(
                        (ball) => ball.name === typeA,
                    );
                    const newIndex = ballIndex + 1;
                    if (newIndex >= BALL_TYPES.length - 2 && sunCreateTime === null && gameStartTime !== null) {
                        sunCreateTime = Date.now() - gameStartTime;
                        console.log("🌞 Đã tạo Mặt Trời sau: " + sunCreateTime + " ms");
                    }
                    if (newIndex >= BALL_TYPES.length - 1) {
                        blackHoleAnimation(newer, older);
                        return;
                    }
                    // Create the merge effect
                    mergeAnimation(newer, older);

                    setTimeout(() => {
                        try {
                            let finalSize = BALL_TYPES[newIndex].size;
                            let initialSize = older.circleRadius;
                            const newBall = Bodies.circle(
                                older.position.x,
                                older.position.y,
                                initialSize,
                                {
                                    density: DENSITY,
                                    friction: FRICTION_AIR,
                                    restitution: RESTITUTION,
                                    friction: FRICTION,
                                    slop: SLOP,
                                    render: {
                                        fillStyle: BALL_TYPES[newIndex].color,
                                        sprite: {
                                            texture: BALL_TYPES[newIndex].texture,
                                            xScale: (2 * initialSize) / TEXTURESIZE[BALL_TYPES[newIndex].texture].width,
                                            yScale: (2 * initialSize) / TEXTURESIZE[BALL_TYPES[newIndex].texture].height
                                        },
                                    },
                                    label: `ball_${BALL_TYPES[newIndex].name}`,
                                },
                            );
                            World.remove(engine.world, [older, newer]);
                            balls = balls.filter(
                                (ball) => ball !== older && ball !== newer,
                            );
                            balls.push(newBall);
                            playSound("assets/soundEffect/plong.mp3");
                            World.add(engine.world, newBall);
                            updateScore(SCORE_TABLE[newIndex]);
                            // Firework animation
                            fireworkAnimation(older.position.x, older.position.y, BALL_TYPES[newIndex].color);
                            // Zoom animation for the new planet
                            zoomAnimation(newBall, finalSize);
                        } catch (delayError) {
                            console.error(
                                "Error in delayed merge:",
                                delayError,
                            );
                        }
                    }, INTERVAL_TIME / 5);
                }
            } catch (innerError) {
                console.error(
                    "Error processing collision pair in collisionStart:",
                    innerError,
                );
            }
        });
    } catch (error) {
        console.error("Error in collisionStart event handler:", error);
    }
});

let touchingSens = new Set();
let touchingLimit = new Set();

/**
 * Track balls touching the sensor or limit lines while collisions remain active
 *
 * @event collisionActive
 */
Events.on(engine, "collisionActive", (event) => {
    try {
        const pairs = event.pairs;
        pairs.forEach((pair) => {
            try {
                let { bodyA, bodyB } = pair;
                let limit = null;
                let sens = null;
                if (bodyA.label.includes("ball_") && bodyB.label === "sens") {
                    sens = bodyA;
                } else if (
                    bodyB.label.includes("ball_") &&
                    bodyA.label === "sens"
                ) {
                    sens = bodyB;
                } else if (
                    bodyA.label.includes("ball_") &&
                    bodyB.label === "limit"
                ) {
                    limit = bodyA;
                } else if (
                    bodyB.label.includes("ball_") &&
                    bodyA.label === "limit"
                ) {
                    limit = bodyB;
                }
                if (sens) {
                    touchingSens.add(sens.id);
                } else if (limit) {
                    touchingLimit.add(limit.id);
                }
            } catch (innerError) {
                console.error(
                    "Error processing collision pair in collisionActive:",
                    innerError,
                );
            }
        });
    } catch (error) {
        console.error("Error in collisionActive event handler:", error);
    }
});

/**
 * Clear contact tracking after collisions end and stop blinking when needed
 *
 * @event collisionEnd
 */
Events.on(engine, "collisionEnd", (event) => {
    try {
        event.pairs.forEach((pair) => {
            try {
                let { bodyA, bodyB } = pair;
                let sens = null;
                let limit = null;
                if (bodyA.label.includes("ball_") && bodyB.label === "sens") {
                    sens = bodyA;
                } else if (
                    bodyB.label.includes("ball_") &&
                    bodyA.label === "sens"
                ) {
                    sens = bodyB;
                } else if (
                    bodyA.label.includes("ball_") &&
                    bodyB.label === "limit"
                ) {
                    limit = bodyA;
                } else if (
                    bodyB.label.includes("ball_") &&
                    bodyA.label === "limit"
                ) {
                    limit = bodyB;
                }
                if (sens) {
                    stopBlinking();
                    touchingSens.delete(sens.id);
                } else if (limit) {
                    touchingLimit.delete(limit.id);
                }
            } catch (innerError) {
                console.error(
                    "Error processing collision pair in collisionEnd:",
                    innerError,
                );
            }
        });
    } catch (error) {
        console.error("Error in collisionEnd event handler:", error);
    }
});

/**
 * Start blinking when a ball touching the sensor line is still enough
 */
setInterval(() => {
    try {
        touchingSens.forEach((ballId) => {
            try {
                let ball = Composite.allBodies(engine.world).find(
                    (b) => b.id === ballId,
                );
                if (ball) {
                    const velocity = Math.sqrt(
                        ball.velocity.x ** 2 + ball.velocity.y ** 2,
                    );
                    if (velocity < STILLNESS_VELOCITY * 5) {
                        startBlinking();
                    }
                }
            } catch (innerError) {
                console.error(
                    "Error processing touchingSens ball in setInterval:",
                    innerError,
                );
            }
        });
    } catch (error) {
        console.error("Error in setInterval for touchingSens:", error);
    }
}, INTERVAL_TIME);

/**
 * Show the game-over alert when a ball touching the limit line is still enough
 */
setInterval(() => {
    try {
        touchingLimit.forEach((ballId) => {
            try {
                let ball = Composite.allBodies(engine.world).find(
                    (b) => b.id === ballId,
                );
                if (ball) {
                    const velocity = Math.sqrt(
                        ball.velocity.x ** 2 + ball.velocity.y ** 2,
                    );
                    if (velocity < STILLNESS_VELOCITY && !alertFlag) {
                        alertFlag = true;
                        gameOver = true;
                        stopGameProgressAutoSave();
                        saveGameProgress(true)
                        .then(data => {
                            console.log("✅ Game data sent successfully:", data);
                        })
                        .catch(error => {
                            console.error("❌ Error sending game data:", error);
                        });
                        try {
                            let gameOverModal = new tingle.modal({
                                footer: true,
                                stickyFooter: false,
                                closeMethods: [],
                                closeLabel: "Close",
                                cssClass: ["game-over-modal"],
                                onClose: function () {},
                                beforeClose: function () {
                                    return true;
                                },
                            });
                            gameOverModal.setContent(`
                                <h1 style="margin: 0; color: red;">GAME OVER...</h1>
                                <p style="margin: 10px 0;">SCORE: ${score}</p>
                            `);
                            gameOverModal.addFooterBtn(
                                "RETRY",
                                "tingle-btn tingle-btn--primary",
                                function () {
                                    gameOverModal.close();
                                    restartGame();
                                },
                            );
                            gameOverModal.open();
                        } catch (modalError) {
                            console.error(
                                "Error displaying game over modal:",
                                modalError,
                            );
                        }
                    }
                }
            } catch (innerError) {
                console.error(
                    "Error processing touchingLimit ball in setInterval:",
                    innerError,
                );
            }
        });
    } catch (error) {
        console.error("Error in setInterval for touchingLimit:", error);
    }
}, INTERVAL_TIME * 2);

let isDragging = false;

function getGameAreaOffsetX(event) {
    const rect = gameArea.getBoundingClientRect();
    const scaleX = gameArea.width / rect.width;
    return (event.clientX - rect.left) * scaleX;
}

function moveCurrentBallToEventX(event) {
    const offsetX = getGameAreaOffsetX(event);
    const currentBallRadius = currentBall.circleRadius;
    const newX = Math.max(
        Math.min(offsetX, gameArea.width - 10 - currentBallRadius),
        10 + currentBallRadius,
    );
    Body.setPosition(currentBall, {
        x: newX,
        y: currentBall.position.y,
    });
}

function releaseCurrentBall() {
    if (!gameOver && currentBall && isDragging) {
        isDragging = false;
        canMoveBall = false;
        Body.setVelocity(currentBall, { x: 0, y: 0 });
        Body.setAngularVelocity(currentBall, 0);
        Body.setStatic(currentBall, false);
        currentBall = null;
        ballCount++;
        setTimeout(() => {
            try {
                const currentIndex = nextBallIndex;
                nextBallIndex = ballCount < 2 ? 0 : SPAWN_RATE[Math.floor(Math.random() * SPAWN_RATE.length)];
                updateNextDisplay();
                createMovingBall(currentIndex);
                canMoveBall = true;
            } catch (timeoutError) {
                console.error(
                    "Error in setTimeout callback after mouseup:",
                    timeoutError,
                );
            }
        }, INTERVAL_TIME / 2);
    }
}

/**
 * mousedown: start dragging and move the ball to the clicked x coordinate
 */
gameArea.addEventListener("mousedown", (event) => {
    try {
        if (!gameOver && currentBall) {
            event.preventDefault();
            isDragging = true;
            moveCurrentBallToEventX(event);
        }
    } catch (error) {
        console.error("Error in mousedown event:", error);
    }
});

/**
 * mousemove: follow the cursor x position while dragging
 */
window.addEventListener("mousemove", (event) => {
    try {
        if (isDragging && canMoveBall && currentBall) {
            moveCurrentBallToEventX(event);
        }
    } catch (error) {
        console.error("Error in mousemove event:", error);
    }
});

/**
 * mouseup: release the ball and let it fall
 */
window.addEventListener("mouseup", () => {
    try {
        releaseCurrentBall();
    } catch (error) {
        console.error("Error in mouseup event:", error);
    }
});

/**
 * Initial setup
 */
preloadTextures.then(() => {
    try {
        updateNextDisplay();
        createMovingBall(nextBallIndex);
        gameStartTime = Date.now();
        startGameProgressAutoSave();
    } catch (error) {
        console.error("Error during initial setup:", error);
    }
});
/**
 * Start the engine and renderer
 */
try {
    const runner = Runner.create();
    Runner.run(runner, engine);
    Render.run(render);
} catch (error) {
    console.error("Error starting Engine or Render:", error);
}


/**
 * Global error handler
 */
window.addEventListener("error", (event) => {
    console.error("Global error caught:", event.error);
});
