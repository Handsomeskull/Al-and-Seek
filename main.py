import pygame
import random
import numpy as np
from collections import defaultdict, deque
import sys
import os
import multiprocessing
import copy

# Oyun Ayarları ve Sabit degerler
# Ekran boyutları
GRID_SIZE = 16
CELL_SIZE = 50
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 50
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WALL_COLOR = (50, 50, 50)
CAUGHT_COLOR = (128, 128, 128)
AGENT_COLORS = [
    (255, 87, 34), (233, 30, 99), (156, 39, 176), (103, 58, 183),
    (63, 81, 181), (3, 169, 244), (0, 150, 136), (139, 195, 74),
    (255, 235, 59), (255, 152, 0)
]

# Oyun mekanikleri
TURN_DURATION = 45
AGENT_SPEED = 4
HIDING_PROXIMITY_THRESHOLD = 8 # BFS mesafesi daha uzun olabileceğinden

# Q-Learning değerleri
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 1.0
MAX_EXPLORATION_RATE = 1.0
MIN_EXPLORATION_RATE = 0.01
EXPLORATION_DECAY_RATE = 0.001

def q_table_factory():
    " Multiprocessing ile uyumlu (pickleable) q_table defaultdict fabrika islemi"
    return np.zeros(4)

class Agent:
    " Ebe ve saklananları temsil eden ana sınıf."
    def __init__(self, role, grid_size):
        self.role = role
        self.grid_size = grid_size
        self.x = random.randint(0, self.grid_size - 1)
        self.y = random.randint(0, self.grid_size - 1)
        self.px = self.x * CELL_SIZE + CELL_SIZE // 2
        self.py = self.y * CELL_SIZE + CELL_SIZE // 2
        self.color = random.choice(AGENT_COLORS)
        self.score = 0
        self.q_table = defaultdict(q_table_factory)
        self.is_caught = False

    def get_state(self, other_agents):
        "saklananın mevcut durumunu belirler."
        relative_positions = []
        for agent in other_agents:
            relative_positions.append(self.x - agent.x)
            relative_positions.append(self.y - agent.y)
        return tuple(relative_positions)

    def choose_action(self, state, exploration_rate):
        "Epsilon-greedy stratejisi ile bir aksiyon yani hareket seç"
        if random.uniform(0, 1) < exploration_rate:
            return random.randint(0, 3)
        else:
            return np.argmax(self.q_table[state])

    def move(self, action, wall_coords):
        " Seçilen aksiyona göre saklananın HEDEF grid pozisyonunu güncelle"
        next_x, next_y = self.x, self.y
        if action == 0: next_y -= 1
        elif action == 1: next_y += 1
        elif action == 2: next_x -= 1
        elif action == 3: next_x += 1

        if not (next_x < 0 or next_x >= self.grid_size or
                next_y < 0 or next_y >= self.grid_size or
                (next_x, next_y) in wall_coords):
            self.x, self.y = next_x, next_y

    def update_q_table(self, state, action, reward, next_state):
        "Q-learning formülünü kullanarak Q-tablosunu güncell"
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        new_value = old_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_max - old_value)
        self.q_table[state][action] = new_value

    def update_pixel_pos(self):
        "piksel pozisyonunu hedef grid pozisyonuna doğru güncelle"
        target_px = self.x * CELL_SIZE + CELL_SIZE // 2
        target_py = self.y * CELL_SIZE + CELL_SIZE // 2
        dx, dy = target_px - self.px, target_py - self.py
        dist = (dx**2 + dy**2)**0.5
        if dist < AGENT_SPEED:
            self.px, self.py = target_px, target_py
        elif dist != 0:
            self.px += (dx / dist) * AGENT_SPEED
            self.py += (dy / dist) * AGENT_SPEED

    def is_at_target(self):
        " hedef grid hücresinin merkezinde olup olmadığını kontrol et"
        target_px = self.x * CELL_SIZE + CELL_SIZE // 2
        target_py = self.y * CELL_SIZE + CELL_SIZE // 2
        return self.px == target_px and self.py == target_py

    def draw(self, surface):
        "Ajanı(saklananı dangalağı) ekrana çiz"
        radius = CELL_SIZE // 2 - 5
        center = (self.px, self.py)
        draw_color = self.color if not self.is_caught else CAUGHT_COLOR
        pygame.draw.circle(surface, draw_color, center, radius)
        if self.role == 'seeker':
            pygame.draw.circle(surface, BLACK, center, radius, 3)

