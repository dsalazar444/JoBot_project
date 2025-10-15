//------------------------------------ funciones helpers -------------------------------------
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

//------------------------------------ renderizar -------------------------------------

/* Función: Estiliza y asigna contenedor para mensaje de Usuario, dentro del main
  Parametros: mensaje -> string. Es lo que se mostrará.
  Retorna: mensaje estructurado en json ->

  Importante: retorna un json ->{texto: mensaje, remitente: remitente, nivel_sel: nivelSeleccionado, usuario: usuario_obj}
  Porque será mandado, desde el "main", con un método POST al backend, el cual espera un json
*/
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

  // Para convertir a json, y pasar atributo de este div especifico
  return estructurarMensajeParaBackend(mensaje, mensaje_div);
}

/* Función:  Estiliza y asigna contenedor para mensaje de Robot, dentro del main
  Parametros: mensaje -> string
*/
function renderMensajeRobot(mensaje) {
  const chat_container = document.getElementById("chat-container");

  //Creamos elemento html div para el mensaje
  let mensaje_div = document.createElement("div")
  mensaje_div.classList.add("mensaje", "robot", "w-75", "px-3","py-1","mb-3", "rounded","align-self-start");  // Para aplicar estilos
  mensaje_div.setAttribute("data-remitente", "robot");

  //Aplicamos negrilla
  mensaje_div = aplicarNegrillas(mensaje, mensaje_div) //Si es primer mensaje, no hay problema porque no tendrá ****, entonces retornará el mensaje normal
  
  // Agregar div de mensaje al contenedor principal
  chat_container.appendChild(mensaje_div);

  // Hacer scroll automático hacia abajo en el contenedor principal 
  chat_container.scrollTop = chat_container.scrollHeight;
}

/* Función: Obtiene patrones ** ** (indicadores de negrilla), y se la aplica usando etiquetas html
  Parametros: mensaje -> string
              mensaje_div -> elemento HTML (es el div del mensaje)
  Retorna: mensaje_div -> elemento HTML (div) con etiquetas 'span' y 'strong' para agregar "estilo"
*/
function aplicarNegrillas(mensaje, mensaje_div){
  // Expresión regular para detectar partes entre ** **
  const partes = mensaje.split(/(\*\*.+?\*\*)/g);

  partes.forEach(parte => {
    if (parte.startsWith("**") && parte.endsWith("**")) {
      const strong = document.createElement("strong");
      strong.textContent = parte.slice(2, -2); // Quita los asteriscos
      mensaje_div.appendChild(strong);
    } else {
      const span = document.createElement("span");
      span.textContent = parte;
      mensaje_div.appendChild(span);
    }

  });

  return mensaje_div
}

/* Función: A partir de un string y un contenedor, genera un json con las claves {texto, remitente, mensaje_json}, el cual 
servirá para pasar input recien enviado del usuario, al backend y que el modelo genere una respuesta

  Parametros: mensaje -> string
              div -> elemento HTML (útil porque tiene atributo con información del remitente)
*/
function estructurarMensajeParaBackend(mensaje, div){
  const remitente = div.getAttribute("data-remitente");
  const usuario_obj = document.getElementById("sidebar").getAttribute("data-usuario")
  const mensaje_json = {
    texto: mensaje,
    remitente: remitente,
    nivel_sel: nivelSeleccionado,
    usuario: usuario_obj,
  };
  
  return mensaje_json;
}
    
/* Función: Envia mensaje recien enviado por usuario desde la interfaz, al backend usando fetch con metodo POST

  Parametros: mensaje_estructurado -> json con claves {texto, remitente, mensaje_json}
*/
async function enviarMensajeABackend(mensaje_estructurado){

  //Mandamos json con mensaje desde interfaz, al backend, y guardamos lo que esta nos retorna (respuesta de ia) en variable response
  const response = await fetch("/game_mode/api/mensajes/", {
    method: "POST",
    headers: { "Content-Type": "application/json",
      'X-CSRFToken' : getCookie('csrftoken'),
    },
    body: JSON.stringify(mensaje_estructurado),
  });

  //Convertimos HTTP (response) a json
  const data = await response.json(); 

  //Revisar si la respuesta fue exitosa
  if (data.success) {
    //Renderizamos respuesta
    
    renderMensajeRobot(estructurarMensajeConEtiqueta(data.contenido));
  } else {
    console.error("Error al procesar el mensaje:", data.contenido);
    renderMensajeRobot("Lo siento, hubo un error al procesar tu mensaje.");
  }
}

