// Funcion para que cuando se clickee nivel, este cambie de color y se mantenga hasta que se clickee otro
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.nivel-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.nivel-item').forEach(el => {
        el.classList.remove('active');
      });
      this.classList.add('active');
    });
  });
});
