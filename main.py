import pygame
import sys
import random
import json
import os

# --- Ініціалізація ---
pygame.init()
pygame.mixer.init() # Для звуку

WIDTH, HEIGHT = 360, 640 
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Crypto Tapper")

# Кольори
BLACK, WHITE, GOLD = (10, 10, 10), (240, 240, 240), (255, 200, 0)
GREEN, RED, GRAY = (0, 255, 100), (255, 50, 50), (35, 35, 35)
PURPLE, BLUE = (120, 0, 200), (0, 120, 255)

def get_font(size):
    try: return pygame.font.SysFont("sans-serif", size, bold=True)
    except: return pygame.font.Font(None, size)

font_main = get_font(20)
font_small = get_font(16)
font_tiny = get_font(13)

# --- ЗБЕРЕЖЕННЯ ---
SAVE_FILE = "player_save.json"
game_data = {
    "btc": 0.0, "usd": 0.0, "taps": 0, 
    "task_done": False, "click_lvl": 1, "miners": 0
}

def save_game():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(game_data, f)
    except: pass

if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            game_data.update(json.load(f))
    except: pass

# --- Економіка та Таймери ---
mode = "TAPPER"
btc_price = 62000.0
price_history = [62000.0] * 20
last_update = pygame.time.get_ticks()
last_passive = pygame.time.get_ticks()
UPDATE_INTERVAL = 20000 # Таймер 20 секунд
save_timer_vis = 0
tap_effects = []

clock = pygame.time.Clock()

