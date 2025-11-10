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

// Guards to avoid duplicate or concurrent loading of past chats for the same level
let isLoadingChatPast = false;
let lastLoadedLevel = null;

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
function renderMensajeRobot(mensaje, es_temp = false) {
  const chat_container = document.getElementById("chat-container");

  //Creamos elemento html div para el mensaje
  let mensaje_div = document.createElement("div")
  mensaje_div.classList.add("mensaje", "robot", "w-75", "px-3","py-1","mb-3", "rounded","align-self-start");  // Para aplicar estilos
  mensaje_div.setAttribute("data-remitente", "robot");

  if(es_temp){
    //Añadimos icono de escribiendo
    mensaje_div = agregarIcono(mensaje_div);
  }else{
    //Aplicamos negrilla
    mensaje_div = aplicarNegrillas(mensaje, mensaje_div); //Si es primer mensaje, no hay problema porque no tendrá ****, entonces retornará el mensaje normal
  }
 
  
  // Agregar div de mensaje al contenedor principal
  chat_container.appendChild(mensaje_div);

  // Hacer scroll automático hacia abajo en el contenedor principal 
  chat_container.scrollTop = chat_container.scrollHeight;

  // Solo retornar el elemento si es temporal (para poder eliminarlo después) DE
  // RESTO NO SE RETORNA NADA
  if(es_temp){
    return mensaje_div;
  }
}

/* Función: Genera div que contiene un icono de escribiendo
  Parametros: mensaje_div -> elemento HTML (es el div del mensaje)
  Retorna: mensaje_div -> elemento HTML (div) con elemento 'i' que es icono de escribiendo
*/
function agregarIcono(mensaje_div){
  const icon = document.createElement("i");
  icon.classList.add("bi", "bi-chat-dots", "fs-4");
  mensaje_div.appendChild(icon);
  mensaje_div.classList.replace("w-75","w-auto");

  return mensaje_div;
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
    // Devolver el contenido para que el llamador sea quien renderice.
    // Esto evita que la respuesta se renderice dos veces (dentro de la función y en el llamador).
    return data.contenido;
  } else {
    console.error("Error al procesar el mensaje:", data.contenido);
    // Retornamos null para que el llamador pueda decidir cómo mostrar el error
    return null;
  }
}

/* Función: Obtiene historial de chats, para que al abrir nivel, salgan los mensajes anteriores */
async function cargarChatPasado() {
  // Evitar llamados duplicados si ya estamos cargando el mismo nivel
  if (isLoadingChatPast && nivelSeleccionado === lastLoadedLevel) {
    console.log('cargarChatPasado: ya se está cargando el historial para el nivel', nivelSeleccionado);
    return;
  }

  isLoadingChatPast = true;
  lastLoadedLevel = nivelSeleccionado;

  console.log('cargarChatPasado: iniciando fetch para nivel', nivelSeleccionado);

  try{
    //Obtenemos historial de chats de nivel seleccionado, y lo "guardamos" en atributo de response 
    const response = await fetch("/game_mode/api/cargarChats/", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        body: JSON.stringify({nivel: nivelSeleccionado}) //Convertivmos objeto JS a Json
      })

    console.log('cargarChatPasado: response status:', response.status);
    
    //Convertimos HTTP (response) a json
    const data = await response.json();
    console.log('cargarChatPasado: data completa recibida:', data);

    //Para que se rendericen según corresponda ('Robot' o 'Usuario')
    designarDiseñoChatPasado(data);
  } catch (error) {
    console.error("Error obteniendo la lista para cargar chats anteriores:", error);
  }
  finally {
    // Marcamos que ya no estamos cargando; permitimos cargar otro nivel si cambia
    isLoadingChatPast = false;
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
  console.log('designarDiseñoChatPasado: entrando con data:', data);
  const input_chat = document.getElementById('input_chat');
  //Si no se pudo obtener historial, que salga
  if (!data.success){
    console.log('designarDiseñoChatPasado: data.success es false, saliendo');
    return ;
    };
  
    //Obtenemos lista historial
  historial = data.historial;
  console.log('designarDiseñoChatPasado: historial array:', historial);
  console.log('designarDiseñoChatPasado: historial.length:', historial.length);
  
  historial.forEach((item, idx) => {
    console.log(`designarDiseñoChatPasado: procesando mensaje ${idx}:`, item);
    
      const remitente = item.remitente;
      const mensaje = item.contenido;
      const esPrimerItem = idx === 0; //Contiene bool

      console.log(`Mensaje ${idx}: remitente=${remitente}, esPrimerItem=${esPrimerItem}, mensaje=`, mensaje);

      if (remitente === "robot"){
        if (esPrimerItem){ 
          //Porque primer elemento es de Robot pero no tiene la misma estructura (dict con claves que genera la ia) que 
          // todas las respuestas de la IA
          console.log(`Renderizando primer mensaje robot como string:`, mensaje);
          renderMensajeRobot(mensaje); //Pasamos un string. No usamos estructurarMensajeConEtiqueta porque mensaje ya es un string
        } else {
          // Convertimos mensaje a json porque funcion estructurarMensajeConEtiqueta espera un json
          console.log(`Intentando parsear mensaje ${idx} a JSON:`, mensaje);
          const mensaje_json = JSON.parse(mensaje);
          console.log(`JSON parseado:`, mensaje_json);
          
          const mensaje_dict_estilizado = estructurarMensajeConEtiqueta(mensaje_json); //Es un dictionario, no un JSON
           //Estilizamos cada parte del diccionario como mensaje de robot, mandando el string que contiene cada key a render
          for (let key in mensaje_dict_estilizado) {
            renderMensajeRobot(mensaje_dict_estilizado[key]);
          }

          //Si el nivel acabó, deshabilitamos input
          if (mensaje_json.nivel_acabo){
            input_chat.disabled = true; 
          }
        }
      } else {
        console.log(`Renderizando mensaje de usuario:`, mensaje);
        renderMensajeUsuario(mensaje);
      }

  });

}

