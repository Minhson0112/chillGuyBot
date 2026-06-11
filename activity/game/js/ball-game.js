/**
 * matter.jsの基本モジュール取得
 */
const { Engine, Render, World, Body, Bodies, Composite, Mouse, Events } =
    Matter;

/**
 * 定数定義
 */

// 重力加速度
const GRAVITY = 2;

// ゲームエリアの幅と高さ（ピクセル単位）
const GAME_AREA_WIDTH = 430;
const GAME_AREA_HEIGHT = 720;

// ゲームで使用する色の定義
const COLOR = {
    red: "#FF0000"
};

// ボールタイプ一覧
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

// ボールプレビュー表示サイズ
const DISPLAY_BALL_SIZE = "20px";

// ボールの密度（質量に影響）
const DENSITY = 0.001;

// 空気抵抗（値が大きいほど落下が遅くなる）
const FRICTION_AIR = 0.03;

// 反発係数（0 に近いほど弾まない）
const RESTITUTION = 0.4;

// 摩擦係数（床や壁との摩擦）
const FRICTION = 0.1;

// 衝突時の誤差許容範囲（小さいほど正確な判定）
const SLOP = 0.3;

// 衝突処理などの間隔
const INTERVAL_TIME = 1000;

// アニメーションフレーム更新の間隔
const ANIMATION_TIMEOUT = 16;

// 静止判定の速度しきい値
const STILLNESS_VELOCITY = 0.1;

// 壁の位置とサイズ
const WALL_X = {
    left: -9,
    right: 439,
};

// 壁の中央Y座標
const WALL_Y = 370;

// 壁の高さ
const WALL_HEIGHT = 740;

// 壁の厚さ
const THICKNESS = 20;

// 床のX座標
const FLOOR_X = 215;

// 床のY座標
const FLOOR_Y = 729;

// 床の幅
const FLOOR_WIDTH = 430;

// 天井のY座標
const CELLING_Y = -9;

// ゲームオーバーラインのY座標
const GAME_OVER_LINE_Y = 110;

// 感知線のY座標
const SENS_LINE_Y = 160;

// 感知線のY座標
const LINE_THICKNESS = 1;

// スコアテーブル
const SCORE_TABLE = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55];

// ボール出現率の配列
const SPAWN_RATE = [
    0, 0, 0, 0, 0,  // stone 30%
    1, 1, 1, 1,     // moon 25%
    2, 2, 2,        // mercury 20%
    3, 3,           // mars 15%
    4               // venus 10%
];

// ボールのテクスチャサイズ
const TEXTURESIZE = {};

/**
 * 変数定義
 */

// ゲーム内のすべてのボールを格納する配列
let balls = [];

// 現在操作中のボール
let currentBall = null;

// ゲームオーバーラインの点滅を管理するためのインターバルID
let blinkInterval;

// プレイヤーのスコア
let score = 0;

let sunCreateTime = null;
let gameStartTime = null;

// ゲームオーバーのアラートを表示したかどうかを管理するフラグ
let alertFlag = false;

// ゲーム内で生成されたボールの総数
let ballCount = 0;

// 次に出現するボールのインデックス （BALL_TYPESの配列インデックス）
let nextBallIndex = 0;

// ボールを移動可能かどうかを制御するフラグ
let canMoveBall = true;

// ゲームオーバーになったかどうかの状態管理
let gameOver = false;

// エフェクトを描画するキャンバス要素を取得
let $effectCanvas = $("#effectCanvas");

//キャンバスの描画コンテキスト
let effectCtx = $effectCanvas[0].getContext("2d");

// エフェクト用キャンバスのサイズをゲームエリアに合わせて設定
$effectCanvas.attr({ width: GAME_AREA_WIDTH, height: GAME_AREA_HEIGHT });

/**
 * ボールのテクスチャリソースを事前にロードする
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

/**
 * EngineとWorldの初期化
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
 * DOM要素とRenderの初期化
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
 * ゲーム内のオブジェクトを管理するコンテナ
 */
const gameWorld = World.create();
World.add(engine.world, gameWorld);

/**
 * 静的オブジェクト（壁、床、天井、ゲームオーバーライン、感知線）の生成
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
 * 関数定義
 */

/**
 * 次に表示するボールのプレビュー表示を更新する
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
 * 指定したボールタイプの移動可能なボールを生成する
 *
 * @function createMovingBall
 * @param {number} typeIndex // BALL_TYPES配列内のインデックス
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
 * ゲームオーバーラインの点滅を開始する
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
 * ゲームオーバーラインの点滅を停止する
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
 * プレビュー用ボールを指定のx座標に描画する
 *
 * @function drawPreviewBall
 * @param {number} x // プレビュー表示するボールのx座標
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
 * ゲームを再スタート（ページリロード）する
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
 * スコアを更新する
 *
 * @function updateScore
 * @param {number} [points=0] // 加算するスコア
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
 * 指定されたサウンドファイルを再生する
 *
 * @function playSound
 * @param {string} soundFile // 再生するサウンドファイルのパス
 */