def draw_text(text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    screen.blit(img, rect)

# Головний цикл
while True:
    screen.fill(BLACK)
    now = pygame.time.get_ticks()
    
    # Розрахунок часу для таймера
    time_passed = now - last_update
    time_left = max(0, (UPDATE_INTERVAL - time_passed) // 1000)

    # Пасивний дохід від майнерів (щосекунди)
    if now - last_passive > 1000:
        game_data["usd"] += game_data["miners"] * 0.5
        last_passive = now

    # Оновлення курсу кожні 20 секунд
    if time_passed > UPDATE_INTERVAL:
        btc_price += btc_price * random.uniform(-0.07, 0.07)
        price_history.append(btc_price)
        if len(price_history) > 20: price_history.pop(0)
        last_update = now
        save_game()

    # ВЕРХНЯ ПАНЕЛЬ
    pygame.draw.rect(screen, (25, 25, 25), (0, 0, WIDTH, 95))
    draw_text(f"USD: ${round(game_data['usd'], 2)}", font_main, GREEN, 15, 15)
    draw_text(f"BTC: {round(game_data['btc'], 4)}", font_small, GOLD, 15, 42)
    draw_text(f"Оновлення: {time_left}с", font_tiny, WHITE, 15, 68)

    # Кнопка SAVE
    s_col = WHITE if now < save_timer_vis else BLUE
    save_btn = pygame.draw.rect(screen, s_col, (WIDTH - 85, 20, 70, 35), border_radius=8)
    draw_text("SAVE", font_tiny, BLACK if now < save_timer_vis else WHITE, WIDTH - 50, 37, True)

    # МЕНЮ (1/3 ширини екрана)
    m_w = WIDTH // 3
    btn_tap_rect = pygame.Rect(0, HEIGHT-70, m_w, 70)
    btn_mkt_rect = pygame.Rect(m_w, HEIGHT-70, m_w, 70)
    btn_shp_rect = pygame.Rect(m_w*2, HEIGHT-70, m_w, 70)
    
    pygame.draw.rect(screen, PURPLE if mode == "TAPPER" else GRAY, btn_tap_rect)
    pygame.draw.rect(screen, BLUE if mode == "MARKET" else GRAY, btn_mkt_rect)
    pygame.draw.rect(screen, (0, 150, 0) if mode == "SHOP" else GRAY, btn_shp_rect)
    
    draw_text("ТАП", font_tiny, WHITE, m_w//2, HEIGHT-35, True)
    draw_text("БІРЖА", font_tiny, WHITE, m_w + m_w//2, HEIGHT-35, True)
    draw_text("МАГАЗ", font_tiny, WHITE, m_w*2 + m_w//2, HEIGHT-35, True)

    # Клік-зони
    tap_circle = up_click_btn = buy_miner_btn = buy_btn = sell_btn = claim_btn = pygame.Rect(0,0,0,0)

    if mode == "TAPPER":
        tap_circle = pygame.draw.circle(screen, GOLD, (WIDTH//2, HEIGHT//2), 75)
        draw_text("₿", get_font(35), BLACK, WIDTH//2, HEIGHT//2, True)
        draw_text(f"Тапи: {game_data['taps']}", font_main, WHITE, WIDTH//2, HEIGHT//2 + 95, True)
        
        # КВЕСТ (50 тапів)
        if not game_data["task_done"] and game_data["taps"] >= 50:
            claim_btn = pygame.draw.rect(screen, GREEN, (WIDTH//2-70, 485, 140, 40), border_radius=10)
            draw_text("ВЗЯТИ 1 BTC", font_tiny, BLACK, WIDTH//2, 505, True)

        for effect in tap_effects[:]:
            draw_text(f"+${round(0.01 * game_data['click_lvl'], 2)}", font_tiny, GREEN, effect['x'], effect['y'])
            effect['y'] -= 2; effect['life'] -= 1
            if effect['life'] <= 0: tap_effects.remove(effect)

    elif mode == "MARKET":
        draw_text(f"КУРС: ${round(btc_price, 1)}", font_main, GOLD, WIDTH//2, 115, True)
        graph_rect = pygame.Rect(20, 150, WIDTH-40, 140)
        pygame.draw.rect(screen, (20, 20, 20), graph_rect)
        
        p_w = (time_passed / UPDATE_INTERVAL) * (WIDTH - 40)
        pygame.draw.rect(screen, GRAY, (20, 295, WIDTH-40, 5))
        pygame.draw.rect(screen, BLUE, (20, 295, p_w, 5))

        if len(price_history) > 1:
            try:
                min_p, max_p = min(price_history), max(price_history)
                rng = (max_p - min_p) if max_p != min_p else 1
                pts = [(20 + i*((WIDTH-40)/19), 290 - ((p-min_p)/rng*120)) for i, p in enumerate(price_history)]
                pygame.draw.lines(screen, GREEN if price_history[-1] >= price_history[-2] else RED, False, pts, 2)
            except: pass
        
        buy_btn = pygame.draw.rect(screen, GREEN, (20, 340, 155, 50), border_radius=10)
        draw_text("КУПИТИ 0.1", font_tiny, BLACK, 97, 365, True)
        sell_btn = pygame.draw.rect(screen, RED, (185, 340, 155, 50), border_radius=10)
        draw_text("ПРОДАТИ ВСЕ", font_tiny, WHITE, 262, 365, True)

    elif mode == "SHOP":
        draw_text("МАГАЗИН", font_main, WHITE, WIDTH//2, 120, True)
        
        # Покращення кліку
        click_cost = game_data["click_lvl"] * 15
        up_click_btn = pygame.draw.rect(screen, PURPLE, (20, 160, WIDTH-40, 75), border_radius=10)
        draw_text(f"Клік (Lvl {game_data['click_lvl']})", font_small, WHITE, 40, 175)
        draw_text(f"Ціна: ${click_cost}", font_tiny, GOLD, 40, 200)

        # Покращення майнерів
        miner_cost = (game_data["miners"] + 1) * 60
        buy_miner_btn = pygame.draw.rect(screen, BLUE, (20, 255, WIDTH-40, 75), border_radius=10)
        draw_text(f"Майнер (x{game_data['miners']})", font_small, WHITE, 40, 270)
        draw_text(f"Ціна: ${miner_cost} (+$0.5/с)", font_tiny, GOLD, 40, 295)

    # Обробка подій
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            save_game()
            pygame.quit(); sys.exit()
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if save_btn.collidepoint(pos):
                save_game()
                save_timer_vis = now + 300

            if btn_tap_rect.collidepoint(pos): mode = "TAPPER"
            if btn_mkt_rect.collidepoint(pos): mode = "MARKET"
            if btn_shp_rect.collidepoint(pos): mode = "SHOP"
            
            if mode == "TAPPER":
                if tap_circle.collidepoint(pos):
                    game_data['taps'] += 1
                    game_data['usd'] += 0.01 * game_data['click_lvl']
                    tap_effects.append({'x': pos[0], 'y': pos[1], 'life': 12})
                if claim_btn.collidepoint(pos) and not game_data["task_done"]:
                    game_data["btc"] += 1.0
                    game_data["task_done"] = True
                    save_game()
            
            elif mode == "SHOP":
                if up_click_btn.collidepoint(pos) and game_data["usd"] >= (game_data["click_lvl"] * 15):
                    game_data["usd"] -= (game_data["click_lvl"] * 15)
                    game_data["click_lvl"] += 1
                m_c = (game_data["miners"] + 1) * 60
                if buy_miner_btn.collidepoint(pos) and game_data["usd"] >= m_c:
                    game_data["usd"] -= m_c
                    game_data["miners"] += 1
            
            elif mode == "MARKET":
                cost_01 = btc_price * 0.1
                if buy_btn.collidepoint(pos) and game_data['usd'] >= cost_01:
                    game_data['usd'] -= cost_01
                    game_data['btc'] += 0.1
                if sell_btn.collidepoint(pos) and game_data['btc'] > 0:
                    game_data['usd'] += game_data['btc'] * btc_price
                    game_data['btc'] = 0

    pygame.display.flip()
    clock.tick(30)
       