// function limpiar_respuesta_ia(mensaje_json){
//   console.log("mensaje_json -<<<<", mensaje_json);
//   if (!mensaje_json) return {};

//   delete mensaje_json.avanza;
//   delete mensaje_json.nivel_acabo;
  
//   if (mensaje_json.siguiente_pregunta == null){
//     delete mensaje_json.siguiente_pregunta;
//   }

//   if (mensaje_json.mensaje_despedida == null){
//     delete mensaje_json.mensaje_despedida;
//   }

//   return mensaje_json
// }

/* Función: Obtiene historial de chats, para que al abrir nivel, salgan los mensajes anteriores */
async function cargarChatPasado() {
  try{
    //Obtenemos historial de chats de nivel seleccionado, y lo "guardamos" en atributo de response 
    const response = await fetch("/game_mode/api/cargarChats", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        body: JSON.stringify({nivel: nivelSeleccionado}) //Convertivmos objeto JS a Json
      })

    //Convertimos HTTP (response) a json
    const data = await response.json();

    //Para que se renderizen según corresponda ('Robot' o 'Usuario')
    designarDiseñoChatPasado(data);
  } catch (error) {
    console.error("Error obteniendo la lista para cargar chats anteriores:", error);
  }
}

/* Función: Recorre elementos (diccionarios de mensajes) de una lista historial (mensajes enviados, en orden), obtiene 
su remitente, y con base a esto, los renderiza.

  Parametros: data -> lista de diccionarios con claves {success, historial}, con historial -> diccionario con claves {contenido, remitente, timestamp}
  data -> [
  { success: bool,
    historial: {
          contenido: ,
          remitente: ,
          timestamp: ,
          }
  },
    ...
  ]
*/
function designarDiseñoChatPasado(data){
  //Si no se pudo obtener historial, que salga
  if (!data.success){
    return ;
    };
  
    //Obtenemos lista historial
  historial = data.historial;
  historial.forEach((item, idx) => {
    
      const remitente = item.remitente;
      const mensaje = item.contenido;
      const esPrimerItem = idx === 0; //Contiene bool

      if (remitente === "robot"){
        if (esPrimerItem){ 
          //Porque primer elemento es de Robot pero no tiene la misma estructura (dict con claves que genera la ia) que 
          // todas las respuestas de la IA
          renderMensajeRobot(mensaje); //Pasamos un string. No usamos estructurarMensajeConEtiqueta porque mensaje ya es un string
        } else {
          // Convertimos mensaje a json porque funcion estructurarMensajeConEtiqueta espera un json
          const mensaje_json = JSON.parse(mensaje);
          renderMensajeRobot(estructurarMensajeConEtiqueta(mensaje_json)); 
          //estructurarMensajeConEtiqueta retorna un string, que es lo que espera renderizar..
        }
      } else {
        renderMensajeUsuario(mensaje);
      }

  });

}

/* Función: A partir de un json con las claves predefinidas de la respuesta del modelo, se estiliza un string con estas.

  Parametros: mensaje -> json con claves definidas en la respuesta del modelo.
  return: mensaje_listo -> string
*/
function estructurarMensajeConEtiqueta(mensaje){

  let mensaje_listo;
  //Si hay mensaje de despedida, no se muestra siguiente pregunta sino el mensaje de despedida.
  if (mensaje.mensaje_despedida){
    mensaje_listo = `**💬 Comentario del entrevistador:** ${mensaje.respuesta_entrevistador}

  **🤖 Retroalimentación de JoBot:** ${mensaje.feedback_instructor}

  **✅ Calificación obtenida:** ${mensaje.puntaje}.

  🤝 ${mensaje.mensaje_despedida}.
    `
  } else {
    //Si no hay mensaje de despedida,  es porque hay siguiente pregunta y no mensaje de despedida.
  mensaje_listo = `**💬 Comentario del entrevistador:** ${mensaje.respuesta_entrevistador}

  **🤖 Retroalimentación de JoBot:** ${mensaje.feedback_instructor}

  **✅ Calificación obtenida:** ${mensaje.puntaje}

  **👉 Próxima pregunta:** ${mensaje.siguiente_pregunta}
    `
  } 

  return mensaje_listo

}


