document.addEventListener('DOMContentLoaded', function() {
    // Kit butonlarını seç
    const kitButtons = document.querySelectorAll('.kit-btn');
    const rankingTitle = document.getElementById('ranking-title');
    const rankingDescription = document.getElementById('ranking-description');
    const rankingData = document.getElementById('ranking-data');
    
    // Tier renklerini belirle
    const tierClasses = {
        'Tier1': 'tier1',
        'Tier2': 'tier2',
        'Tier3': 'tier3',
        'Tier4': 'tier4',
        'Tier5': 'tier5'
    };
    
    // Kit butonlarına tıklama olayı ekle
    kitButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Önceden seçili butonu temizle
            kitButtons.forEach(btn => btn.classList.remove('active'));
            
            // Şu anki butonu aktif yap
            this.classList.add('active');
            
            // Seçilen kit tipini al
            const kitType = this.getAttribute('data-kit');
            
            // Başlığı güncelle
            rankingTitle.textContent = `${kitType} Kit Sıralaması`;
            rankingDescription.textContent = 'Yükleniyor...';
            
            // Verileri getir ve tabloyu doldur
            fetchKitRankings(kitType);
        });
    });
    
    // Belirli bir kit türü için sıralama verilerini getir
    function fetchKitRankings(kitType) {
        fetch(`/api/kits/${kitType}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Veri alınamadı');
                }
                return response.json();
            })
            .then(data => {
                if (data.users && data.users.length > 0) {
                    displayRankings(data.users);
                    rankingDescription.textContent = `${data.users.length} oyuncu sıralamada`;
                } else {
                    rankingData.innerHTML = '';
                    rankingDescription.textContent = 'Bu kit türü için henüz kayıt bulunmuyor';
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                rankingDescription.textContent = 'Veriler yüklenirken bir hata oluştu';
            });
    }
    
    // Sıralama verilerini tabloda göster
    function displayRankings(users) {
        rankingData.innerHTML = '';
        
        users.forEach((user, index) => {
            const row = document.createElement('tr');
            
            // Tarih biçimlendirme
            const date = new Date(user.date);
            const formattedDate = `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}`;
            
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td><span class="tier-badge ${tierClasses[user.tier]}">${user.tier}</span></td>
                <td>${formattedDate}</td>
            `;
            
            rankingData.appendChild(row);
        });
    }
});