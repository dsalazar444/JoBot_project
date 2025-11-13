let tiempo; //Tiempo de respuesta en segundos
let intervalo;
let i=0; //Indica en qué pregunta vamos
let j=0; //Indica en qué respuesta vamos

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

//Funcion que inicializa timer
function iniciar_contador(contador, icono, sonido, input_btn, toast_element_time) {
    tiempo = 60; //Para que al pasar a siguiente pregunta, empieze desde 60
    intervalo = setInterval(() => {
        tiempo--;
        contador.textContent = tiempo; //Actualizamos tiempo mostrado en UI

        if(tiempo <= 0) {
            detener_contador(input_btn); //Parar el contador, PONER TAMBIEN QUE CUANDO SE DE ENTER SII hay input escrito
            icono.classList.replace("bi-alarm", "bi-alarm-fill");
            sonido.play();
            mostrar_toast_tiempo_finalizado(toast_element_time);
            //alert("Intentalo de nuevo, !tu puedes!");
        }
    }, 1000); //Para que cada ciclo (tiempo--), se ejecute cada 1 segundo (1000 ms)
}

function detener_contador(input_btn) {
    clearInterval(intervalo);
    input_btn.disabled = true; //Deshabilitamos input
}
//Obtiene preguntas del backend
async function obtener_preguntas() {
    try{
        const response = await fetch('/multiplayer/api/obtenerPreguntas/');
        const data = await response.json(); 
        if(data.success){
            const respuesta_preg = data.respuesta; //Contiene preguntas y respuestas
            console.log("preguntas-respuestas: ", respuesta_preg);
            return data.respuesta;
        }
        console.log("success: ", data.success);
        return null;

    } catch (error) {
        console.error("Error:", error);
    }
}
//texto_pregunta -> es el p donde va la pregunta.
function mostrar_pregunta(texto_pregunta, respuesta_preg){
    if(respuesta_preg){
        const preguntas = respuesta_preg.preguntas //Obtenemos clave de objeto JS
        typeof(preguntas);
        console.log(preguntas);
        if(i < preguntas.length){
            console.log(i);
            const pregunta = preguntas[i];
            texto_pregunta.textContent = pregunta;  
            i++;
            return pregunta;
        } else {
            console.log("Preguntas se acabaron");
            //alert("Partida finalizada");
            return;
        }
    }
}

function obtener_respuesta_ia(respuesta_preg){
     if(respuesta_preg){
        const respuestas = respuesta_preg.respuestas //Obtenemos clave de objeto JS
        console.log(respuestas);
        if(j < respuestas.length){
            console.log(j);
            console.log(respuestas[j]);
            const respuesta =  respuestas[j];
            j++;
            return respuesta;
        } else {
            console.log("Respuestas se acabaron");
            //alert("Partida finalizada");
            return;
        }
    }
}

function render_mensaje_usuario(user_container, mensaje, text_user, es_temp = false){

    if(es_temp){
    
        text_user.textContent = "";
        agregarIcono(user_container);
    } else {
        const iconos = user_container.querySelectorAll('i.bi-chat-dots');
        iconos.forEach(icono => icono.remove());

        text_user.textContent = mensaje;
    }
}

function render_mensaje_ia(ia_container, mensaje, text_ia, es_temp= false){
    if(es_temp){
        // Limpiar contenido anterior y agregar solo el icono
        text_ia.textContent = "";
        agregarIcono(ia_container);
    } else {
        // Limpiar iconos previos del contenedor
        const iconos = ia_container.querySelectorAll('i.bi-chat-dots');
        iconos.forEach(icono => icono.remove());
    
        text_ia.textContent = mensaje;
    }
}

function agregarIcono(div){
  const icon = document.createElement("i");
  icon.classList.add("bi", "bi-chat-dots", "fs-4");
  div.appendChild(icon);
  //mensaje_div.classList.add("w-auto");

  //return div;
}

async function enviar_respuesta_backend(pregunta, respuesta_perf, mensaje){
    const response = await fetch("/multiplayer/api/respuestaUser/", {
        method: 'POST',
        headers: {
          'Content-Type':'application/json', //para indicar envio de json
          'X-CSRFToken' : getCookie('csrftoken') //necesaria para peticiones POST/PUT/DELETE desde JavaScript hacia el backend Django, proque si no este la boquea
        }, 
        body: JSON.stringify({'pregunta': pregunta, 'respuesta_perf': respuesta_perf, 'mensaje': mensaje}) //Convertivmos objeto JS a Json
      });
    
    //Convertimos HTTP (response) a json
    const data = await response.json(); 

  //Revisar si la respuesta fue exitosa
    if (data.success) {
        // Devolver el contenido para que el llamador sea quien renderice.
        // Esto evita que la respuesta se renderice dos veces (dentro de la función y en el llamador).
        console.log("recibido en js: ", data.respuesta);
        return JSON.parse(data.respuesta);
    } else {
        console.error("Error al procesar el mensaje:", data.contenido);
        // Retornamos null para que el llamador pueda decidir cómo mostrar el error
        return null;
    }
}

