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
const form = document.querySelector('#inquiry-form');
if (form) {
  form.hidden = false;
  const zh = document.body.dataset.language === 'zh';
  const translate = (en, cn) => zh ? cn : en;
  const query = new URLSearchParams(location.search);
  ['program', 'grade'].forEach(name => {
    const value = query.get(name);
    const select = form.elements[name];
    if ([...select.options].some(option => option.value === value)) select.value = value;
  });
  // Preserve only validated interest selections when switching languages; never personal details.
  const languageLink = document.querySelector('.language-link');
  const safeQuery = new URLSearchParams();
  ['program', 'grade'].forEach(name => { if (form.elements[name].value) safeQuery.set(name, form.elements[name].value); });
  if (safeQuery.size) languageLink.href += '?' + safeQuery.toString();
  let downloadURL;
  form.addEventListener('input', () => {
    document.querySelector('#review').hidden = true;
    document.querySelector('#send-email').removeAttribute('href');
    document.querySelector('#download-request').removeAttribute('href');
    if (downloadURL) { URL.revokeObjectURL(downloadURL); downloadURL = undefined; }
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const value = key => String(data.get(key) || '').trim();
    if (!value('name')) { form.elements.name.setCustomValidity(translate('Please enter your name.', '请输入姓名。')); form.elements.name.reportValidity(); return; }
    const selected = key => form.elements[key].selectedOptions[0].textContent;
    const intent = translate('Trial class request', '体验课申请');
    const message = [
      translate('Hello TTW,', 'TTW 团队您好，'), '', intent, '',
      `${translate('Contact name', '联系人')}: ${value('name')}`,
      `${translate('Contact email', '联系邮箱')}: ${value('email')}`,
      `${translate('Grade group', '年级分组')}: ${selected('grade')}`,
      `${translate('Program interest', '课程兴趣')}: ${selected('program')}`,
      ...(value('timing') ? [`${translate('Preferred timing', '希望的时间')}: ${value('timing')}`] : []),
      ...(value('area') ? [`${translate('Postal area', '邮编区域')}: ${value('area').toUpperCase()}`] : []),
      ...(value('source') ? [`${translate('Heard about TTW through', '了解来源')}: ${selected('source')}`] : []),
      ...(value('notes') ? ['', translate('Interests / questions:', '兴趣 / 问题：'), value('notes')] : []),
      '', translate('Please confirm availability, location, timing, fees and relevant policies. I understand this is an inquiry, not a confirmed booking.', '请确认开班、地点、时间、费用和相关政策。我理解这是咨询申请，不是已确认预约。'),
      translate('I am an adult learner or parent/guardian and agree to be contacted about this inquiry.', '我是成人学习者或家长 / 监护人，同意就此次咨询与我联系。')
    ].join('\n');
    document.querySelector('#request-preview').value = message;
    const subject = `TTW — ${intent} — ${selected('program')}`;
    document.querySelector('#send-email').href = `mailto:${form.dataset.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`;
    if (downloadURL) URL.revokeObjectURL(downloadURL);
    downloadURL = URL.createObjectURL(new Blob([message], {type: 'text/plain;charset=utf-8'}));
    document.querySelector('#download-request').href = downloadURL;
    document.querySelector('#form-status').textContent = '';
    const review = document.querySelector('#review');
    review.hidden = false; review.focus();
    review.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
  });
  form.elements.name.addEventListener('input', () => form.elements.name.setCustomValidity(''));
  document.querySelector('#copy-request').addEventListener('click', async () => {
    const preview = document.querySelector('#request-preview');
    const status = document.querySelector('#form-status');
    try { await navigator.clipboard.writeText(preview.value); status.textContent = translate('Copied. Paste into your email and send it to TTW.', '已复制。请粘贴至邮件并发送给 TTW。'); }
    catch { preview.focus(); preview.select(); status.textContent = translate('Message selected. Use your device’s Copy command, then paste into your email.', '已选中消息。请使用设备的复制功能，再粘贴至邮件。'); }
  });
}

