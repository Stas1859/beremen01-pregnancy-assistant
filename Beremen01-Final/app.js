// Простое приложение для GitHub Pages
class Beremen01App {
    constructor() {
        this.userId = this.getUserId();
        this.init();
    }

    getUserId() {
        // Генерируем уникальный ID для пользователя
        let userId = localStorage.getItem('beremen01_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('beremen01_user_id', userId);
        }
        return userId;
    }

    init() {
        // Проверяем, есть ли сохраненные данные пользователя
        const savedData = localStorage.getItem('beremen01_user_data');
        if (savedData) {
            this.showMainMenu();
        } else {
            this.showWelcome();
        }
    }

    showWelcome() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="welcome">
                <div class="emoji">🤰</div>
                <h1>Добро пожаловать в Beremen01!</h1>
                <p>Ваш персональный ассистент для мониторинга беременности</p>
                <div class="welcome-features">
                    <div class="feature-item">⚖️ Мониторинг веса</div>
                    <div class="feature-item">🩸 Контроль давления</div>
                    <div class="feature-item">😊 Дневник настроения</div>
                    <div class="feature-item">🍯 Контроль сахара</div>
                </div>
                <button onclick="app.startApp()" class="btn-primary">Начать использование</button>
            </div>
        `;
    }

    startApp() {
        // Сохраняем, что пользователь начал использовать приложение
        localStorage.setItem('beremen01_user_data', JSON.stringify({
            startDate: new Date().toISOString(),
            userId: this.userId
        }));
        this.showMainMenu();
    }

    showMainMenu() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="main-menu">
                <div class="header">
                    <h2>Beremen01</h2>
                    <div class="user-info">ID: ${this.userId.substring(0, 8)}...</div>
                </div>
                
                <div class="menu-grid">
                    <div class="menu-item" onclick="app.showWeight()">
                        <div class="menu-icon">⚖️</div>
                        <div class="menu-title">Вес</div>
                        <div class="menu-desc">Мониторинг веса</div>
                    </div>
                    <div class="menu-item" onclick="app.showPressure()">
                        <div class="menu-icon">🩸</div>
                        <div class="menu-title">Давление</div>
                        <div class="menu-desc">Контроль АД</div>
                    </div>
                    <div class="menu-item" onclick="app.showMood()">
                        <div class="menu-icon">😊</div>
                        <div class="menu-title">Настроение</div>
                        <div class="menu-desc">Дневник эмоций</div>
                    </div>
                    <div class="menu-item" onclick="app.showSugar()">
                        <div class="menu-icon">🍯</div>
                        <div class="menu-title">Сахар</div>
                        <div class="menu-desc">Уровень глюкозы</div>
                    </div>
                </div>
                
                <div class="stats-summary">
                    <h3>Статистика</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-number">${this.getWeightEntries().length}</span>
                            <span class="stat-label">Записей веса</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.getPressureEntries().length}</span>
                            <span class="stat-label">Измерений АД</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.getMoodEntries().length}</span>
                            <span class="stat-label">Записей настроения</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${this.getSugarEntries().length}</span>
                            <span class="stat-label">Измерений сахара</span>
                        </div>
                    </div>
                </div>
                
                <div class="menu-actions">
                    <button onclick="app.showSettings()" class="btn-secondary">Настройки</button>
                    <button onclick="app.resetData()" class="btn-danger">Сбросить данные</button>
                </div>
            </div>
        `;
    }

    showWeight() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="weight-page">
                <h2>Мониторинг веса</h2>
                <div class="input-group">
                    <label>Вес (кг):</label>
                    <input type="number" id="weight" step="0.1" placeholder="Введите вес">
                </div>
                <div class="input-group">
                    <label>Дата:</label>
                    <input type="date" id="weight-date">
                </div>
                <button onclick="app.saveWeight()" class="btn-primary">Сохранить</button>
                <button onclick="app.showMainMenu()" class="btn-secondary">Назад</button>
                <div id="weight-history"></div>
            </div>
        `;
        document.getElementById('weight-date').value = new Date().toISOString().split('T')[0];
        this.loadWeightHistory();
    }

    saveWeight() {
        const weight = document.getElementById('weight').value;
        const date = document.getElementById('weight-date').value;
        
        if (!weight || !date) {
            alert('Пожалуйста, заполните все поля');
            return;
        }

        const weightData = JSON.parse(localStorage.getItem('weight_data') || '[]');
        weightData.push({ weight: parseFloat(weight), date, userId: this.userId });
        localStorage.setItem('weight_data', JSON.stringify(weightData));
        
        alert('Вес сохранен!');
        this.loadWeightHistory();
    }

    loadWeightHistory() {
        const weightData = JSON.parse(localStorage.getItem('weight_data') || '[]');
        const userData = weightData.filter(item => item.userId === this.userId);
        
        const historyDiv = document.getElementById('weight-history');
        if (userData.length > 0) {
            historyDiv.innerHTML = `
                <h3>История веса:</h3>
                <div class="history-list">
                    ${userData.map(item => `
                        <div class="history-item">
                            <span>${item.date}</span>
                            <span>${item.weight} кг</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    showPressure() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="pressure-page">
                <h2>Контроль давления</h2>
                <div class="input-group">
                    <label>Систолическое (верхнее):</label>
                    <input type="number" id="systolic" placeholder="120">
                </div>
                <div class="input-group">
                    <label>Диастолическое (нижнее):</label>
                    <input type="number" id="diastolic" placeholder="80">
                </div>
                <div class="input-group">
                    <label>Дата:</label>
                    <input type="date" id="pressure-date">
                </div>
                <button onclick="app.savePressure()" class="btn-primary">Сохранить</button>
                <button onclick="app.showMainMenu()" class="btn-secondary">Назад</button>
                <div id="pressure-history"></div>
            </div>
        `;
        document.getElementById('pressure-date').value = new Date().toISOString().split('T')[0];
        this.loadPressureHistory();
    }

    savePressure() {
        const systolic = document.getElementById('systolic').value;
        const diastolic = document.getElementById('diastolic').value;
        const date = document.getElementById('pressure-date').value;
        
        if (!systolic || !diastolic || !date) {
            alert('Пожалуйста, заполните все поля');
            return;
        }

        const pressureData = JSON.parse(localStorage.getItem('pressure_data') || '[]');
        pressureData.push({ systolic: parseInt(systolic), diastolic: parseInt(diastolic), date, userId: this.userId });
        localStorage.setItem('pressure_data', JSON.stringify(pressureData));
        
        alert('Давление сохранено!');
        this.loadPressureHistory();
    }

    loadPressureHistory() {
        const pressureData = JSON.parse(localStorage.getItem('pressure_data') || '[]');
        const userData = pressureData.filter(item => item.userId === this.userId);
        
        const historyDiv = document.getElementById('pressure-history');
        if (userData.length > 0) {
            historyDiv.innerHTML = `
                <h3>История давления:</h3>
                <div class="history-list">
                    ${userData.map(item => `
                        <div class="history-item">
                            <span>${item.date}</span>
                            <span>${item.systolic}/${item.diastolic}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    showMood() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="mood-page">
                <h2>Дневник настроения</h2>
                <div class="input-group">
                    <label>Настроение (1-10):</label>
                    <input type="range" id="mood" min="1" max="10" value="5">
                    <span id="mood-value">5</span>
                </div>
                <div class="input-group">
                    <label>Самочувствие (1-10):</label>
                    <input type="range" id="wellbeing" min="1" max="10" value="5">
                    <span id="wellbeing-value">5</span>
                </div>
                <div class="input-group">
                    <label>Дата:</label>
                    <input type="date" id="mood-date">
                </div>
                <button onclick="app.saveMood()" class="btn-primary">Сохранить</button>
                <button onclick="app.showMainMenu()" class="btn-secondary">Назад</button>
                <div id="mood-history"></div>
            </div>
        `;
        document.getElementById('mood-date').value = new Date().toISOString().split('T')[0];
        
        // Обновление значений при изменении слайдеров
        document.getElementById('mood').oninput = function() {
            document.getElementById('mood-value').textContent = this.value;
        };
        document.getElementById('wellbeing').oninput = function() {
            document.getElementById('wellbeing-value').textContent = this.value;
        };
        
        this.loadMoodHistory();
    }

    saveMood() {
        const mood = document.getElementById('mood').value;
        const wellbeing = document.getElementById('wellbeing').value;
        const date = document.getElementById('mood-date').value;
        
        if (!date) {
            alert('Пожалуйста, выберите дату');
            return;
        }

        const moodData = JSON.parse(localStorage.getItem('mood_data') || '[]');
        moodData.push({ mood: parseInt(mood), wellbeing: parseInt(wellbeing), date, userId: this.userId });
        localStorage.setItem('mood_data', JSON.stringify(moodData));
        
        alert('Настроение сохранено!');
        this.loadMoodHistory();
    }

    loadMoodHistory() {
        const moodData = JSON.parse(localStorage.getItem('mood_data') || '[]');
        const userData = moodData.filter(item => item.userId === this.userId);
        
        const historyDiv = document.getElementById('mood-history');
        if (userData.length > 0) {
            historyDiv.innerHTML = `
                <h3>История настроения:</h3>
                <div class="history-list">
                    ${userData.map(item => `
                        <div class="history-item">
                            <span>${item.date}</span>
                            <span>Настроение: ${item.mood}/10</span>
                            <span>Самочувствие: ${item.wellbeing}/10</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    showSugar() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="sugar-page">
                <h2>Контроль сахара</h2>
                <div class="input-group">
                    <label>Уровень сахара (ммоль/л):</label>
                    <input type="number" id="sugar" step="0.1" placeholder="5.5">
                </div>
                <div class="input-group">
                    <label>Дата:</label>
                    <input type="date" id="sugar-date">
                </div>
                <button onclick="app.saveSugar()" class="btn-primary">Сохранить</button>
                <button onclick="app.showMainMenu()" class="btn-secondary">Назад</button>
                <div id="sugar-history"></div>
            </div>
        `;
        document.getElementById('sugar-date').value = new Date().toISOString().split('T')[0];
        this.loadSugarHistory();
    }

    saveSugar() {
        const sugar = document.getElementById('sugar').value;
        const date = document.getElementById('sugar-date').value;
        
        if (!sugar || !date) {
            alert('Пожалуйста, заполните все поля');
            return;
        }

        const sugarData = JSON.parse(localStorage.getItem('sugar_data') || '[]');
        sugarData.push({ sugar: parseFloat(sugar), date, userId: this.userId });
        localStorage.setItem('sugar_data', JSON.stringify(sugarData));
        
        alert('Уровень сахара сохранен!');
        this.loadSugarHistory();
    }

    loadSugarHistory() {
        const sugarData = JSON.parse(localStorage.getItem('sugar_data') || '[]');
        const userData = sugarData.filter(item => item.userId === this.userId);
        
        const historyDiv = document.getElementById('sugar-history');
        if (userData.length > 0) {
            historyDiv.innerHTML = `
                <h3>История сахара:</h3>
                <div class="history-list">
                    ${userData.map(item => `
                        <div class="history-item">
                            <span>${item.date}</span>
                            <span>${item.sugar} ммоль/л</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    // Методы для получения данных
    getWeightEntries() {
        const weightData = JSON.parse(localStorage.getItem('weight_data') || '[]');
        return weightData.filter(item => item.userId === this.userId);
    }

    getPressureEntries() {
        const pressureData = JSON.parse(localStorage.getItem('pressure_data') || '[]');
        return pressureData.filter(item => item.userId === this.userId);
    }

    getMoodEntries() {
        const moodData = JSON.parse(localStorage.getItem('mood_data') || '[]');
        return moodData.filter(item => item.userId === this.userId);
    }

    getSugarEntries() {
        const sugarData = JSON.parse(localStorage.getItem('sugar_data') || '[]');
        return sugarData.filter(item => item.userId === this.userId);
    }

    // Настройки
    showSettings() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="settings-page">
                <h2>Настройки</h2>
                <div class="settings-section">
                    <h3>Информация о пользователе</h3>
                    <div class="setting-item">
                        <label>ID пользователя:</label>
                        <input type="text" value="${this.userId}" readonly>
                    </div>
                    <div class="setting-item">
                        <label>Дата регистрации:</label>
                        <input type="text" value="${new Date().toLocaleDateString()}" readonly>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Данные</h3>
                    <div class="setting-item">
                        <label>Записей веса:</label>
                        <span>${this.getWeightEntries().length}</span>
                    </div>
                    <div class="setting-item">
                        <label>Измерений давления:</label>
                        <span>${this.getPressureEntries().length}</span>
                    </div>
                    <div class="setting-item">
                        <label>Записей настроения:</label>
                        <span>${this.getMoodEntries().length}</span>
                    </div>
                    <div class="setting-item">
                        <label>Измерений сахара:</label>
                        <span>${this.getSugarEntries().length}</span>
                    </div>
                </div>
                
                <div class="settings-actions">
                    <button onclick="app.exportData()" class="btn-primary">Экспорт данных</button>
                    <button onclick="app.showMainMenu()" class="btn-secondary">Назад</button>
                </div>
            </div>
        `;
    }

    // Экспорт данных
    exportData() {
        const data = {
            userId: this.userId,
            exportDate: new Date().toISOString(),
            weight: this.getWeightEntries(),
            pressure: this.getPressureEntries(),
            mood: this.getMoodEntries(),
            sugar: this.getSugarEntries()
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `beremen01_data_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        alert('Данные экспортированы!');
    }

    // Сброс данных
    resetData() {
        if (confirm('Вы уверены, что хотите сбросить все данные? Это действие нельзя отменить.')) {
            localStorage.removeItem('weight_data');
            localStorage.removeItem('pressure_data');
            localStorage.removeItem('mood_data');
            localStorage.removeItem('sugar_data');
            localStorage.removeItem('beremen01_user_data');
            
            alert('Все данные сброшены!');
            this.showWelcome();
        }
    }
}

// Инициализация приложения
const app = new Beremen01App();