/* Función: A partir de un json con las claves predefinidas de la respuesta del modelo, se estiliza un string con estas.

  Parametros: mensaje -> json con claves definidas en la respuesta del modelo.
  return: mensaje_listo -> string
*/
function estructurarMensajeConEtiqueta(mensaje){

  const mensaje_listo= {
      comentario_entrevistador: `**💬 Comentario del entrevistador:** ${mensaje.respuesta_entrevistador}`,
      retroalimentacion: `**🤖 Retroalimentación de JoBot:** ${mensaje.feedback_instructor}`,
      calificación: `**✅ Calificación obtenida:** ${mensaje.puntaje}.`,
    };
  //Si hay mensaje de despedida, no se muestra siguiente pregunta sino el mensaje de despedida.
  if (mensaje.mensaje_despedida){
    mensaje_listo.despedida = `🤝 ${mensaje.mensaje_despedida}.`
  } else {
    //Si no hay mensaje de despedida,  es porque hay siguiente pregunta y no mensaje de despedida.
  mensaje_listo.prox_pregunta = `**👉 Próxima pregunta:** ${mensaje.siguiente_pregunta}`
  } 

  return mensaje_listo

}

/* Función: Obtenemos de backend, niveles definidos en bd, y nivel actual del user loggeado
Retorna -> lista con esos elementos

*/
async function obtenerNivelActual() {
  try {
    const response = await fetch("/game_mode/api/obtenerNivelAct/");
    const data = await response.json(); //Es un json
    const nivel_act = data.nivel_act;

    return nivel_act;
  } catch (error) {
    console.error("Error:", error);
    return None; 
  }     
  
}

/* Función: Bloqueamos/desbloqueamos input dependiendo de si es su nivel actual o no.

  Parametros: niveles_info -> lista con elemento niveles (los definidos en la
                              bd) y con nivel actual
              input_chat -> div donde se pone input en interfaz
*/
function bloquearInputNiveles(nivel_act, input_chat){

  if (nivel_act){
    console.log("Nivel actual:", nivel_act);
    console.log("Nivel seleccionado:", nivelSeleccionado);

    if(parseInt(nivelSeleccionado) === parseInt(nivel_act)){
      console.log("Desbloqueando input - nivel actual");
      input_chat.disabled = false;
    } else {
      console.log("Bloqueando input - no es nivel actual");
      input_chat.disabled = true;
    }
  } else {
    console.log("Error: nivel_act no definidos");
    input_chat.disabled = true; // Por seguridad, bloquear por defecto
  }
}