def create_walls(num_walls, grid_size):
    "Rastgele duvarlar oluşturur ve hem Rect listesi hem de koordinat seti döndürur"
    walls_rect = []
    wall_coords = set()
    for _ in range(num_walls * (grid_size // 8)**2):
        wall_w = random.choice([1, 2, 3])
        wall_h = random.choice([1, 2]) if wall_w < 3 else 1
        wall_x, wall_y = random.randint(0, grid_size - wall_w), random.randint(0, grid_size - wall_h)
        new_wall_rect = pygame.Rect(wall_x * CELL_SIZE, wall_y * CELL_SIZE, wall_w * CELL_SIZE, wall_h * CELL_SIZE)
        
        if not any(new_wall_rect.colliderect(r) for r in walls_rect):
            walls_rect.append(new_wall_rect)
            for r in range(wall_y, wall_y + wall_h):
                for c in range(wall_x, wall_x + wall_w):
                    wall_coords.add((c, r))
    return walls_rect, wall_coords
#bu sayede arkadaslarımız çıkışı olmayan duvarların içinde spawn olmazlar
def bresenham_los_check(x0, y0, x1, y1, wall_coords):
    "İki grid noktası arasında duvar olup olmadığını Bresenham algoritması ile kontrol eder"
    dx, sx = x1 - x0, 1 if x0 < x1 else -1
    dy, sy = y1 - y0, 1 if y0 < y1 else -1
    dx = abs(dx); dy = -abs(dy)
    err = dx + dy
    while True:
        if (x0, y0) in wall_coords: return True
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy:
            if x0 == x1: break
            err += dy; x0 += sx
        if e2 <= dx:
            if y0 == y1: break
            err += dx; y0 += sy
    return False

def bfs_distance(start_node, end_node, grid_size, wall_coords):
    "İki nokta arasındaki en kısa yol mesafesini BFS ile hesapla"
    if start_node == end_node: return 0
    q = deque([(start_node, 0)])
    visited = {start_node}
    while q:
        (x, y), dist = q.popleft()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) == end_node: return dist + 1
            if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) not in visited and (nx, ny) not in wall_coords:
                visited.add((nx, ny)); q.append(((nx, ny), dist + 1))
    return float('inf')

# yoruldum amk

def is_map_connected(grid_size, wall_coords):
    "Haritanın tamamen ulaşılabilir olup olmadığını kontrol eder (Flood Fill)."
    grid = [[(c, r) not in wall_coords for c in range(grid_size)] for r in range(grid_size)]
    total_empty = sum(sum(row) for row in grid)
    if total_empty == 0: return False
    start_node = next(((c, r) for r, row in enumerate(grid) for c, val in enumerate(row) if val), None)
    if not start_node: return False
    q, visited, count = deque([start_node]), {start_node}, 0
    while q:
        c, r = q.popleft(); count += 1
        for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nc, nr = c + dc, r + dr
            if 0 <= nr < grid_size and 0 <= nc < grid_size and grid[nr][nc] and (nc, nr) not in visited:
                visited.add((nc, nr)); q.append((nc, nr))
    return total_empty == count

def reset_turn_positions(agents, wall_coords):
    "Ajanların pozisyonlarını bir tur için sıfırlar."
    positions = set()
    for agent in agents:
        agent.is_caught = False
        while True:
            new_x, new_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (new_x, new_y) not in positions and (new_x, new_y) not in wall_coords:
                agent.x, agent.y = new_x, new_y
                agent.px, agent.py = agent.x * CELL_SIZE + CELL_SIZE // 2, agent.y * CELL_SIZE + CELL_SIZE // 2
                positions.add((agent.x, agent.y))
                break

