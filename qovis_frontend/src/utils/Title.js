export function changeTitle(title) {
  const titleEl = document.querySelector('head title');
  titleEl.textContent = title;
}