//Función muestra mensaje de user en UI, llama a función que envia a backend, y
//retorna respuesta de llamada.
async function procesarMensaje(container, mensaje, text_user, input_btn, pregunta, respuesta_ia) {
  //.trim() quita espacios en blanco al inicio y al final del texto
  if (!mensaje.trim()) return; // Evita enviar vacío

   console.log("el mensaje/transcripcion no está vacio");
    //Mensaje enviado del usuario, lo mostramos en la interfaz, y esta funcion nos retorna el mensaje dentro de un json, 
    // que será mandado al backend para que modelo responda
    render_mensaje_usuario(container, mensaje, text_user);
    input_btn.value = ""; // Limpiar input

    const respuesta_json = await enviar_respuesta_backend(pregunta, respuesta_ia, mensaje);
    return respuesta_json;
}

//Actualizamos puntuación
function actualizar_puntaje(puntaje_span, respuesta_json){
    console.log("Tipo:", typeof respuesta_json);
    console.log("Claves disponibles:", Object.keys(respuesta_json));

    //Actualizamos contenido de span
    console.log("puntuacion: ", respuesta_json.puntuacion);
    puntaje_span.textContent = respuesta_json.puntuacion;
}

function reset_puntaje(puntaje_span){
    puntaje_span.textContent = "...";
}

function mostrar_toast(a_mejorar_span, aciertos_span, respuesta_json, toast_element){
    a_mejorar_span.textContent = respuesta_json.a_mejorar;
    aciertos_span.textContent = respuesta_json.aciertos;

    console.log("a mejorar: ", respuesta_json.a_mejorar);
    console.log("aciertos: ", respuesta_json.aciertos);

    // Mostrar el toast
    const toast = new bootstrap.Toast(toast_element);
    toast.show();

    return toast;
}

function mostrar_toast_tiempo_finalizado(toast_element){
    // Mostrar el toast
    const toast = new bootstrap.Toast(toast_element);
    toast.show();
}

function mostrar_toast_partida_finalizada(toast_element){
    // Mostrar el toast
    const toast = new bootstrap.Toast(toast_element);
    toast.show();
}

//ACLARACIÓN
//user_container -> div, text_user -> p
document.addEventListener("DOMContentLoaded", async function () {
    const contador = document.getElementById('contador');
    const icono_contador = document.getElementById("i-contador");
    const sonido = document.getElementById('sonido-ring');
    const input_btn = document.getElementById('input_chat_multij');
    const texto_pregunta = document.getElementById('preg-text');
    const texto_ia = document.getElementById('text-ia');
    const texto_user = document.getElementById('text-jugador');
    const ia_container = document.getElementById('jugador-start');
    const user_container = document.getElementById('jugador-end');
    const puntuacion = document.getElementById('puntuacion');
    const toast_element = document.getElementById('push-up');
    const toast_element_time = document.getElementById('push-up-time');
    const toast_element_finish = document.getElementById('push-up-finish');
    const a_mejorar_span = document.getElementById('a_mejorar');
    const aciertos_span = document.getElementById('aciertos');
    const sig_btn = document.getElementById('sig-btn');
    let toast;
    
    try{

        const preguntas_json = await obtener_preguntas();
        iniciar_contador(contador, icono_contador, sonido, input_btn, toast_element_time);
        let pregunta = mostrar_pregunta(texto_pregunta, preguntas_json);
        let respuesta_ia = obtener_respuesta_ia(preguntas_json);

        render_mensaje_ia(ia_container, "", texto_ia, true);
        render_mensaje_usuario(user_container, "", texto_user, true);

        
        document.getElementById('input_chat_multij').addEventListener('keydown', async (e) => {
            //Si hay un enter y hay contenido escrito, paramos el timer
            if(e.key === "Enter" && !e.shiftKey){
                e.preventDefault();
                const mensaje = input_btn.value;

                if(mensaje){
                    detener_contador(input_btn);
                    render_mensaje_ia(ia_container, respuesta_ia, texto_ia);
                    const respuesta_json = await procesarMensaje(user_container, mensaje, texto_user, input_btn, pregunta, respuesta_ia);

                    if(respuesta_json){
                        actualizar_puntaje(puntuacion, respuesta_json);
                        toast = mostrar_toast(a_mejorar_span, aciertos_span, respuesta_json, toast_element);
                    }

                }
            } else {
                //Para que solo ponga animación cuando el usuario empiece a teclear
                const icono_user = user_container.querySelector('i.bi-chat-dots');
                if(icono_user){
                    icono_user.classList.add('escribiendo');
                }
            }
        });

        sig_btn.addEventListener('click', function () {
            console.log("escuché")
            toast.hide();

            if(i >= preguntas_json.preguntas.length || j >= preguntas_json.respuestas.length) {
                //alert("¡Juego completado! No hay más preguntas.");
                mostrar_toast_partida_finalizada(toast_element_finish);
                return; // No continuar
            }
            iniciar_contador(contador, icono_contador, sonido, input_btn, toast_element_time);

            //Obtenemos la siguiente pregunta
            pregunta = mostrar_pregunta(texto_pregunta, preguntas_json);
            respuesta_ia = obtener_respuesta_ia(preguntas_json);

            render_mensaje_ia(ia_container, "", texto_ia, true);
            render_mensaje_usuario(user_container, "", texto_user, true);
            input_btn.disabled = false; //Volvemos a habilitar input
            reset_puntaje(puntuacion);
        })

        //mostrar_pregunta(texto_pregunta, preguntas_json);
    } catch (error) {
        console.error("Error inicializando la página:", error);
    }
});
