document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('voteForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const selectedRegion = document.querySelector('input[name="region_id"]:checked');
            if (!selectedRegion) {
                showMessage('Пожалуйста, выберите регион', 'error');
                return;
            }
            
            const btn = document.getElementById('voteBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Отправка...';
            
            try {
                const formData = new FormData();
                formData.append('region_id', selectedRegion.value);
                
                const response = await fetch('/vote', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('✅ Ваш голос успешно учтён!', 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showMessage('❌ ' + (data.error || 'Ошибка при голосовании'), 'error');
                    btn.disabled = false;
                    btn.textContent = '🗳️ Проголосовать';
                }
            } catch (error) {
                showMessage('❌ Ошибка соединения. Попробуйте позже.', 'error');
                btn.disabled = false;
                btn.textContent = '🗳️ Проголосовать';
            }
        });
    }
});

function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = 'message ' + type;
    
    setTimeout(() => {
        msg.className = 'message';
    }, 5000);
}

document.querySelectorAll('.region-item').forEach(item => {
    item.addEventListener('click', function(e) {
        if (e.target.tagName !== 'INPUT') {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }
        }
    });
});

// Поиск по регионам (дополнительная функция)
function filterRegions(query) {
    const items = document.querySelectorAll('.region-item');
    const searchTerm = query.toLowerCase().trim();
    
    items.forEach(item => {
        const label = item.querySelector('label');
        const text = label.textContent.toLowerCase();
        const code = label.querySelector('.region-code')?.textContent.toLowerCase() || '';
        
        if (text.includes(searchTerm) || code.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}