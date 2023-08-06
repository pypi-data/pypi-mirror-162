const $sidebar_overlay = document.querySelector('.sidebar-overlay');
const $sidebar_toggler = document.querySelector('.sidebar-toggler');
const $sidebar_toggler_icon = $sidebar_toggler.querySelector('i.fas');

const toggleSidebar = function() {
  $sidebar_overlay.classList.toggle('hidden');
  $sidebar_toggler_icon.classList.toggle('fa-bars');
  $sidebar_toggler_icon.classList.toggle('fa-times');
}

$sidebar_toggler.addEventListener('click', toggleSidebar);

