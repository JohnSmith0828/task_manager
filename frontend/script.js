// frontend/script.js
class TaskManagerApp {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000/api';
        this.token = localStorage.getItem('token');
        this.currentUser = null;
        this.tasks = [];
        this.currentFilter = 'all';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        if (this.token) {
            this.showMainSection();
            this.loadUserProfile();
            this.loadTasks();
            this.loadStatistics();
        } else {
            this.showLoginSection();
        }
    }
    
    bindEvents() {
        // 認証関連イベント
        document.getElementById('login-form').addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form').addEventListener('submit', (e) => this.handleRegister(e));
        document.getElementById('logout-btn').addEventListener('click', () => this.handleLogout());
        
        // 画面切り替え
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterSection();
        });
        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginSection();
        });
        
        // タスク関連イベント
        document.getElementById('task-form').addEventListener('submit', (e) => this.handleCreateTask(e));
        
        // フィルタイベント
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilter(e));
        });
    }
    
    // API呼び出しヘルパー
    async apiCall(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Token ${this.token}` })
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || JSON.stringify(data));
            }
            
            return data;
        } catch (error) {
            this.showMessage(`エラー: ${error.message}`, 'error');
            throw error;
        }
    }
    
    // 認証処理
    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const loginData = {
            username: formData.get('username') || document.getElementById('login-username').value,
            password: formData.get('password') || document.getElementById('login-password').value
        };
        
        try {
            const response = await this.apiCall('/auth/login/', {
                method: 'POST',
                body: JSON.stringify(loginData)
            });
            
            this.token = response.token;
            this.currentUser = response.user;
            localStorage.setItem('token', this.token);
            
            this.showMessage('ログインしました', 'success');
            this.showMainSection();
            this.loadTasks();
            this.loadStatistics();
        } catch (error) {
            console.error('Login failed:', error);
        }
    }
    
    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const registerData = {
            username: formData.get('username') || document.getElementById('register-username').value,
            email: formData.get('email') || document.getElementById('register-email').value,
            password: formData.get('password') || document.getElementById('register-password').value,
            password_confirm: formData.get('password_confirm') || document.getElementById('register-password-confirm').value
        };
        
        try {
            const response = await this.apiCall('/auth/register/', {
                method: 'POST',
                body: JSON.stringify(registerData)
            });
            
            this.token = response.token;
            this.currentUser = response.user;
            localStorage.setItem('token', this.token);
            
            this.showMessage('登録が完了しました', 'success');
            this.showMainSection();
            this.loadTasks();
            this.loadStatistics();
        } catch (error) {
            console.error('Registration failed:', error);
        }
    }
    
    async handleLogout() {
        try {
            await this.apiCall('/auth/logout/', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.token = null;
            this.currentUser = null;
            localStorage.removeItem('token');
            this.showMessage('ログアウトしました', 'success');
            this.showLoginSection();
        }
    }
    
    async loadUserProfile() {
        if (!this.currentUser) {
            try {
                this.currentUser = await this.apiCall('/auth/profile/');
                document.getElementById('username-display').textContent = this.currentUser.username;
            } catch (error) {
                console.error('Profile load failed:', error);
            }
        } else {
            document.getElementById('username-display').textContent = this.currentUser.username;
        }
    }
    
    // タスク処理
    async loadTasks() {
        try {
            const response = await this.apiCall('/tasks/');
            this.tasks = response.results || response;
            this.renderTasks();
        } catch (error) {
            console.error('Tasks load failed:', error);
        }
    }
    
    async handleCreateTask(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        const taskData = {
            title: formData.get('title') || document.getElementById('task-title').value,
            description: formData.get('description') || document.getElementById('task-description').value,
            priority: formData.get('priority') || document.getElementById('task-priority').value,
            due_date: formData.get('due_date') || document.getElementById('task-due-date').value || null
        };
        
        if (!taskData.title.trim()) {
            this.showMessage('タスクタイトルを入力してください', 'error');
            return;
        }
        
        try {
            await this.apiCall('/tasks/', {
                method: 'POST',
                body: JSON.stringify(taskData)
            });
            
            this.showMessage('タスクを作成しました', 'success');
            e.target.reset();
            this.loadTasks();
            this.loadStatistics();
        } catch (error) {
            console.error('Task creation failed:', error);
        }
    }
    
    async toggleTask(taskId) {
        try {
            await this.apiCall(`/tasks/${taskId}/toggle/`, { method: 'POST' });
            this.loadTasks();
            this.loadStatistics();
        } catch (error) {
            console.error('Task toggle failed:', error);
        }
    }
    
    async deleteTask(taskId) {
        if (!confirm('このタスクを削除しますか？')) return;
        
        try {
            await this.apiCall(`/tasks/${taskId}/`, { method: 'DELETE' });
            this.showMessage('タスクを削除しました', 'success');
            this.loadTasks();
            this.loadStatistics();
        } catch (error) {
            console.error('Task deletion failed:', error);
        }
    }
    
    // 統計処理
    async loadStatistics() {
        try {
            const stats = await this.apiCall('/tasks/statistics/');
            document.getElementById('total-tasks').textContent = stats.total_tasks;
            document.getElementById('completed-tasks').textContent = stats.completed_tasks;
            document.getElementById('pending-tasks').textContent = stats.pending_tasks;
            document.getElementById('overdue-tasks').textContent = stats.overdue_tasks;
        } catch (error) {
            console.error('Statistics load failed:', error);
        }
    }
    
    // UI処理
    showLoginSection() {
        document.getElementById('login-section').style.display = 'flex';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('main-section').style.display = 'none';
    }
    
    showRegisterSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'flex';
        document.getElementById('main-section').style.display = 'none';
    }
    
    showMainSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('main-section').style.display = 'block';
    }
    
    handleFilter(e) {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        this.currentFilter = e.target.dataset.filter;
        this.renderTasks();
    }
    
    renderTasks() {
        const container = document.getElementById('tasks-list');
        
        let filteredTasks = this.tasks;
        if (this.currentFilter === 'completed') {
            filteredTasks = this.tasks.filter(task => task.is_completed);
        } else if (this.currentFilter === 'pending') {
            filteredTasks = this.tasks.filter(task => !task.is_completed);
        }
        
        if (filteredTasks.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; margin: 2rem 0;">タスクがありません</p>';
            return;
        }
        
        container.innerHTML = filteredTasks.map(task => this.createTaskHTML(task)).join('');
        
        // イベントリスナーを追加
        container.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => this.toggleTask(btn.dataset.taskId));
        });
        
        container.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => this.deleteTask(btn.dataset.taskId));
        });
    }
    
    createTaskHTML(task) {
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleString('ja-JP') : '未設定';
        const isOverdue = task.is_overdue ? ' (期限切れ)' : '';
        
        return `
            <div class="task-item ${task.is_completed ? 'completed' : ''}">
                <div class="task-content">
                    <div class="task-title ${task.is_completed ? 'completed' : ''}">${task.title}</div>
                    ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                    <div class="task-meta">
                        <span class="priority-badge priority-${task.priority}">
                            ${task.priority === 'high' ? '高' : task.priority === 'medium' ? '中' : '低'}
                        </span>
                        <span>期限: ${dueDate}${isOverdue}</span>
                        <span>作成日: ${new Date(task.created_at).toLocaleDateString('ja-JP')}</span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="toggle-btn" data-task-id="${task.id}">
                        ${task.is_completed ? '未完了にする' : '完了にする'}
                    </button>
                    <button class="delete-btn" data-task-id="${task.id}">削除</button>
                </div>
            </div>
        `;
    }
    
    showMessage(message, type = 'success') {
        const container = document.getElementById('message-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        container.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    new TaskManagerApp();
});