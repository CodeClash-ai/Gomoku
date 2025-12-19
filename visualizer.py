#!/usr/bin/env python3
"""
Gomoku Game Visualizer
A web-based visualizer for replaying Gomoku game logs.
Usage: python visualizer.py [--port PORT] [--logs-dir LOGS_DIR]
"""

import argparse
import json
import os
from pathlib import Path
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Global configuration
LOGS_DIR = "logs"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gomoku Game Visualizer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 30px;
        }
        
        .game-selector {
            margin-bottom: 30px;
            text-align: center;
        }
        
        .game-selector label {
            font-size: 1.1em;
            margin-right: 10px;
            font-weight: 600;
        }
        
        .game-selector select {
            padding: 10px 20px;
            font-size: 1em;
            border: 2px solid #667eea;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            min-width: 300px;
        }
        
        .game-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .game-info.active {
            display: block;
        }
        
        .info-row {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .info-item {
            text-align: center;
        }
        
        .info-label {
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 1.2em;
            color: #333;
        }
        
        .game-area {
            display: none;
            gap: 30px;
        }
        
        .game-area.active {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            flex-wrap: wrap;
        }
        
        .board-container {
            flex: 1;
            min-width: 500px;
            max-width: 600px;
        }
        
        .board {
            background: #daa520;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: inline-block;
        }
        
        .board-grid {
            display: grid;
            gap: 0;
            background: #8b6914;
        }
        
        .cell {
            width: 30px;
            height: 30px;
            border: 1px solid #8b6914;
            background: #daa520;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
        }
        
        .cell:hover {
            background: #e6b930;
        }
        
        .stone {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .stone.black {
            background: radial-gradient(circle at 30% 30%, #555, #000);
        }
        
        .stone.white {
            background: radial-gradient(circle at 30% 30%, #fff, #ddd);
        }
        
        .stone.last-move {
            box-shadow: 0 0 0 3px #ff4444;
        }
        
        .controls-container {
            flex: 0 0 300px;
        }
        
        .controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            position: sticky;
            top: 20px;
        }
        
        .move-info {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 6px;
        }
        
        .move-counter {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .current-player {
            font-size: 1.1em;
            color: #666;
        }
        
        .buttons {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        button {
            padding: 12px 20px;
            font-size: 1em;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .speed-control {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
        }
        
        .speed-control label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #666;
        }
        
        .speed-control input {
            width: 100%;
        }
        
        .move-list {
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            padding: 10px;
        }
        
        .move-item {
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .move-item:hover {
            background: #e9ecef;
        }
        
        .move-item.active {
            background: #667eea;
            color: white;
            font-weight: 600;
        }
        
        .winner-banner {
            display: none;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 20px;
            margin-top: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            animation: slideIn 0.5s;
        }
        
        .winner-banner.active {
            display: block;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .no-games {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Gomoku Game Visualizer</h1>
            <p>Replay and analyze your Gomoku games</p>
        </div>
        
        <div class="content">
            <div class="game-selector">
                <label for="game-select">Select a game:</label>
                <select id="game-select">
                    <option value="">-- Choose a game log --</option>
                </select>
            </div>
            
            <div id="game-info" class="game-info">
                <div class="info-row">
                    <div class="info-item">
                        <div class="info-label">Game #</div>
                        <div class="info-value" id="info-game-num">-</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Black Player</div>
                        <div class="info-value" id="info-black">-</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">White Player</div>
                        <div class="info-value" id="info-white">-</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Total Moves</div>
                        <div class="info-value" id="info-moves">-</div>
                    </div>
                </div>
            </div>
            
            <div id="game-area" class="game-area">
                <div class="board-container">
                    <div class="board">
                        <div id="board" class="board-grid"></div>
                    </div>
                    <div id="winner-banner" class="winner-banner"></div>
                </div>
                
                <div class="controls-container">
                    <div class="controls">
                        <div class="move-info">
                            <div class="move-counter" id="move-counter">Move 0</div>
                            <div class="current-player" id="current-player">Start</div>
                        </div>
                        
                        <div class="buttons">
                            <button class="btn-secondary" id="btn-first">⏮ First</button>
                            <button class="btn-secondary" id="btn-prev">◀ Previous</button>
                            <button class="btn-primary" id="btn-play">▶ Play</button>
                            <button class="btn-secondary" id="btn-next">Next ▶</button>
                            <button class="btn-secondary" id="btn-last">Last ⏭</button>
                            <button class="btn-danger" id="btn-reset">↺ Reset</button>
                        </div>
                        
                        <div class="speed-control">
                            <label>Playback Speed: <span id="speed-value">1.0x</span></label>
                            <input type="range" id="speed-slider" min="0.5" max="3" step="0.5" value="1">
                        </div>
                        
                        <div class="move-list" id="move-list"></div>
                    </div>
                </div>
            </div>
            
            <div id="no-games" class="no-games" style="display: none;">
                No game logs found. Run some games first!
            </div>
        </div>
    </div>
    
    <script>
        let currentGame = null;
        let currentMoveIndex = 0;
        let isPlaying = false;
        let playInterval = null;
        let playbackSpeed = 1.0;
        
        // Load available games
        async function loadGames() {
            try {
                const response = await fetch('/api/games');
                const games = await response.json();
                
                const select = document.getElementById('game-select');
                select.innerHTML = '<option value="">-- Choose a game log --</option>';
                
                if (games.length === 0) {
                    document.getElementById('no-games').style.display = 'block';
                    return;
                }
                
                games.forEach(game => {
                    const option = document.createElement('option');
                    option.value = game.filename;
                    option.textContent = `Game #${game.game_number} - ${game.timestamp} (${game.moves} moves)`;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading games:', error);
            }
        }
        
        // Load a specific game
        async function loadGame(filename) {
            try {
                const response = await fetch(`/api/game/${filename}`);
                currentGame = await response.json();
                currentMoveIndex = 0;
                
                setupBoard();
                updateGameInfo();
                renderBoard();
                updateMoveList();
                
                document.getElementById('game-info').classList.add('active');
                document.getElementById('game-area').classList.add('active');
            } catch (error) {
                console.error('Error loading game:', error);
            }
        }
        
        // Setup the board grid
        function setupBoard() {
            const board = document.getElementById('board');
            const size = currentGame.board_size;
            board.style.gridTemplateColumns = `repeat(${size}, 30px)`;
            board.innerHTML = '';
            
            for (let i = 0; i < size * size; i++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.index = i;
                board.appendChild(cell);
            }
        }
        
        // Update game info display
        function updateGameInfo() {
            document.getElementById('info-game-num').textContent = currentGame.game_number;
            document.getElementById('info-black').textContent = currentGame.players.black.name;
            document.getElementById('info-white').textContent = currentGame.players.white.name;
            document.getElementById('info-moves').textContent = currentGame.moves.length;
        }
        
        // Render the current board state
        function renderBoard() {
            const cells = document.querySelectorAll('.cell');
            cells.forEach(cell => cell.innerHTML = '');
            
            const size = currentGame.board_size;
            
            for (let i = 0; i <= currentMoveIndex && i < currentGame.moves.length; i++) {
                const move = currentGame.moves[i];
                const index = move.x * size + move.y;
                const cell = cells[index];
                
                const stone = document.createElement('div');
                stone.className = `stone ${move.player}`;
                if (i === currentMoveIndex && currentMoveIndex > 0) {
                    stone.classList.add('last-move');
                }
                cell.appendChild(stone);
            }
            
            updateMoveInfo();
            checkWinner();
        }
        
        // Update move counter and current player
        function updateMoveInfo() {
            document.getElementById('move-counter').textContent = `Move ${currentMoveIndex}`;
            
            if (currentMoveIndex === 0) {
                document.getElementById('current-player').textContent = 'Start';
            } else if (currentMoveIndex < currentGame.moves.length) {
                const nextPlayer = currentGame.moves[currentMoveIndex].player === 'black' ? 'White' : 'Black';
                document.getElementById('current-player').textContent = `Next: ${nextPlayer}`;
            } else {
                document.getElementById('current-player').textContent = 'Game Over';
            }
        }
        
        // Check if we've reached the winner
        function checkWinner() {
            const banner = document.getElementById('winner-banner');
            
            if (currentMoveIndex === currentGame.moves.length) {
                const winner = currentGame.winner;
                if (winner === 'draw') {
                    banner.textContent = "🤝 Game ended in a draw!";
                } else {
                    banner.textContent = `🎉 ${winner} wins!`;
                }
                banner.classList.add('active');
                stopPlaying();
            } else {
                banner.classList.remove('active');
            }
        }
        
        // Update move list
        function updateMoveList() {
            const list = document.getElementById('move-list');
            list.innerHTML = '';
            
            currentGame.moves.forEach((move, index) => {
                const item = document.createElement('div');
                item.className = 'move-item';
                if (index === currentMoveIndex - 1) {
                    item.classList.add('active');
                }
                item.textContent = `${index + 1}. ${move.player} (${move.x}, ${move.y})`;
                item.onclick = () => {
                    currentMoveIndex = index + 1;
                    renderBoard();
                    updateMoveList();
                };
                list.appendChild(item);
            });
        }
        
        // Control functions
        function firstMove() {
            stopPlaying();
            currentMoveIndex = 0;
            renderBoard();
            updateMoveList();
        }
        
        function prevMove() {
            stopPlaying();
            if (currentMoveIndex > 0) {
                currentMoveIndex--;
                renderBoard();
                updateMoveList();
            }
        }
        
        function nextMove() {
            if (currentMoveIndex < currentGame.moves.length) {
                currentMoveIndex++;
                renderBoard();
                updateMoveList();
            } else {
                stopPlaying();
            }
        }
        
        function lastMove() {
            stopPlaying();
            currentMoveIndex = currentGame.moves.length;
            renderBoard();
            updateMoveList();
        }
        
        function togglePlay() {
            if (isPlaying) {
                stopPlaying();
            } else {
                startPlaying();
            }
        }
        
        function startPlaying() {
            if (currentMoveIndex >= currentGame.moves.length) {
                currentMoveIndex = 0;
                renderBoard();
                updateMoveList();
            }
            
            isPlaying = true;
            document.getElementById('btn-play').textContent = '⏸ Pause';
            
            const interval = 1000 / playbackSpeed;
            playInterval = setInterval(() => {
                nextMove();
            }, interval);
        }
        
        function stopPlaying() {
            isPlaying = false;
            document.getElementById('btn-play').textContent = '▶ Play';
            if (playInterval) {
                clearInterval(playInterval);
                playInterval = null;
            }
        }
        
        function resetGame() {
            stopPlaying();
            firstMove();
        }
        
        // Event listeners
        document.getElementById('game-select').addEventListener('change', (e) => {
            if (e.target.value) {
                stopPlaying();
                loadGame(e.target.value);
            }
        });
        
        document.getElementById('btn-first').addEventListener('click', firstMove);
        document.getElementById('btn-prev').addEventListener('click', prevMove);
        document.getElementById('btn-play').addEventListener('click', togglePlay);
        document.getElementById('btn-next').addEventListener('click', nextMove);
        document.getElementById('btn-last').addEventListener('click', lastMove);
        document.getElementById('btn-reset').addEventListener('click', resetGame);
        
        document.getElementById('speed-slider').addEventListener('input', (e) => {
            playbackSpeed = parseFloat(e.target.value);
            document.getElementById('speed-value').textContent = `${playbackSpeed}x`;
            
            if (isPlaying) {
                stopPlaying();
                startPlaying();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!currentGame) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    prevMove();
                    break;
                case 'ArrowRight':
                    nextMove();
                    break;
                case ' ':
                    e.preventDefault();
                    togglePlay();
                    break;
                case 'Home':
                    firstMove();
                    break;
                case 'End':
                    lastMove();
                    break;
                case 'r':
                case 'R':
                    resetGame();
                    break;
            }
        });
        
        // Initialize
        loadGames();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve the main visualizer page."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/games")
def get_games():
    """Get list of available game logs."""
    games = []
    logs_path = Path(LOGS_DIR)

    if not logs_path.exists():
        return jsonify([])

    for json_file in sorted(logs_path.glob("*.json"), reverse=True):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                games.append(
                    {
                        "filename": json_file.name,
                        "game_number": data.get("game_number", "?"),
                        "timestamp": data.get("timestamp", "Unknown"),
                        "moves": len(data.get("moves", [])),
                    }
                )
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    return jsonify(games)


@app.route("/api/game/<filename>")
def get_game(filename):
    """Get a specific game log."""
    # Security check: only allow JSON files from logs directory
    if not filename.endswith(".json") or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    file_path = Path(LOGS_DIR) / filename

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    """Run the visualizer server."""
    global LOGS_DIR

    parser = argparse.ArgumentParser(description="Gomoku Game Visualizer")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--logs-dir", type=str, default="logs", help="Directory containing game logs"
    )
    args = parser.parse_args()

    LOGS_DIR = args.logs_dir

    print(f"\n{'=' * 60}")
    print("🎮 Gomoku Game Visualizer")
    print(f"{'=' * 60}")
    print(f"\n📁 Logs directory: {os.path.abspath(LOGS_DIR)}")
    print(f"🌐 Server running at: http://localhost:{args.port}")
    print("\n💡 Keyboard shortcuts:")
    print("   ← → : Previous/Next move")
    print("   Space: Play/Pause")
    print("   Home/End: First/Last move")
    print("   R: Reset to start")
    print(f"\n{'=' * 60}\n")

    app.run(debug=True, port=args.port, host="0.0.0.0")


if __name__ == "__main__":
    main()
