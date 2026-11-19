const toggle = document.querySelector('.navbar-toggler');
const navigation = document.getElementById('navbarToggle');

if (toggle && navigation) {
  toggle.addEventListener('click', () => {
    const expanded = navigation.classList.toggle('show');
    toggle.setAttribute('aria-expanded', String(expanded));
  });
}