def train_worker(args):
    "Paralel eğitim için asgari ücret ile çalışan kasiyer(işci) fonksiyonu."
    agents, wall_coords, turns_to_run, start_turn_num = args
    seeker = agents[0]
    hiders = agents[1:]

    for i in range(1, turns_to_run + 1):
        current_turn = start_turn_num + i
        exploration_rate = MIN_EXPLORATION_RATE + (MAX_EXPLORATION_RATE - MIN_EXPLORATION_RATE) * np.exp(-EXPLORATION_DECAY_RATE * current_turn)
        
        reset_turn_positions(agents, wall_coords)
        caught_this_turn = [False] * len(hiders)
        
        for _ in range(TURN_DURATION * 5):
            for j, hider in enumerate(hiders):
                if not hider.is_caught and hider.x == seeker.x and hider.y == seeker.y:
                    hider.is_caught, caught_this_turn[j] = True, True
                    seeker.score += 15; hider.score -= 15
            
            for k, agent in enumerate(agents):
                if agent.role == 'hider' and agent.is_caught: continue
                other_agents = [ag for l, ag in enumerate(agents) if k != l and not ag.is_caught]
                state = agent.get_state(other_agents)
                action = agent.choose_action(state, exploration_rate)
                
                temp_agent = Agent(agent.role, agent.grid_size); temp_agent.x, temp_agent.y = agent.x, agent.y
                temp_agent.move(action, wall_coords)

                reward = 0
                if agent.role == 'seeker':
                    reward = -0.1
                    alive_hiders = [h for h in hiders if not h.is_caught]
                    if alive_hiders:
                        closest_hider = min(alive_hiders, key=lambda h: bfs_distance((agent.x, agent.y), (h.x, h.y), GRID_SIZE, wall_coords))
                        dist_before = bfs_distance((agent.x, agent.y), (closest_hider.x, closest_hider.y), GRID_SIZE, wall_coords)
                        dist_after = bfs_distance((temp_agent.x, temp_agent.y), (closest_hider.x, closest_hider.y), GRID_SIZE, wall_coords)
                        has_los = not bresenham_los_check(agent.x, agent.y, closest_hider.x, closest_hider.y, wall_coords)

                        if any(h.x == temp_agent.x and h.y == temp_agent.y for h in alive_hiders): reward = 15
                        elif has_los and dist_after < dist_before: reward += 0.7
                        elif has_los: reward -= 0.3
                else:
                    reward = -0.05
                    dist_before = bfs_distance((agent.x, agent.y), (seeker.x, seeker.y), GRID_SIZE, wall_coords)
                    dist_after = bfs_distance((temp_agent.x, temp_agent.y), (seeker.x, seeker.y), GRID_SIZE, wall_coords)
                    is_occluded = bresenham_los_check(temp_agent.x, temp_agent.y, seeker.x, seeker.y, wall_coords)

                    if dist_after > dist_before: reward += 0.6
                    elif dist_after < dist_before: reward -= 0.6
                    if is_occluded:
                        if dist_after > HIDING_PROXIMITY_THRESHOLD: reward += 2.5
                        else: reward += 1.5
                
                next_state = temp_agent.get_state(other_agents)
                agent.update_q_table(state, action, reward, next_state)
                agent.move(action, wall_coords)

        if not any(caught_this_turn): seeker.score -= 20
        for j, hider in enumerate(hiders):
            if not caught_this_turn[j]: hider.score += 11
            
    return [(agent.q_table, agent.score) for agent in agents]

def run_headless_training_parallel(num_turns, seeker, hiders, all_agents, walls, wall_coords):
    "Çoklu işlemci kullanarak headless eğitimi yönet"
    try:
        num_cores = os.cpu_count() or 1
        print(f"\nKullanılabilir CPU çekirdeği sayısı: {num_cores}")
    except NotImplementedError:
        num_cores = 1
        print("\nCPU çekirdek sayısı tespit edilemedi, tek çekirdekle devam ediliyor.")
