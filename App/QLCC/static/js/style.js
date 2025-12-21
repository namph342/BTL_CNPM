document.addEventListener("DOMContentLoaded", function () {
    const items = document.querySelectorAll('.ql-item');

    items.forEach(item => {
        item.addEventListener('click', () => {
            items.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // OPTIONAL: điều hướng trang
            const target = item.getAttribute('data-target');
            if (target) {
                window.location.href = `/quanly/${target}`;
            }
        });
    });
});
function enableEditMode() {
    // 1. Mở khóa các ô input (bỏ disabled)
    document.getElementById('priceFields').disabled = false;

    // 2. Hiện nút Lưu và Hủy
    document.getElementById('actionButtons').classList.remove('d-none');

    // 3. Ẩn nút "Chỉnh sửa" ở trên đi cho đỡ rối
    document.getElementById('btnEnableEdit').classList.add('d-none');

    // 4. Đổi dòng trạng thái bên dưới
    document.getElementById('statusFooter').innerHTML = '<small class="text-primary fw-bold"><i class="bi bi-pencil-fill me-1"></i>Đang chỉnh sửa...</small>';
}

function cancelEditMode() {
    // Reload lại trang để quay về dữ liệu cũ và khóa lại
    window.location.reload();
}

window.onload = function () {
    // Uncomment dòng dưới nếu muốn vừa mở lên là hiện bảng in luôn
    // window.print();
}

function selectPayment(type) {
        // 1. Hiển thị khung chi tiết
        document.getElementById('paymentDetails').classList.remove('d-none');

        // 2. Ẩn tất cả nội dung con trước
        document.getElementById('momoContent').classList.add('d-none');
        document.getElementById('bankContent').classList.add('d-none');
        document.getElementById('cashContent').classList.add('d-none');
        document.getElementById('counterContent').classList.add('d-none');

        // 3. Hiện nội dung tương ứng
        if(type === 'momo') document.getElementById('momoContent').classList.remove('d-none');
        if(type === 'bank') document.getElementById('bankContent').classList.remove('d-none');
        if(type === 'cash') document.getElementById('cashContent').classList.remove('d-none');
        if(type === 'counter') document.getElementById('counterContent').classList.remove('d-none');
    }