//Funciones que se ejecutan siempre que se recargue página
/*Notas:
- Clase 'active' -> Hace que cuando se clickee nivel, este cambie de color y se mantenga hasta que se clickee otro
*/
document.addEventListener("DOMContentLoaded", async function () {
  console.log('DOMContentLoaded: Iniciando carga de página');
  
  try {
    const nivel_actual = await obtenerNivelActual(); //Obtenemos niveles disponibles, y nivel actual
    console.log('Nivel actual recibida:', nivel_actual);
    
    //Obtenemos elemento html
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const body = document.getElementById('body');
    const input_chat = document.getElementById('input_chat');
    const empezar_btn = document.getElementById('empezar-btn');
    const main = document.getElementById('chat-container');
    //Boton de microfono
    const micBtn = document.getElementById('mic-btn');
      /*Objeto de motor de reconocimiento de voz del navegador*/
    const recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'es-ES'; 
    recognition.interimResults = false; // solo devolver resultados finales (no parciales)
    recognition.maxAlternatives = 1;  // solo la mejor interpretación de lo que escuchó
    
    // 1. Activar automáticamente el primer nivel cuando carga la página
    const primer_nivel = document.querySelector('.nivel-item')
    console.log('DOMContentLoaded: primer_nivel encontrado:', primer_nivel);
    
    if (primer_nivel){
      primer_nivel.classList.add('active');
      nivelSeleccionado = primer_nivel.getAttribute('data-nivel');

      //Bloqueamos/desbloqueamos input dependiendo de si es su nivel actual o no.
      bloquearInputNiveles(nivel_actual, input_chat);
      console.log('DOMContentLoaded: nivelSeleccionado establecido a:', nivelSeleccionado);
    }

  //No hay necesidad de limpiar main div, porque no hay nada
  // Cargamos los mensajes pasados de ese chat:
  console.log('DOMContentLoaded: llamando cargarChatPasado()');
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

      //Bloqueamos/desbloqueamos input dependiendo de si es su nivel actual o no.
      bloquearInputNiveles(nivel_actual, input_chat);

      //Mandamos valor de nivel seleccionado a backend (django)
      //Esa es la url a la que mandaremos la info, la cual esta asociada a la función init
      fetch("/game_mode/index/", {
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

  //Cuando el boton sea clickeado
  micBtn.onclick = () => {
    recognition.start(); //Empieza a escuchar

    input_chat.disabled = true; //Deshabilitamos el input mientras escucha

    micBtn.classList.replace("bi-mic", "bi-mic-fill");

  }

  //Se ejecuta cuando el navegador termina de escuchar
  recognition.onresult = async (event) => {
    console.log("procesaré el audio");
    const voice_text = event.results[0][0].transcript;

    console.log(voice_text);
    // Llamamos a la misma función que el Enter
    await procesarMensaje(voice_text);
  }

  //Cuando termina de escuchar
  recognition.onend = () => {
    input_chat.disabled = false; //Habilitamos input
    micBtn.classList.replace("bi-mic-fill", "bi-mic");
  }

  //Si hay un error
  recognition.onerror = () => {
    input_chat.disabled = false;  // asegurarse de habilitarlo si hay error
    micBtn.classList.replace("bi-stop-fill", "bi-mic");
  };

  //Hace que cuando, en imnput-sectionm, cuando se presione Enter, obtengamos el valor en este contenedor
  input_chat.addEventListener("keydown", async (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); //Previene que el enter haga algo propio del navegador (enviar formulario, \n, etc)
      // const mensaje = input_chat.value.trim();

      await procesarMensaje(input_chat.value);
    }
  })
  
  } catch (error) {
    console.error("Error inicializando la página:", error);
  }

  /*Boton de multijugador */
  empezar_btn.addEventListener('click', function() {
    //Obtenemos todos los radios
    const radios = document.getElementsByName('radioDefault');
    let radio_seleccionado = null;

    //Buscamos cuál ha sido seleccionado
    for (const radio of radios){
      if(radio.checked){
        radio_seleccionado = radio.value;
        break;
      }
    }

    switch(radio_seleccionado){
      case 'amigo':
        window.location.href = '';
        break;
      case 'ia':
        window.location.href = '';
        break;
      default:
        alert('Por favor selecciona una opción');
    }

  })

});

// Función común que maneja el envío de cualquier mensaje
async function procesarMensaje(mensaje) {
  //.trim() quita espacios en blanco al inicio y al final del texto
  if (!mensaje.trim()) return; // Evita enviar vacío

   console.log("el mensaje/transcripcion no está vacio");
  //Mensaje enviado del usuario, lo mostramos en la interfaz, y esta funcion nos retorna el mensaje dentro de un json, 
  // que será mandado al backend para que modelo responda
  const mensaje_json = renderMensajeUsuario(mensaje); // Mostrar en UI
  input_chat.value = ""; // Limpiar input

  //Mostramos icono temporal de escribiendo
  const temp_div = renderMensajeRobot("", true);
  try {
    // Enviamos mensaje a backend; la función retorna el contenido de la IA (o null si hubo error)
    const respuesta_ia = await enviarMensajeABackend(mensaje_json);

    //Eliminamos div con icono de esperando
    temp_div.remove();
    if (respuesta_ia) {
      // respuesta_ia es un objeto JSON uniforme que estructurarMensajeConEtiqueta convierte a diccionario con cada respuesta (entrevistador, puntaje, etc.)
      const respuesta_dividida = estructurarMensajeConEtiqueta(respuesta_ia);

      //Estilizamos cada parte del diccionario como mensaje de robot, mandando el string que contiene cada key a render
      for (let key in respuesta_dividida) {
        renderMensajeRobot(respuesta_dividida[key]);
      }
    } else {
      renderMensajeRobot('Lo siento, hubo un error al procesar tu mensaje.');
    }
  } catch (err) {
    console.error(err);
    renderMensajeRobot('Lo siento, hubo un error al procesar tu mensaje.');
  }
}

// -------------- Calendario ------------
$(document).ready(function() {
  $('#calendario').datepicker({
    todayHighlight: true ,
    language: "es",
  });
});