# BURADA THREAD SAYISINI GÖSTERİR
    turns_per_core = num_turns // num_cores
    remaining_turns = num_turns % num_cores
    
    tasks = []
    start_turn = 0
    for i in range(num_cores):
        turns_for_this_core = turns_per_core + (1 if i < remaining_turns else 0)
        if turns_for_this_core == 0: continue
        
        #Her işlem için ajanların derin(bizde deriniz) misali bir kopyasını oluştur
        agents_copy = copy.deepcopy(all_agents)
        task_args = (agents_copy, wall_coords, turns_for_this_core, start_turn)
        tasks.append(task_args)
        start_turn += turns_for_this_core

    print(f"{num_turns} tur, {len(tasks)} çekirdek üzerinde paralel olarak işlenecek...")
    
    with multiprocessing.Pool(processes=len(tasks)) as pool:
        results = pool.map(train_worker, tasks)

    print("Paralel eğitim tamamlandı. Sonuçlar birleştiriliyor...")
    
    # Sonuçları birleştir
    final_scores = [0] * len(all_agents)
    for result_set in results:
        for i, (worker_q_table, worker_score) in enumerate(result_set):
            all_agents[i].q_table.update(worker_q_table)
            final_scores[i] += worker_score

    # Skoru ortalamaya göre ayarla
    for i, agent in enumerate(all_agents):
        agent.score = final_scores[i] / len(results) if results else 0

    print("Birleştirme tamamlandı! Grafiksel mod başlatılıyor.")
    return num_turns

