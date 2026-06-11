<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mergeverse</title>
    <link rel="stylesheet" href="{{ asset('game/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tingle/0.15.3/tingle.min.css" />
</head>
<body>
    <div id="header"></div>

    <div id="main">
        <div id="gameRule">
            <img src="{{ asset('game/BallTexture/stoneGame.png') }}" alt="Tiêu đề">
            <img src="{{ asset('game/BallTexture/evolution.png') }}" alt="Tiến hóa">
            <button id="gameDetail">Luật chơi</button>
        </div>

        <div id="gameContainer">
            <canvas id="gameArea" width="430" height="720"></canvas>
            <p class="bodyCounter">
                <span>0</span>
            </p>
            <div id="nextBallContainer">
                <span>NEXT</span>
                <div id="nextBall"></div>
            </div>
            <canvas id="effectCanvas"></canvas>
            <canvas id="comboCanvas"></canvas>
        </div>

        <div id="gameNote">
            <h2 id="introduction">Giới thiệu hành tinh</h2>
            <ul class="planets">
                <li class="planet"><img src="{{ asset('game/BallTexture/stone.png') }}"><span>Đá</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/moon.png') }}"><span>Mặt trăng</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/mercury.png') }}"><span>Thủy tinh</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/mars.png') }}"><span>Hỏa tinh</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/venus.png') }}"><span>Kim tinh</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/earth.png') }}"><span>Trái Đất</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/neptune.png') }}"><span>Hải vương</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/uranus.png') }}"><span>Thiên vương</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/saturn.png') }}"><span>Thổ tinh</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/jupiter.png') }}"><span>Mộc tinh</span></li>
                <li class="planet"><img src="{{ asset('game/BallTexture/sun.png') }}"><span>Mặt trời</span></li>
            </ul>
        </div>
    </div>

    <div id="overlay"></div>

    <div id="gameDialog">
        <div id="dialog-header">
            <div id="dialog-title">
                <img src="{{ asset('game/BallTexture/telescope.png') }}">
                <h2>Luật chơi</h2>
            </div>
            <button id="closeDialog">
                <img src="{{ asset('game/BallTexture/closeButton.png') }}">
            </button>
        </div>
        <div class="dialog-content">
            <img src="{{ asset('game/BallTexture/evolution.png') }}" alt="Luật chơi">
            <div id="rule-content">
                <p>Giới thiệu trò chơi!</p>
                <p>🌟 Mục tiêu: Hợp nhất các hành tinh để tạo ra Mặt Trời!</p>
                <p>🪐 Ghép 2 hành tinh giống nhau để tiến hóa thành hành tinh lớn hơn!</p>
                <p>💥 Nếu các hành tinh chạm vạch over, trò chơi kết thúc!</p>
                <p>🚀 Bạn có thể trở thành người tạo ra vũ trụ không!?</p>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.17.1/matter.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tingle/0.15.3/tingle.min.js"></script>
    <script src="{{ asset('game/ball-game.js') }}"></script>
    <script src="{{ asset('game/common.js') }}"></script>

    <script>
        const DISCORD_ID = "{{ $discord_id }}";
        const USERNAME = "{{ $username }}";
    </script>
</body>
</html>
