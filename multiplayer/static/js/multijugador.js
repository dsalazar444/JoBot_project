function correr_contador(contador, icono, sonido) {
    let tiempo = 60; //Tiempo de respuesta en segundos

    const intervalo = setInterval(() => {
        tiempo--;
        contador.textContent = tiempo; //Actualizamos tiempo mostrado en UI

        if(tiempo <= 0) {
            clearInterval(intervalo); //Para el contador, PONER TAMBIEN QUE CUANDO SE DE ENTER
            icono.classList.replace("bi-alarm", "bi-alarm-fill");
            sonido.play();
        }
    }, 1000); //Para que cada ciclo (tiempo--), se ejecute cada 1 segundo (1000 ms)
}

document.addEventListener("DOMContentLoaded", async function () {
    const contador = document.getElementById('contador');
    const icono_contador = document.getElementById("i-contador");
    const sonido = document.getElementById('sonido-ring');

    document.getElementById('div-contador').addEventListener('click', function () {
        //Que cuando se de enter, se 
        correr_contador(contador, icono_contador, sonido);
    });
});
