// Funcion para que cuando se clickee nivel, este cambie de color y se mantenga hasta que se clickee otro
document.addEventListener("DOMContentLoaded", function () {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const body = document.getElementById('body');

  document.querySelectorAll('.nivel-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.nivel-item').forEach(el => {
        el.classList.remove('active');
      });
      this.classList.add('active');
    });
  });

  sidebarToggle.addEventListener('click', function () {
    // Al elemento con id sidebar, a su lista de clases, añade y quita la clase 'collapsed', si ya está, la quita, y viceversa
    sidebar.classList.toggle('collapsed');
    body.classList.toggle('sidebar-collapsed'); //Necesario porque sidebar y navbar no son hermanas, y necesitamos que cuando el sidebar colapse, los elementos sidebar.collapsed nav {} cambiarles el tamaño, pero con esa regla lo que decimos es que se aplique a elementos nav hijos de sidebar, y esto no pasa, pero nav es hijo de heder-body, entonces necesitamos que este tenga el atributo collapsed

  });
});

// -------------- Calendario ------------
$(document).ready(function() {
  $('#calendario').datepicker({
    todayHighlight: true ,
    language: "es",
  });
});