function playSound(soundFile) {
    let audio = new Audio(soundFile);
    audio.volume = 1;
    audio.play().catch(error => console.error("Error playing sound:", error));
}

/**
 * RGB形式の文字列をオブジェクトに変換する
 *
 * @function rgbStringToObject
 * @param {string} rgbString // RGBカラー形式の文字列
 * @returns {object} { r: 赤, g: 緑, b: 青 } のオブジェクト
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
 * 同じ惑星が衝突した際の合体アニメーション
 *
 * @function mergeAnimation
 * @param {object} newer 一つ目の衝突した惑星（上側の惑星）
 * @param {object} older 二つ目の衝突した惑星（下側の惑星）
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
 * 指定した座標に花火アニメーションを作成する
 *
 * @function fireworkAnimation
 * @param {number} x // エフェクトの発生位置 (X座標)
 * @param {number} y // エフェクトの発生位置 (Y座標)
 * @param {string|object} color // エフェクトの色
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
 * 惑星を合体した後の新惑星の拡大アニメーション
 *
 * @function zoomAnimation
 * @param {object} newBall // 惑星を合体した後の新惑星
 * @param {number} finalSize // 新惑星のサイズ
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
 * 太陽を合体した後のブラックホールアニメーション
 *
 * @function blackHoleAnimation
 * @param {object} newer 吸い込まれる1つ目の太陽
 * @param {object} older 吸い込まれる2つ目の太陽
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
 * 衝突イベントハンドラ
 */

/**
 * 衝突開始時に同一ラベルのボール同士を統合するかスコアを更新する
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
                    // 惑星を合体エフェクト作成
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
                            // 花火アニメーション
                            fireworkAnimation(older.position.x, older.position.y, BALL_TYPES[newIndex].color);
                            // 新惑星の拡大アニメーション
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
 * 衝突継続中に感知線や制限線に接触しているボールを追跡する
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
 * 衝突終了時に接触追跡を解除し、必要に応じて点滅を停止する
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
 * センサーに触れているボールが十分に静止している場合、点滅を開始する
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
 * 制限線に触れているボールが十分に静止している場合、ゲームオーバーのアラートを表示する
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
                        let discordId = getDiscordIdFromAuth();
                        let discordName = getDiscordUserNameFromAuth();
                        let guildId = getDiscordGuildIdFromAuth();
                        let accessToken = window.chillGuyDiscordAuth?.accessToken;
                        let requestHeaders = {
                            "Content-Type": "application/json",
                        };
                        if (accessToken) {
                            requestHeaders.Authorization = `Bearer ${accessToken}`;
                        }
                        fetch("/api/game-over", {
                            method: "POST",
                            headers: requestHeaders,
                            body: JSON.stringify({
                                discord_id: discordId,
                                username: discordName,
                                score: score,
                                sun_time: sunCreateTime,
                                guild_id: guildId,
                            }),
                        })
                        .then(response => response.json())
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

/**
 * mousedown: マウスのクリックでドラッグ開始し、クリック位置にボールのx座標を更新
 */
gameArea.addEventListener("mousedown", (event) => {
    try {
        if (!gameOver && currentBall) {
            isDragging = true;
            const { offsetX } = event;
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
    } catch (error) {
        console.error("Error in mousedown event:", error);
    }
});

/**
 * mousemove: マウスムーブ中にドラッグ状態ならボールのx位置を追従
 */
gameArea.addEventListener("mousemove", (event) => {
    try {
        if (isDragging && canMoveBall && currentBall) {
            const { offsetX } = event;
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
    } catch (error) {
        console.error("Error in mousemove event:", error);
    }
});

/**
 * mouseup: マウスボタンを離すとボールをリリースして落下させる
 */
gameArea.addEventListener("mouseup", (event) => {
    try {
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
    } catch (error) {
        console.error("Error in mouseup event:", error);
    }
});

/**
 * 初期設定
 */
preloadTextures.then(() => {
    try {
        updateNextDisplay();
        createMovingBall(nextBallIndex);
        gameStartTime = Date.now();
    } catch (error) {
        console.error("Error during initial setup:", error);
    }
});
/**
 * エンジンとレンダラーの開始
 */
try {
    Engine.run(engine);
    Render.run(render);
} catch (error) {
    console.error("Error starting Engine or Render:", error);
}


/**
 * グローバルエラーハンドラ
 */
window.addEventListener("error", (event) => {
    console.error("Global error caught:", event.error);
});
