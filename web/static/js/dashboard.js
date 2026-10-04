const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('sidebar-toggle');
const mainContent = document.getElementById('main-content');

toggleBtn.addEventListener('click', () => {
    const collapsed = sidebar.classList.toggle('sidebar-collapsed');
    mainContent.classList.toggle('sidebar-open', !collapsed);
    toggleBtn.setAttribute('aria-expanded', String(!collapsed));
});
