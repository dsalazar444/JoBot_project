let tiempo = 60; //Tiempo de respuesta en segundos
let intervalo;
let i=0; //Indica en qué pregunta vamos

//Funcion que inicializa timer
function iniciar_contador(contador, icono, sonido, input_btn) {
    intervalo = setInterval(() => {
        tiempo--;
        contador.textContent = tiempo; //Actualizamos tiempo mostrado en UI

        if(tiempo <= 0) {
            detener_contador(input_btn); //Parar el contador, PONER TAMBIEN QUE CUANDO SE DE ENTER SII hay input escrito
            icono.classList.replace("bi-alarm", "bi-alarm-fill");
            sonido.play();
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
        preguntas = respuesta_preg.preguntas //Obtenemos clave de objeto JS
        typeof(preguntas);
        console.log(preguntas)
        if(i < preguntas.length - 1){
            console.log(i);
            texto_pregunta.textContent = preguntas[i];  
            i++;
        } else {
            console.log("Preguntas se acabaron");
        }
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    const contador = document.getElementById('contador');
    const icono_contador = document.getElementById("i-contador");
    const sonido = document.getElementById('sonido-ring');
    const input_btn = document.getElementById('input_chat_multij');
    const texto_pregunta = document.getElementById('preg-text')
    
    //Para que se ponga cuando se ingrese a la página
    try{

        const preguntas_json = await obtener_preguntas();
        iniciar_contador(contador, icono_contador, sonido, input_btn);
        mostrar_pregunta(texto_pregunta, preguntas_json);
        document.getElementById('input_chat_multij').addEventListener('keydown', async (e) => {
            //Si hay un enter y hay contenido escrito, paramos el timer
            if(e.key === "Enter" && !e.shiftKey){
                e.preventDefault();
                if(input_btn.value){
                    detener_contador(input_btn);
                }
            }
        });

        //mostrar_pregunta(texto_pregunta, preguntas_json);
    } catch (error) {
        console.error("Error inicializando la página:", error);
    }
});
