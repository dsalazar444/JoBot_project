function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verifica que la cookie empieza con el nombre indicado
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function renderMensajeUsuario(mensaje) {
  const chat_container = document.getElementById("chat-container");

  //Creamos div para el mensaje
  const mensaje_div = document.createElement("div")
  mensaje_div.classList.add("mensaje", "usuario", "w-75", "px-3","py-1","mb-3","rounded","align-self-end");  // Para aplicar estilos
  mensaje_div.setAttribute("data-remitente", "usuario");
  mensaje_div.textContent = mensaje; //textConten es una propiedad de los div, etc. para poner/leer texto dentro de ese elemento

  // Agregar div de mensaje al contenedor principal
  chat_container.appendChild(mensaje_div);

  // Hacer scroll automático hacia abajo en el contenedor principal
  chat_container.scrollTop = chat_container.scrollHeight;

  // Para convertir a json, y obtener atributo de este div especifico
  return estructurarMensaje(mensaje, mensaje_div);
}

function renderMensajeRobot(mensaje) {
  const chat_container = document.getElementById("chat-container");

  //Creamos div para el mensaje
  const mensaje_div = document.createElement("div")
  mensaje_div.classList.add("mensaje", "robot", "w-75", "px-3","py-1", "rounded","align-self-start");  // Para aplicar estilos
  mensaje_div.setAttribute("data-remitente", "robot");
  mensaje_div.textContent = mensaje; //textConten es una propiedad de los div, etc. para poner/leer texto dentro de ese elemento

  // Agregar div de mensaje al contenedor principal
  chat_container.appendChild(mensaje_div);

  // Hacer scroll automático hacia abajo en el contenedor principal 
  chat_container.scrollTop = chat_container.scrollHeight;

  //return estructurarMensaje(mensaje, mensaje_div); //No
  // necesito estructurarlo en json porque ya lo obtengo en json desde el
  // frontend.
}

function estructurarMensaje(mensaje, div){
  const remitente = div.getAttribute("data-remitente");
  const usuario_obj = document.getElementById("sidebar").getAttribute("data-usuario")
  const mensaje_json = {
    texto: mensaje,
    remitente: remitente,
    nivel_sel: nivelSeleccionado,
    usuario: usuario_obj,
  };

  console.log("remitente", remitente, " - texto: ", mensaje," - texto: ", mensaje, );
  
  return mensaje_json;
}
    
  

async function enviarMensajeBack(mensaje_estructurado){
  const response = await fetch("/game_mode/api/mensajes/", {
    method: "POST",
    headers: { "Content-Type": "application/json",
      'X-CSRFToken' : getCookie('csrftoken'),
    },
    body: JSON.stringify(mensaje_estructurado),
  });

  const data = await response.json(); //Porque response es un HTTP, hay que convertirlo a json
  console.log("Objeto recibido:", data.contenido);
  //Revisar si la respuesta fue exitosa
  if (data.success) {
    mensaje_limpio = limpiar_respuesta_ia(data.contenido)
    return mensaje_limpio;
  } else {
    console.error("Error al procesar el mensaje:", data.contenido);
    mensaje_limpio = "Lo siento, hubo un error al procesar tu mensaje.";
  }
}

function limpiar_respuesta_ia(mensaje_json){
  console.log("mensaje_json -<<<<", mensaje_json);
  if (!mensaje_json) return {};

  delete mensaje_json.avanza;
  delete mensaje_json.nivel_acabo;
  
  if (mensaje_json.siguiente_pregunta == null){
    delete mensaje_json.siguiente_pregunta;
  }

  if (mensaje_json.mensaje_despedida == null){
    delete mensaje_json.mensaje_despedida;
  }

  return mensaje_json
}

async function cargarChatPasado() {
  try{
    const response = await fetch("/game_mode/api/cargarChats", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        body: JSON.stringify({nivel: nivelSeleccionado}) //Convertivmos objeto JS a Json
      })


    const data = await response.json();

    console.log("Lista recibida:", data.lista);

    designarDiseñoChatPasado(data);
  } catch (error) {
    console.error("Error obteniendo la lista para cargar chats anteriores:", error);
  }
}

function designarDiseñoChatPasado(data){
  if (!data.success){
    return ;
    };
  
  historial = data.historial;
  historial.forEach(item => {
      const remitente = item.remitente;
      const mensaje = item.contenido;

      if (remitente === "robot"){
        renderMensajeRobot(mensaje);
      }else{
        renderMensajeUsuario(mensaje)
      }

  });

}



// Funcion para que cuando se clickee nivel, este cambie de color y se mantenga hasta que se clickee otro
document.addEventListener("DOMContentLoaded", function () {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const body = document.getElementById('body');
  const input_chat = document.getElementById('input_chat');

  // 1. Activar automáticamente el primer nivel cuando carga la página
  const primer_nivel = document.querySelector('.nivel-item')
  if (primer_nivel){
    primer_nivel.classList.add('active');
    nivelSeleccionado = primer_nivel.getAttribute('data-nivel');
  }

  // Cargamos los mensajes pasados de ese chat:
  cargarChatPasado();

  // 2. Luego escucha los clics en los nivel
  document.querySelectorAll('.nivel-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.nivel-item').forEach(el => {
        el.classList.remove('active');
      });
      this.classList.add('active');

      //Obtenemos el número del nivel
      nivelSeleccionado = this.getAttribute('data-nivel');
      console.log("nivel seleccionado: ", nivelSeleccionado)
      cargarChatPasado(); //Para que cuando cambie de nivel, actualice el historial

      //Mandamos valor a backend (django)
      //Esa es la url a la que mandaremos la info, la cual esta asociada a la función init
      fetch("/game_mode/index", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        body: JSON.stringify({nivel: nivelSeleccionado}) //Convertivmos objeto JS a Json
      })
    });
  });

  sidebarToggle.addEventListener('click', function () {
    // Al elemento con id sidebar, a su lista de clases, añade y quita la clase 'collapsed', si ya está, la quita, y viceversa
    sidebar.classList.toggle('collapsed');
    body.classList.toggle('sidebar-collapsed'); //Necesario porque sidebar y navbar no son hermanas, y necesitamos que cuando el sidebar colapse, los elementos sidebar.collapsed nav {} cambiarles el tamaño, pero con esa regla lo que decimos es que se aplique a elementos nav hijos de sidebar, y esto no pasa, pero nav es hijo de heder-body, entonces necesitamos que este tenga el atributo collapsed

  });

  input_chat.addEventListener("keydown", async (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); //Previene que el enter haga algo propio del navegador (enviar formulario, \n, etc)
      const mensaje = input_chat.value.trim();
  
      if (!mensaje) return; //si la cadena está vacia
  
      const mensaje_json = renderMensajeUsuario(mensaje);  //La respuesta del usuario, lo guardamos como json para mandarla así al backend
      input_chat.value="";
      const respuesta_ia = await enviarMensajeBack(mensaje_json);  //Enviamos mensaje de user al backend, y este nos retona la respuesta de la ia  
      renderMensajeRobot(respuesta_ia);
    }
  })
});

// -------------- Calendario ------------
$(document).ready(function() {
  $('#calendario').datepicker({
    todayHighlight: true ,
    language: "es",
  });
});


