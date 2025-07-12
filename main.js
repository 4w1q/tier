document.addEventListener('DOMContentLoaded', function() {
    // Kit türleri
    const kitTypes = ["Nethpot", "Beast", "Diapot", "Smp", "Axe", "Gapple", "Elytra", "Crystal"];
    const tierColors = {
        "Tier1": "secondary",
        "Tier2": "primary",
        "Tier3": "info",
        "Tier4": "warning",
        "Tier5": "danger"
    };
    
    // Kit butonlarını oluştur
    const kitButtonsContainer = document.getElementById('kitButtons');
    
    kitTypes.forEach(kit => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-outline-primary';
        button.textContent = kit;
        button.addEventListener('click', () => loadKitData(kit));
        kitButtonsContainer.appendChild(button);
    });
    
    // Kit verilerini yükle
    function loadKitData(kitType) {
        // Aktif butonu değiştir
        document.querySelectorAll('#kitButtons button').forEach(btn => {
            if (btn.textContent === kitType) {
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            } else {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            }
        });
        
        // Başlığı güncelle
        document.getElementById('kitTitle').textContent = `${kitType} Kit Sıralaması`;
        
        // Yükleniyor mesajı
        document.getElementById('infoMessage').textContent = "Veriler yükleniyor...";
        document.getElementById('infoMessage').classList.remove('d-none');
        document.getElementById('userList').classList.add('d-none');
        
        // Verileri API'den çek
        fetch(`/api/kits/${kitType}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Veri yüklenirken bir hata oluştu');
                }
                return response.json();
            })
            .then(data => {
                const users = data.users;
                
                if (users.length === 0) {
                    document.getElementById('infoMessage').textContent = 
                        `${kitType} kit türü için henüz kayıt bulunmamaktadır.`;
                    return;
                }
                
                // Kullanıcıları tabloya ekle
                const tableBody = document.getElementById('userListBody');
                tableBody.innerHTML = '';
                
                users.forEach((user, index) => {
                    const row = document.createElement('tr');
                    
                    // Tarih formatını düzenle
                    const date = new Date(user.date);
                    const formattedDate = `${date.toLocaleDateString('tr-TR')}`;
                    
                    // Tier badge rengi
                    const tierBadge = `<span class="badge bg-${tierColors[user.tier] || 'secondary'}">${user.tier}</span>`;
                    
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${user.username}</td>
                        <td>${user.name}</td>
                        <td>${tierBadge}</td>
                        <td>${formattedDate}</td>
                    `;
                    
                    tableBody.appendChild(row);
                });
                
                // Listeyi göster
                document.getElementById('infoMessage').classList.add('d-none');
                document.getElementById('userList').classList.remove('d-none');
            })
            .catch(error => {
                console.error('Hata:', error);
                document.getElementById('infoMessage').textContent = 
                    'Veriler yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.';
            });
    }
    
    // Sayfa yüklendiğinde ilk kit türünü yükle (isteğe bağlı)
    // loadKitData(kitTypes[0]);
});