def main():
    "Ana oyun döngüsü"
    training_mode = False; num_training_turns = 0
    while True:
        choice = input("Lütfen bir mod seçin:\n1: Grafiksel mod (Normal Başlat)\n2: Hızlı Eğitim modu (Headless)\nSeçiminiz: ")
        if choice == '1': break
        elif choice == '2':
            training_mode = True
            while True:
                try:
                    num_training_turns = int(input("Kaç tur eğitim yapmak istersiniz? (örn: 10000): "))
                    if num_training_turns > 0: break
                    else: print("Lütfen 0'dan büyük bir sayı girin.")
                except ValueError: print("Geçersiz giriş. Lütfen bir sayı girin.")
            break
        else: print("Geçersiz seçim. Lütfen 1 veya 2 girin.")

    chosen_colors = random.sample(AGENT_COLORS, 3)
    seeker = Agent('seeker', GRID_SIZE); seeker.color = chosen_colors[0]
    hiders = [Agent('hider', GRID_SIZE), Agent('hider', GRID_SIZE)]
    hiders[0].color = chosen_colors[1]
    hiders[1].color = chosen_colors[2]
    all_agents = [seeker] + hiders
    
    print("Geçerli bir harita oluşturuluyor...")
    while True:
        walls, wall_coords = create_walls(12, GRID_SIZE)
        if is_map_connected(GRID_SIZE, wall_coords):
            print("Harita oluşturuldu.")
            break

    turn_count = 0
    if training_mode:
        turn_count = run_headless_training_parallel(num_training_turns, seeker, hiders, all_agents, walls, wall_coords)

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI and Seek")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    reset_turn_positions(all_agents, wall_coords)
    turn_count += 1
    turn_timer = TURN_DURATION * FPS
    exploration_rate = MIN_EXPLORATION_RATE + (MAX_EXPLORATION_RATE - MIN_EXPLORATION_RATE) * np.exp(-EXPLORATION_DECAY_RATE * turn_count)
    caught_this_turn = [False, False]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        turn_timer -= 1
        if turn_timer <= 0:
            if not any(caught_this_turn): seeker.score -= 20
            for i, hider in enumerate(hiders):
                if not caught_this_turn[i]: hider.score += 11
            
            print(f"Tur {turn_count} Bitti. Ebe: {int(seeker.score)}, S1: {int(hiders[0].score)}, S2: {int(hiders[1].score)}")
            reset_turn_positions(all_agents, wall_coords)
            turn_count += 1
            turn_timer = TURN_DURATION * FPS
            exploration_rate = MIN_EXPLORATION_RATE + (MAX_EXPLORATION_RATE - MIN_EXPLORATION_RATE) * np.exp(-EXPLORATION_DECAY_RATE * turn_count)
            caught_this_turn = [False, False]

        if all(agent.is_at_target() for agent in all_agents):
            for i, hider in enumerate(hiders):
                if not hider.is_caught and hider.x == seeker.x and hider.y == seeker.y:
                    hider.is_caught = True; caught_this_turn[i] = True
                    seeker.score += 15; hider.score -= 15
            
            agent_actions = {}
            for i, agent in enumerate(all_agents):
                if agent.role == 'hider' and agent.is_caught: continue
                other_agents = [ag for j, ag in enumerate(all_agents) if i != j and not ag.is_caught]
                state = agent.get_state(other_agents)
                action = agent.choose_action(state, exploration_rate)
                agent_actions[agent] = action
                
                temp_agent = Agent(agent.role, agent.grid_size); temp_agent.x, temp_agent.y = agent.x, agent.y
                temp_agent.move(action, wall_coords)
                
                
                reward = 0
                if agent.role == 'seeker':
                    reward = -0.1; alive_hiders = [h for h in hiders if not h.is_caught]
                    if alive_hiders:
                        closest_hider = min(alive_hiders, key=lambda h: bfs_distance((agent.x, agent.y), (h.x, h.y), GRID_SIZE, wall_coords))
                        dist_before = bfs_distance((agent.x, agent.y), (closest_hider.x, closest_hider.y), GRID_SIZE, wall_coords)
                        dist_after = bfs_distance((temp_agent.x, temp_agent.y), (closest_hider.x, closest_hider.y), GRID_SIZE, wall_coords)
                        has_los = not bresenham_los_check(agent.x, agent.y, closest_hider.x, closest_hider.y, wall_coords)

                        if any(h.x == temp_agent.x and h.y == temp_agent.y for h in alive_hiders): reward = 15
                        elif has_los and dist_after < dist_before: reward += 0.7
                        elif has_los: reward -= 0.3
                else: # Hider
                    reward = -0.05
                    dist_before = bfs_distance((agent.x, agent.y), (seeker.x, seeker.y), GRID_SIZE, wall_coords)
                    dist_after = bfs_distance((temp_agent.x, temp_agent.y), (seeker.x, seeker.y), GRID_SIZE, wall_coords)
                    is_occluded = bresenham_los_check(temp_agent.x, temp_agent.y, seeker.x, seeker.y, wall_coords)

                    if dist_after > dist_before: reward += 0.6
                    elif dist_after < dist_before: reward -= 0.6
                    if is_occluded:
                        if dist_after > HIDING_PROXIMITY_THRESHOLD: reward += 2.5
                        else: reward += 1.5
                
                next_state = temp_agent.get_state(other_agents)
                agent.update_q_table(state, action, reward, next_state)

            for agent, action in agent_actions.items(): agent.move(action, wall_coords)
        
        for agent in all_agents: agent.update_pixel_pos()

        screen.fill(WHITE)
        for x in range(0, WIDTH, CELL_SIZE): pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT - 50))
        for y in range(0, HEIGHT - 50, CELL_SIZE): pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))
        for wall in walls: pygame.draw.rect(screen, WALL_COLOR, wall)
        for agent in all_agents: agent.draw(screen)

        turn_text = font.render(f"Tur: {turn_count}", True, BLACK); screen.blit(turn_text, (WIDTH - turn_text.get_width() - 10, 10))
        timer_text = font.render(f"Süre: {max(0, turn_timer // FPS)}", True, BLACK); screen.blit(timer_text, (10, HEIGHT - 40))
        score_text = font.render(f"Ebe: {int(seeker.score)} | S1: {int(hiders[0].score)} | S2: {int(hiders[1].score)}", True, BLACK)
        screen.blit(score_text, (timer_text.get_width() + 20, HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
