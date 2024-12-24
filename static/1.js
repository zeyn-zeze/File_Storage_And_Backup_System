
    function showUpdateForm(userId) {
        // Kullanıcı bilgilerini metin kutuları ile değiştir
        document.getElementById('username-' + userId).style.display = 'none';
        document.getElementById('email-' + userId).style.display = 'none';
        document.getElementById('role-' + userId).style.display = 'none';
        document.getElementById('active-' + userId).style.display = 'none';

        // Güncelleme formunu göster
        document.getElementById('update-form-' + userId).style.display = 'block';

        // Verileri inputlara aktar
        document.getElementById('input-username-' + userId).value = document.getElementById('username-' + userId).innerText;
        document.getElementById('input-email-' + userId).value = document.getElementById('email-' + userId).innerText;
        document.getElementById('input-role-' + userId).value = document.getElementById('role-' + userId).innerText;
        document.getElementById('input-active-' + userId).checked = document.getElementById('active-' + userId).innerText.trim() === 'Evet';
    }