//Funciones que se ejecutan siempre que se recargue página
/*Notas:
- Clase 'active' -> Hace que cuando se clickee nivel, este cambie de color y se mantenga hasta que se clickee otro
*/
document.addEventListener("DOMContentLoaded", function () {
  //Obtenemos elemento html
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const body = document.getElementById('body');
  const input_chat = document.getElementById('input_chat');
  const main = document.getElementById('chat-container')

  // 1. Activar automáticamente el primer nivel cuando carga la página
  const primer_nivel = document.querySelector('.nivel-item')
  if (primer_nivel){
    primer_nivel.classList.add('active');
    nivelSeleccionado = primer_nivel.getAttribute('data-nivel');
  }

  //No hay necesidad de limpiar main div, porque no hay nada
  // Cargamos los mensajes pasados de ese chat:
  cargarChatPasado();

  // 2. Luego escucha los clics en los niveles y actualiza variable
  document.querySelectorAll('.nivel-item').forEach(item => {
    item.addEventListener('click', function() {
      document.querySelectorAll('.nivel-item').forEach(el => {
        el.classList.remove('active');
      });
      this.classList.add('active');

      //Obtenemos el número del nivel
      nivelSeleccionado = this.getAttribute('data-nivel');
      
      //Limpiamos elementos html en div
      main.innerHTML = "";
      //Cargamos chats de nivel seleccionado, haciendo que cuando cambie de nivel, actualice el historial
      cargarChatPasado();

      //Mandamos valor de nivel seleccionado a backend (django)
      //Esa es la url a la que mandaremos la info, la cual esta asociada a la función init
      fetch("/game_mode/index", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        //Convierte un valor de JavaScript en una cadena JSON
        body: JSON.stringify({nivel: nivelSeleccionado}) 
      })
    });
  });

  //Hace que cuando se clickee boton de colapsar barra lateral, esta lo haga.
  sidebarToggle.addEventListener('click', function () {
    // Al elemento con id sidebar, a su lista de clases, añade y quita la clase 'collapsed', si ya está, la quita, y viceversa
    sidebar.classList.toggle('collapsed');
    body.classList.toggle('sidebar-collapsed'); //Necesario porque sidebar y navbar no son hermanas, y necesitamos que cuando el sidebar colapse, los elementos sidebar.collapsed nav {} cambiarles el tamaño, pero con esa regla lo que decimos es que se aplique a elementos nav hijos de sidebar, y esto no pasa, pero nav es hijo de heder-body, entonces necesitamos que este tenga el atributo collapsed

  });

  //Hace que cuando, en imnput-sectionm, cuando se presione Enter, obtengamos el valor en este contenedor
  input_chat.addEventListener("keydown", async (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); //Previene que el enter haga algo propio del navegador (enviar formulario, \n, etc)
      const mensaje = input_chat.value.trim();
  
      if (!mensaje) return; //si la cadena está vacia
      
      //Mensaje enviado del usuario, lo mostramos en la interfaz, y esta funcion nos retorna el mensaje dentro de un json, 
      // que será mandado al backend para que modelo responda
      const mensaje_json = renderMensajeUsuario(mensaje); 

      //Limpiamos barra de input
      input_chat.value="";

      //Enviamos mensaje a backend, el cual nos retorna la respuesta de la ia, por lo que la guardamos en variable
      const respuesta_ia = await enviarMensajeABackend(mensaje_json); 
      
      //Mostramos en interfaz la respuesta de la ia, la cual es un json -> lo mandamos a estructurarMensajeConEtiqueta para que lo convierta a string
      renderMensajeRobot(estructurarMensajeConEtiqueta(respuesta_ia));
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


