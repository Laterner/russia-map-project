# app.py
from quart import Quart, render_template, request, jsonify, send_from_directory
import aiosqlite
import uuid
import os
from datetime import datetime
from regions import REGIONS


app = Quart(__name__)
app.static_folder = 'static'
app.static_url_path = '/static'

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'votes.db')

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (region_id) REFERENCES regions (id),
                UNIQUE(user_id)
            )
        ''')
        
        # Добавляем регионы если их нет
        for region in REGIONS:
            await db.execute(
                'INSERT OR IGNORE INTO regions (name, code) VALUES (?, ?)',
                (region["name"], region["code"])
            )
        await db.commit()

@app.before_serving
async def startup():
    await init_db()

# Получение голосов для карты
@app.route('/api/get_map_votes')
async def get_map_votes():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT r.code, COUNT(v.id) as votes_count
            FROM regions r
            LEFT JOIN votes v ON r.id = v.region_id
            GROUP BY r.id, r.code
            ORDER BY r.id
        ''')
        rows = await cursor.fetchall()
        
        result = [{"region": row[0], "votes": row[1]} for row in rows]
        return jsonify(result)

@app.route('/')
async def index():
    return await render_template('index.html')

# Главная страница с формой голосования
@app.route('/vote_page')
async def vote_page():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT id, name, code FROM regions ORDER BY name')
        regions = await cursor.fetchall()
        
        # Проверяем, голосовал ли пользователь
        user_id = request.cookies.get('user_id')
        has_voted = False
        if user_id:
            cursor = await db.execute(
                'SELECT region_id FROM votes WHERE user_id = ?',
                (user_id,)
            )
            vote = await cursor.fetchone()
            if vote:
                has_voted = True
    
    return await render_template('vote.html', regions=regions, has_voted=has_voted)

# Обработка голоса
@app.route('/vote', methods=['POST'])
async def vote():
    data = await request.form
    region_id = data.get('region_id')
    
    if not region_id:
        return jsonify({"error": "Регион не выбран"}), 400
    
    user_id = None # = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            # Проверяем, не голосовал ли уже пользователь
            cursor = await db.execute(
                'SELECT id FROM votes WHERE user_id = ?',
                (user_id,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                return jsonify({"error": "Вы уже проголосовали"}), 400
            
            # Сохраняем голос
            await db.execute(
                'INSERT INTO votes (region_id, user_id) VALUES (?, ?)',
                (int(region_id), user_id)
            )
            await db.commit()
            
            # Создаем ответ с cookie
            response = jsonify({"success": True})
            response.set_cookie('user_id', user_id, max_age=31536000)
            return response
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Статистика голосов
@app.route('/stats')
async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT r.name, r.code, COUNT(v.id) as votes_count
            FROM regions r
            LEFT JOIN votes v ON r.id = v.region_id
            GROUP BY r.id, r.name, r.code
            ORDER BY votes_count DESC
        ''')
        stats_data = await cursor.fetchall()
    
    return await render_template('stats.html', stats=stats_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)