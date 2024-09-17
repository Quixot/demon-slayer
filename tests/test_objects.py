import sys, os

# Добавляем путь к модулю с классами
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from game import Player, Enemy
from config.config import WIDTH, HEIGHT

def test_player_initialization():
    player = Player()
    assert player.rect.center == (WIDTH // 2, HEIGHT - 150)
    assert player.speed_x == 0
    assert player.speed_y == 0
    assert not player.on_ground
    assert player.last_direction == 'right'
    assert not player.is_shooting
