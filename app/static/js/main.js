// Highlight active settings nav link based on current hash
function setActiveNavLink() {
    const hash = window.location.hash || '#profile';
    document.querySelectorAll('.settings-nav-link').forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === hash);
    });
}

document.querySelectorAll('.settings-nav-link').forEach(link => {
    link.addEventListener('click', function () {
        document.querySelectorAll('.settings-nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

window.addEventListener('hashchange', setActiveNavLink);
setActiveNavLink();

// Delete account confirmation toggle
const deleteBtn = document.getElementById('delete-account-btn');
const deleteConfirm = document.getElementById('delete-confirm');
const cancelDeleteBtn = document.getElementById('cancel-delete-btn');

if (deleteBtn) {
    deleteBtn.addEventListener('click', function () {
        deleteConfirm.style.display = 'block';
        deleteBtn.style.display = 'none';
    });
}
if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener('click', function () {
        deleteConfirm.style.display = 'none';
        deleteBtn.style.display = 'inline-block';
    });
}
