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
