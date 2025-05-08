// Конфигурация API
const API_URL = 'http://localhost:3000/api';

// Класс для работы с паллетами
class PalletManager {
    constructor() {
        this.pallets = [];
        this.form = document.getElementById('palletForm');
        this.palletList = document.getElementById('palletList');
        this.totalPallets = document.getElementById('totalPallets');
        this.activePallets = document.getElementById('activePallets');
        this.repairPallets = document.getElementById('repairPallets');
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadPallets();
        this.updateStatistics();
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const palletData = {
            id: document.getElementById('palletId').value,
            type: document.getElementById('palletType').value,
            status: 'active'
        };

        try {
            const response = await fetch(`${API_URL}/pallets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(palletData)
            });

            if (response.ok) {
                await this.loadPallets();
                this.form.reset();
                this.showNotification('Паллета успешно добавлена', 'success');
            } else {
                throw new Error('Ошибка при добавлении паллеты');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    async loadPallets() {
        try {
            const response = await fetch(`${API_URL}/pallets`);
            if (response.ok) {
                this.pallets = await response.json();
                this.renderPallets();
                this.updateStatistics();
            }
        } catch (error) {
            this.showNotification('Ошибка при загрузке паллет', 'error');
        }
    }

    renderPallets() {
        this.palletList.innerHTML = '';
        
        this.pallets.forEach(pallet => {
            const item = document.createElement('div');
            item.className = 'list-group-item fade-in';
            item.innerHTML = `
                <div>
                    <strong>ID: ${pallet.id}</strong>
                    <span class="ms-2">Тип: ${pallet.type}</span>
                </div>
                <div>
                    <span class="pallet-status status-${pallet.status}">${pallet.status}</span>
                    <button class="btn btn-sm btn-danger ms-2" onclick="palletManager.deletePallet('${pallet.id}')">
                        Удалить
                    </button>
                </div>
            `;
            this.palletList.appendChild(item);
        });
    }

    updateStatistics() {
        this.totalPallets.textContent = this.pallets.length;
        this.activePallets.textContent = this.pallets.filter(p => p.status === 'active').length;
        this.repairPallets.textContent = this.pallets.filter(p => p.status === 'repair').length;
    }

    async deletePallet(id) {
        if (!confirm('Вы уверены, что хотите удалить эту паллету?')) return;

        try {
            const response = await fetch(`${API_URL}/pallets/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadPallets();
                this.showNotification('Паллета успешно удалена', 'success');
            } else {
                throw new Error('Ошибка при удалении паллеты');
            }
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed top-0 end-0 m-3`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.palletManager = new PalletManager();
}); 