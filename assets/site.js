'use strict';
document.documentElement.classList.add('js');
const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function closeMenu() { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); }
toggle?.addEventListener('click', () => {
  const opened = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(opened));
  nav.classList.toggle('is-open', opened);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); }
});
document.addEventListener('click', event => {
  if (toggle && !event.target.closest('.site-header')) closeMenu();
});
matchMedia('(min-width:761px)').addEventListener('change', closeMenu);
