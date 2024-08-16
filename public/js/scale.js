function scaleContent() {
    const wrapper = document.querySelector('.scale-wrapper');
    const content = document.querySelector('.splitflap');
  
    const scaleX = window.innerWidth / content.offsetWidth;
    const scaleY = window.innerHeight / content.offsetHeight;
    const scale = Math.min(scaleX, scaleY); // Scale uniformly
  
    content.style.transform = `scale(${scale})`;
}
  
// Scale on load and on resize
window.addEventListener('load', scaleContent);
window.addEventListener('resize', scaleContent);
