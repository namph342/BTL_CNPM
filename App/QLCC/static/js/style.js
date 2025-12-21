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

// Hàm bật chế độ chỉnh sửa
function enableEditMode() {
        // 1. Tìm tất cả các ô input trong form
    var inputs = document.querySelectorAll('.custom-input');

        // 2. Xóa thuộc tính disabled (cho phép nhập)
    inputs.forEach(function(input) {
        input.removeAttribute('disabled');
        });

        // 3. Ẩn nút "Chỉnh sửa", Hiện nút "Lưu/Hủy"
        document.getElementById('btnEdit').classList.add('d-none');
        document.getElementById('actionButtons').classList.remove('d-none');
    }

    // Hàm hủy bỏ (Load lại trang để quay về cũ)
function cancelEditMode() {
    location.reload();
}
function selectPayment(method) {
        alert("Bạn đã chọn thanh toán qua: " + method + ". (Chức năng này sẽ hiển thị mã QR hoặc hướng dẫn chi tiết)");
        // Sau này bạn sẽ redirect sang trang QR hoặc hiện ảnh QR lên đây
}