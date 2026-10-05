import {
    countPendingItems,
    getInmuebleByCodigo,
    putInmueble,
    putOutboxItem,
} from "../offline/db.js"

import {
    syncOutbox,
} from "../offline/sync.js"


// ======================================================
// Elementos generales
// ======================================================

const connectionBadge =
    document.querySelector("#connection-badge")

const pendingCount =
    document.querySelector("#pending-count")

const syncButton =
    document.querySelector("#sync-button")

const syncMessage =
    document.querySelector("#sync-message")


// ======================================================
// Búsqueda de inmuebles
// ======================================================

const searchForm =
    document.querySelector("#inmueble-search-form")

const codeInput =
    document.querySelector("#codigo-inmueble")

const searchButton =
    document.querySelector("#search-button")

const searchMessage =
    document.querySelector("#search-message")

const inmuebleResult =
    document.querySelector("#inmueble-result")

const resultSource =
    document.querySelector("#result-source")

const inmuebleName =
    document.querySelector("#inmueble-name")

const inmuebleCode =
    document.querySelector("#inmueble-code")

const inmuebleAddress =
    document.querySelector("#inmueble-address")

const inmuebleType =
    document.querySelector("#inmueble-type")

const inmuebleRoute =
    document.querySelector("#inmueble-route")

const inmuebleNim =
    document.querySelector("#inmueble-nim")

const inmuebleNit =
    document.querySelector("#inmueble-nit")

const operationSelector =
    document.querySelector("#operation-selector")

const showLecturaButton =
    document.querySelector("#show-lectura-button")

const showErrorButton =
    document.querySelector("#show-error-button")


// ======================================================
// Formulario de lecturas
// ======================================================

const lecturaSection =
    document.querySelector("#lectura-section")

const lecturaInmuebleCode =
    document.querySelector("#lectura-inmueble-code")

const lecturaForm =
    document.querySelector("#lectura-form")

const lecturaValue =
    document.querySelector("#lectura-value")

const mesProceso =
    document.querySelector("#mes-proceso")

const lecturaObservacion =
    document.querySelector("#lectura-observacion")

const fotoContador =
    document.querySelector("#foto-contador")

const fotoInmueble =
    document.querySelector("#foto-inmueble")

const openContadorCamera =
    document.querySelector("#open-contador-camera")

const openInmuebleCamera =
    document.querySelector("#open-inmueble-camera")

const fotoContadorStatus =
    document.querySelector("#foto-contador-status")

const fotoInmuebleStatus =
    document.querySelector("#foto-inmueble-status")

const locationButton =
    document.querySelector("#location-button")

const coordenadaX =
    document.querySelector("#coordenada-x")

const coordenadaY =
    document.querySelector("#coordenada-y")

const saveLecturaButton =
    document.querySelector("#save-lectura-button")

const captureMessage =
    document.querySelector("#capture-message")


// ======================================================
// Formulario de inmuebles con error
// ======================================================

const errorSection =
    document.querySelector("#error-section")

const errorVerificationMessage =
    document.querySelector(
        "#error-verification-message"
    )

const errorForm =
    document.querySelector("#error-form")

const errorCodigoTarjeta =
    document.querySelector("#error-codigo-tarjeta")

const errorDireccionServicio =
    document.querySelector(
        "#error-direccion-servicio"
    )

const errorRuta =
    document.querySelector("#error-ruta")

const errorTarifa =
    document.querySelector("#error-tarifa")

const errorContadorAgua =
    document.querySelector("#error-contador-agua")

const errorObservaciones =
    document.querySelector("#error-observaciones")

const errorFotoContador =
    document.querySelector("#error-foto-contador")

const errorFotoInmueble =
    document.querySelector("#error-foto-inmueble")

const errorFotoContadorStatus =
    document.querySelector(
        "#error-foto-contador-status"
    )

const errorFotoInmuebleStatus =
    document.querySelector(
        "#error-foto-inmueble-status"
    )

const openErrorContadorCamera =
    document.querySelector(
        "#open-error-contador-camera"
    )

const openErrorInmuebleCamera =
    document.querySelector(
        "#open-error-inmueble-camera"
    )

const errorLocationButton =
    document.querySelector(
        "#error-location-button"
    )

const errorCoordenadaX =
    document.querySelector("#error-coordenada-x")

const errorCoordenadaY =
    document.querySelector("#error-coordenada-y")

const saveErrorButton =
    document.querySelector("#save-error-button")

const errorCaptureMessage =
    document.querySelector(
        "#error-capture-message"
    )


// ======================================================
// Cámara
// ======================================================

const cameraDialog =
    document.querySelector("#camera-dialog")

const cameraTitle =
    document.querySelector("#camera-title")

const cameraPreview =
    document.querySelector("#camera-preview")

const cameraCanvas =
    document.querySelector("#camera-canvas")

const cameraMessage =
    document.querySelector("#camera-message")

const cameraCaptureButton =
    document.querySelector(
        "#camera-capture-button"
    )

const cameraCloseButton =
    document.querySelector(
        "#camera-close-button"
    )


// ======================================================
// Estado de la aplicación
// ======================================================

let selectedInmueble = null
let cameraStream = null
let cameraTarget = null

const capturedPhotos = {
    contador: null,
    inmueble: null,
    errorContador: null,
    errorInmueble: null,
}


// Configuración reutilizable de los cuatro destinos
// posibles para las fotografías.

const cameraTargets = {
    contador: {
        title: "Fotografía del contador",
        input: fotoContador,
        status: fotoContadorStatus,
    },

    inmueble: {
        title: "Fotografía del inmueble",
        input: fotoInmueble,
        status: fotoInmuebleStatus,
    },

    errorContador: {
        title: "Fotografía del contador con error",
        input: errorFotoContador,
        status: errorFotoContadorStatus,
    },

    errorInmueble: {
        title: "Fotografía del inmueble con error",
        input: errorFotoInmueble,
        status: errorFotoInmuebleStatus,
    },
}


// ======================================================
// Estado de conexión
// ======================================================

function updateConnectionStatus() {
    const online = navigator.onLine

    connectionBadge.textContent =
        online
            ? "En línea"
            : "Sin conexión"

    connectionBadge.classList.toggle(
        "online",
        online
    )

    connectionBadge.classList.toggle(
        "offline",
        !online
    )

    syncButton.disabled = !online
}


async function updatePendingCount() {
    try {
        pendingCount.textContent =
            await countPendingItems()
    } catch (error) {
        console.error(
            "No se pudo actualizar el contador:",
            error
        )
    }
}


// ======================================================
// Mensajes de interfaz
// ======================================================

function setMessage(
    element,
    baseClass,
    message,
    type = ""
) {
    element.textContent = message
    element.className = baseClass

    if (type) {
        element.classList.add(type)
    }
}


function setSearchMessage(
    message,
    type = ""
) {
    setMessage(
        searchMessage,
        "search-message",
        message,
        type
    )
}


function setCaptureMessage(
    message,
    type = ""
) {
    setMessage(
        captureMessage,
        "capture-message",
        message,
        type
    )
}


function setErrorCaptureMessage(
    message,
    type = ""
) {
    setMessage(
        errorCaptureMessage,
        "capture-message",
        message,
        type
    )
}


// ======================================================
// Valores y fotografías
// ======================================================

function setDefaultProcessMonth() {
    const now = new Date()

    const month = String(
        now.getMonth() + 1
    ).padStart(2, "0")

    mesProceso.value =
        `${now.getFullYear()}${month}`
}


function nullableValue(input) {
    return input.value.trim() || null
}


function getSelectedPhoto(
    type,
    fileInput
) {
    return (
        capturedPhotos[type]
        ?? fileInput.files[0]
        ?? null
    )
}


function updatePhotoStatus(
    statusElement,
    file
) {
    if (!file) {
        statusElement.textContent =
            "Ninguna fotografía seleccionada"

        statusElement.classList.remove(
            "selected"
        )

        return
    }

    statusElement.textContent =
        `Seleccionada: ${file.name}`

    statusElement.classList.add(
        "selected"
    )
}


function resetLecturaPhotos() {
    capturedPhotos.contador = null
    capturedPhotos.inmueble = null

    fotoContador.value = ""
    fotoInmueble.value = ""

    updatePhotoStatus(
        fotoContadorStatus,
        null
    )

    updatePhotoStatus(
        fotoInmuebleStatus,
        null
    )
}


function resetErrorPhotos() {
    capturedPhotos.errorContador = null
    capturedPhotos.errorInmueble = null

    errorFotoContador.value = ""
    errorFotoInmueble.value = ""

    updatePhotoStatus(
        errorFotoContadorStatus,
        null
    )

    updatePhotoStatus(
        errorFotoInmuebleStatus,
        null
    )
}


// ======================================================
// Reinicio de formularios
// ======================================================

function resetLecturaForm() {
    lecturaForm.reset()

    setDefaultProcessMonth()
    resetLecturaPhotos()

    coordenadaX.value = ""
    coordenadaY.value = ""

    setCaptureMessage("")
}


function resetErrorForm({
    preserveContext = false,
} = {}) {
    const code =
        preserveContext
            ? errorCodigoTarjeta.value
            : ""

    const address =
        preserveContext
            ? errorDireccionServicio.value
            : ""

    const route =
        preserveContext
            ? errorRuta.value
            : ""

    errorForm.reset()
    resetErrorPhotos()

    errorCodigoTarjeta.value = code
    errorDireccionServicio.value = address
    errorRuta.value = route

    errorCoordenadaX.value = ""
    errorCoordenadaY.value = ""

    setErrorCaptureMessage("")
}


function hideInmueble() {
    selectedInmueble = null

    resetLecturaForm()
    resetErrorForm()

    operationSelector.hidden = true
    lecturaSection.hidden = true
    errorSection.hidden = true
    inmuebleResult.hidden = true
}


// ======================================================
// Renderizado del inmueble
// ======================================================

function renderInmueble(
    inmueble,
    source
) {
    inmuebleName.textContent =
        inmueble.nombre || "Sin nombre"

    inmuebleCode.textContent =
        inmueble.codigo_tarjeta || "—"

    inmuebleAddress.textContent =
        inmueble.direccion || "—"

    inmuebleType.textContent =
        inmueble.tipo_inmueble || "—"

    inmuebleRoute.textContent =
        inmueble.ruta || "—"

    inmuebleNim.textContent =
        inmueble.nim || "—"

    inmuebleNit.textContent =
        inmueble.nit || "—"

    if (source === "server") {
        resultSource.textContent =
            "Actualizado"

        resultSource.classList.remove(
            "local"
        )
    } else {
        resultSource.textContent =
            "Guardado local"

        resultSource.classList.add(
            "local"
        )
    }

    selectedInmueble = inmueble

    lecturaInmuebleCode.textContent =
        inmueble.codigo_tarjeta

    inmuebleResult.hidden = false
    operationSelector.hidden = false

    // Primero se elige la operación.
    lecturaSection.hidden = true
    errorSection.hidden = true
}


// ======================================================
// Formulario de error
// ======================================================

function showErrorForm({
    code,
    verificationMessage,
    inmueble = null,
}) {
    resetErrorForm()

    errorCodigoTarjeta.value = code

    if (inmueble) {
        errorDireccionServicio.value =
            inmueble.direccion || ""

        errorRuta.value =
            inmueble.ruta || ""
    }

    errorVerificationMessage.textContent =
        verificationMessage

    lecturaSection.hidden = true
    errorSection.hidden = false
}


function showUnverifiedErrorForm(
    code,
    message
) {
    setSearchMessage(
        message,
        "warning"
    )

    showErrorForm({
        code,

        verificationMessage:
            "El código no pudo verificarse. "
            + "Puedes documentar el problema ahora; "
            + "el registro conservará su identificador "
            + "y se sincronizará cuando vuelva la conexión.",
    })
}


// ======================================================
// Caché local y búsqueda
// ======================================================

async function findCachedInmueble(
    code,
    message
) {
    const cachedInmueble =
        await getInmuebleByCodigo(code)

    if (!cachedInmueble) {
        return false
    }

    renderInmueble(
        cachedInmueble,
        "local"
    )

    setSearchMessage(
        message,
        "warning"
    )

    return true
}


async function searchInmueble(code) {
    hideInmueble()

    // Sin conexión se busca únicamente en IndexedDB.
    if (!navigator.onLine) {
        const found =
            await findCachedInmueble(
                code,
                "Inmueble recuperado desde este dispositivo"
            )

        if (!found) {
            showUnverifiedErrorForm(
                code,
                "Sin conexión: el inmueble no está guardado localmente."
            )
        }

        return
    }

    let response

    try {
        response = await fetch(
            `/api/v1/inmuebles/${encodeURIComponent(code)}`,
            {
                credentials: "same-origin",

                headers: {
                    Accept: "application/json",
                },
            }
        )
    } catch (error) {
        console.error(
            "No se pudo consultar el servidor:",
            error
        )

        const found =
            await findCachedInmueble(
                code,
                "No fue posible contactar al servidor. "
                + "Se muestran los datos guardados."
            )

        if (!found) {
            showUnverifiedErrorForm(
                code,
                "No fue posible contactar al servidor "
                + "y el inmueble no está guardado localmente."
            )
        }

        return
    }

    if (response.status === 401) {
        setSearchMessage(
            "La sesión expiró. "
            + "Debes iniciar sesión nuevamente.",
            "error"
        )

        return
    }

    // El servidor confirma que el inmueble no existe.
    if (response.status === 404) {
        setSearchMessage(
            "El servidor confirmó que "
            + "el código no existe.",
            "warning"
        )

        showErrorForm({
            code,

            verificationMessage:
                "El servidor confirmó que este código "
                + "no existe. Registra los datos "
                + "disponibles del inmueble con error.",
        })

        return
    }

    if (!response.ok) {
        const found =
            await findCachedInmueble(
                code,
                "El servidor presentó un problema. "
                + "Se muestran los datos guardados."
            )

        if (!found) {
            setSearchMessage(
                "No se pudo consultar el inmueble: "
                + `HTTP ${response.status}`,
                "error"
            )
        }

        return
    }

    const body =
        await response.json()

    const inmueble =
        body.data

    await putInmueble(inmueble)

    renderInmueble(
        inmueble,
        "server"
    )

    setSearchMessage(
        "Inmueble encontrado y guardado "
        + "para uso offline",
        "success"
    )
}


// ======================================================
// Sincronización manual
// ======================================================

async function synchronize() {
    if (!navigator.onLine) {
        syncMessage.textContent =
            "No hay conexión disponible"

        return
    }

    syncButton.disabled = true

    syncMessage.textContent =
        "Sincronizando…"

    try {
        const result =
            await syncOutbox()

        if (
            result.requires_authentication
        ) {
            syncMessage.textContent =
                "Debes iniciar sesión para sincronizar"
        } else if (
            result.requires_review > 0
        ) {
            syncMessage.textContent =
                `${result.requires_review} `
                + "registro(s) requieren revisión"
        } else {
            syncMessage.textContent =
                `${result.synchronized} `
                + "registro(s) sincronizado(s)"
        }

        await updatePendingCount()
    } catch (error) {
        console.error(error)

        syncMessage.textContent =
            "No se pudo completar la sincronización"
    } finally {
        updateConnectionStatus()
    }
}


// ======================================================
// Geolocalización
// ======================================================

function getCurrentPosition() {
    return new Promise(
        (resolve, reject) => {
            if (!navigator.geolocation) {
                reject(
                    new Error(
                        "El dispositivo no admite "
                        + "geolocalización"
                    )
                )

                return
            }

            navigator.geolocation
                .getCurrentPosition(
                    resolve,
                    reject,
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 30000,
                    }
                )
        }
    )
}


async function fillCoordinates(
    button,
    longitudeInput,
    latitudeInput,
    messageSetter
) {
    button.disabled = true

    messageSetter(
        "Obteniendo ubicación…"
    )

    try {
        const position =
            await getCurrentPosition()

        longitudeInput.value =
            position.coords.longitude

        latitudeInput.value =
            position.coords.latitude

        messageSetter(
            "Ubicación obtenida correctamente",
            "success"
        )
    } catch (error) {
        console.error(error)

        messageSetter(
            "No se pudo obtener la ubicación",
            "error"
        )
    } finally {
        button.disabled = false
    }
}


// ======================================================
// Cámara
// ======================================================

function getCameraErrorMessage(error) {
    const messages = {
        NotAllowedError:
            "El permiso de la cámara fue rechazado.",

        NotFoundError:
            "No se encontró una cámara disponible.",

        NotReadableError:
            "La cámara está siendo utilizada "
            + "por otra aplicación.",

        OverconstrainedError:
            "La cámara no admite la "
            + "configuración solicitada.",

        SecurityError:
            "El navegador bloqueó "
            + "la cámara por seguridad.",
    }

    return (
        messages[error.name]
        ?? error.message
        ?? "No se pudo abrir la cámara."
    )
}


function stopCamera() {
    if (cameraStream) {
        cameraStream
            .getTracks()
            .forEach(
                track => track.stop()
            )
    }

    cameraStream = null
    cameraTarget = null

    cameraPreview.srcObject = null
    cameraCaptureButton.disabled = true
    cameraMessage.textContent = ""

    if (cameraDialog.open) {
        cameraDialog.close()
    }
}


async function openCamera(target) {
    const targetConfig =
        cameraTargets[target]

    if (!targetConfig) {
        throw new Error(
            "Destino de fotografía no válido."
        )
    }

    if (
        !navigator.mediaDevices
        || !navigator.mediaDevices.getUserMedia
    ) {
        throw new Error(
            "Este navegador no permite acceder "
            + "a la cámara. Comprueba que la página "
            + "se abra mediante HTTPS o desde "
            + "127.0.0.1."
        )
    }

    stopCamera()

    cameraTarget = target

    cameraTitle.textContent =
        targetConfig.title

    cameraMessage.textContent =
        "Solicitando acceso a la cámara…"

    cameraDialog.showModal()

    try {
        cameraStream =
            await navigator.mediaDevices
                .getUserMedia({
                    audio: false,

                    video: {
                        facingMode: {
                            ideal: "environment",
                        },

                        width: {
                            ideal: 1920,
                        },

                        height: {
                            ideal: 1080,
                        },
                    },
                })

        cameraPreview.srcObject =
            cameraStream

        await cameraPreview.play()

        cameraCaptureButton.disabled =
            false

        cameraMessage.textContent =
            "Cámara preparada"
    } catch (error) {
        stopCamera()
        throw error
    }
}


function canvasToBlob(canvas) {
    return new Promise(
        (resolve, reject) => {
            canvas.toBlob(
                blob => {
                    if (!blob) {
                        reject(
                            new Error(
                                "No se pudo generar "
                                + "la fotografía."
                            )
                        )

                        return
                    }

                    resolve(blob)
                },

                "image/jpeg",
                0.9
            )
        }
    )
}


async function captureCameraPhoto() {
    if (
        !cameraTarget
        || !cameraStream
    ) {
        throw new Error(
            "La cámara no está preparada."
        )
    }

    const width =
        cameraPreview.videoWidth

    const height =
        cameraPreview.videoHeight

    if (!width || !height) {
        throw new Error(
            "La imagen de la cámara todavía "
            + "no está disponible."
        )
    }

    cameraCanvas.width = width
    cameraCanvas.height = height

    const context =
        cameraCanvas.getContext("2d")

    if (!context) {
        throw new Error(
            "No se pudo preparar la captura."
        )
    }

    context.drawImage(
        cameraPreview,
        0,
        0,
        width,
        height
    )

    const blob =
        await canvasToBlob(cameraCanvas)

    const target = cameraTarget

    const targetConfig =
        cameraTargets[target]

    const file = new File(
        [blob],

        `${target}_${Date.now()}.jpg`,

        {
            type: "image/jpeg",
            lastModified: Date.now(),
        }
    )

    capturedPhotos[target] = file

    // Si existía un archivo seleccionado,
    // la foto tomada con cámara tiene prioridad.
    targetConfig.input.value = ""

    updatePhotoStatus(
        targetConfig.status,
        file
    )

    stopCamera()
}


// ======================================================
// Asociación de inputs y botones de cámara
// ======================================================

function bindFileInput(
    fileInput,
    target,
    statusElement
) {
    fileInput.addEventListener(
        "change",
        () => {
            // Si se selecciona un archivo,
            // se descarta la captura previa de cámara.
            capturedPhotos[target] = null

            updatePhotoStatus(
                statusElement,
                fileInput.files[0] ?? null
            )
        }
    )
}


function bindCameraButton(
    button,
    target,
    messageSetter
) {
    button.addEventListener(
        "click",
        async () => {
            try {
                await openCamera(target)
            } catch (error) {
                console.error(error)

                messageSetter(
                    getCameraErrorMessage(error),
                    "error"
                )
            }
        }
    )
}


bindFileInput(
    fotoContador,
    "contador",
    fotoContadorStatus
)

bindFileInput(
    fotoInmueble,
    "inmueble",
    fotoInmuebleStatus
)

bindFileInput(
    errorFotoContador,
    "errorContador",
    errorFotoContadorStatus
)

bindFileInput(
    errorFotoInmueble,
    "errorInmueble",
    errorFotoInmuebleStatus
)


bindCameraButton(
    openContadorCamera,
    "contador",
    setCaptureMessage
)

bindCameraButton(
    openInmuebleCamera,
    "inmueble",
    setCaptureMessage
)

bindCameraButton(
    openErrorContadorCamera,
    "errorContador",
    setErrorCaptureMessage
)

bindCameraButton(
    openErrorInmuebleCamera,
    "errorInmueble",
    setErrorCaptureMessage
)


// ======================================================
// Eventos del diálogo de cámara
// ======================================================

cameraCaptureButton.addEventListener(
    "click",
    async () => {
        cameraCaptureButton.disabled =
            true

        cameraMessage.textContent =
            "Capturando fotografía…"

        try {
            await captureCameraPhoto()
        } catch (error) {
            console.error(error)

            cameraMessage.textContent =
                getCameraErrorMessage(error)

            cameraCaptureButton.disabled =
                false
        }
    }
)


cameraCloseButton.addEventListener(
    "click",
    stopCamera
)


cameraDialog.addEventListener(
    "cancel",
    event => {
        event.preventDefault()
        stopCamera()
    }
)


window.addEventListener(
    "pagehide",
    stopCamera
)


// ======================================================
// Eventos de geolocalización
// ======================================================

locationButton.addEventListener(
    "click",
    () => {
        fillCoordinates(
            locationButton,
            coordenadaX,
            coordenadaY,
            setCaptureMessage
        )
    }
)


errorLocationButton.addEventListener(
    "click",
    () => {
        fillCoordinates(
            errorLocationButton,
            errorCoordenadaX,
            errorCoordenadaY,
            setErrorCaptureMessage
        )
    }
)


// ======================================================
// Selección de operación
// ======================================================

showLecturaButton.addEventListener(
    "click",
    () => {
        if (!selectedInmueble) {
            return
        }

        errorSection.hidden = true
        lecturaSection.hidden = false

        setCaptureMessage("")

        lecturaSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        })
    }
)


showErrorButton.addEventListener(
    "click",
    () => {
        if (!selectedInmueble) {
            return
        }

        showErrorForm({
            code:
                selectedInmueble.codigo_tarjeta,

            inmueble:
                selectedInmueble,

            verificationMessage:
                "El inmueble existe. "
                + "Registra la incidencia "
                + "encontrada durante la visita.",
        })

        errorSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
        })
    }
)


// ======================================================
// Búsqueda del inmueble
// ======================================================

searchForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault()

        const code =
            codeInput.value.trim()

        if (!code) {
            setSearchMessage(
                "Ingresa el código del inmueble",
                "warning"
            )

            return
        }

        searchButton.disabled = true

        setSearchMessage(
            "Buscando inmueble…"
        )

        try {
            await searchInmueble(code)
        } catch (error) {
            console.error(error)

            setSearchMessage(
                "Ocurrió un error durante la búsqueda",
                "error"
            )
        } finally {
            searchButton.disabled = false
        }
    }
)


// ======================================================
// Guardar lectura en IndexedDB
// ======================================================

lecturaForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault()

        if (!selectedInmueble) {
            setCaptureMessage(
                "Primero debes seleccionar un inmueble",
                "error"
            )

            return
        }

        const contadorFile =
            getSelectedPhoto(
                "contador",
                fotoContador
            )

        const inmuebleFile =
            getSelectedPhoto(
                "inmueble",
                fotoInmueble
            )

        if (
            !contadorFile
            || !inmuebleFile
        ) {
            setCaptureMessage(
                "Las dos fotografías son obligatorias",
                "error"
            )

            return
        }

        if (
            !coordenadaX.value
            || !coordenadaY.value
        ) {
            setCaptureMessage(
                "Debes obtener la ubicación",
                "error"
            )

            return
        }

        saveLecturaButton.disabled = true

        setCaptureMessage(
            "Guardando lectura…"
        )

        try {
            const queuedRecord =
                await putOutboxItem({
                    type: "lectura",

                    endpoint:
                        "/api/v1/lecturas",

                    payload: {
                        codigo_inmueble:
                            selectedInmueble
                                .codigo_tarjeta,

                        lectura:
                            lecturaValue.value
                            || null,

                        observacion:
                            nullableValue(
                                lecturaObservacion
                            ),

                        mes_proceso:
                            mesProceso.value.trim(),

                        coordenada_x:
                            coordenadaX.value,

                        coordenada_y:
                            coordenadaY.value,

                        fecha_captura:
                            new Date()
                                .toISOString(),
                    },

                    files: {
                        foto_contador:
                            contadorFile,

                        foto_inmueble:
                            inmuebleFile,
                    },
                })

            console.log(
                "Lectura guardada en la cola:",
                queuedRecord
            )

            let message =
                "Lectura guardada en el dispositivo"

            let messageType =
                "success"

            await updatePendingCount()

            if (navigator.onLine) {
                const result =
                    await syncOutbox()

                await updatePendingCount()

                if (
                    result.synchronized > 0
                ) {
                    message =
                        "Lectura sincronizada correctamente"
                } else if (
                    result.requires_authentication
                ) {
                    message =
                        "Lectura guardada. "
                        + "Debes iniciar sesión "
                        + "para sincronizar."

                    messageType =
                        "warning"
                } else if (
                    result.requires_review > 0
                ) {
                    message =
                        "Lectura guardada, "
                        + "pero requiere revisión "
                        + "antes de sincronizar."

                    messageType =
                        "warning"
                }
            }

            resetLecturaForm()

            setCaptureMessage(
                message,
                messageType
            )
        } catch (error) {
            console.error(error)

            setCaptureMessage(
                "No se pudo guardar la lectura",
                "error"
            )
        } finally {
            saveLecturaButton.disabled =
                false
        }
    }
)


// ======================================================
// Guardar inmueble con error en IndexedDB
// ======================================================

errorForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault()

        const code =
            errorCodigoTarjeta.value.trim()

        const observations =
            errorObservaciones.value.trim()

        if (!code) {
            setErrorCaptureMessage(
                "El código de tarjeta es obligatorio",
                "error"
            )

            return
        }

        if (!observations) {
            setErrorCaptureMessage(
                "Describe el error encontrado",
                "error"
            )

            return
        }

        if (
            !errorCoordenadaX.value
            || !errorCoordenadaY.value
        ) {
            setErrorCaptureMessage(
                "Debes obtener la ubicación",
                "error"
            )

            return
        }

        // Las dos fotografías son opcionales.
        const contadorFile =
            getSelectedPhoto(
                "errorContador",
                errorFotoContador
            )

        const inmuebleFile =
            getSelectedPhoto(
                "errorInmueble",
                errorFotoInmueble
            )

        saveErrorButton.disabled = true

        setErrorCaptureMessage(
            "Guardando error…"
        )

        try {
            const queuedRecord =
                await putOutboxItem({
                    type: "error",

                    endpoint:
                        "/api/v1/errores",

                    payload: {
                        codigo_tarjeta:
                            code,

                        direccion_servicio:
                            nullableValue(
                                errorDireccionServicio
                            ),

                        ruta:
                            nullableValue(
                                errorRuta
                            ),

                        tarifa:
                            nullableValue(
                                errorTarifa
                            ),

                        contador_agua:
                            nullableValue(
                                errorContadorAgua
                            ),

                        observaciones:
                            observations,

                        coordenada_x:
                            errorCoordenadaX.value,

                        coordenada_y:
                            errorCoordenadaY.value,

                        fecha_captura:
                            new Date()
                                .toISOString(),
                    },

                    files: {
                        foto_contador:
                            contadorFile,

                        foto_inmueble:
                            inmuebleFile,
                    },
                })

            console.log(
                "Error guardado en la cola:",
                queuedRecord
            )

            let message =
                "Error guardado en el dispositivo"

            let messageType =
                "success"

            await updatePendingCount()

            if (navigator.onLine) {
                const result =
                    await syncOutbox()

                await updatePendingCount()

                if (
                    result.synchronized > 0
                ) {
                    message =
                        "Error sincronizado correctamente"
                } else if (
                    result.requires_authentication
                ) {
                    message =
                        "Error guardado. "
                        + "Debes iniciar sesión "
                        + "para sincronizar."

                    messageType =
                        "warning"
                } else if (
                    result.requires_review > 0
                ) {
                    message =
                        "Error guardado, "
                        + "pero requiere revisión "
                        + "antes de sincronizar."

                    messageType =
                        "warning"
                }
            }

            // Conserva código, dirección y ruta para
            // que el usuario vea qué inmueble reportó.
            resetErrorForm({
                preserveContext: true,
            })

            setErrorCaptureMessage(
                message,
                messageType
            )
        } catch (error) {
            console.error(error)

            setErrorCaptureMessage(
                "No se pudo guardar el error",
                "error"
            )
        } finally {
            saveErrorButton.disabled =
                false
        }
    }
)


// ======================================================
// Sincronización y conexión
// ======================================================

syncButton.addEventListener(
    "click",
    synchronize
)


window.addEventListener(
    "online",
    updateConnectionStatus
)


window.addEventListener(
    "offline",
    () => {
        updateConnectionStatus()

        syncMessage.textContent =
            "Las capturas se guardarán "
            + "en este dispositivo"
    }
)


window.addEventListener(
    "emax:sync-complete",
    async event => {
        await updatePendingCount()

        if (
            event.detail.synchronized > 0
        ) {
            syncMessage.textContent =
                `${event.detail.synchronized} `
                + "registro(s) sincronizado(s)"
        }
    }
)


// ======================================================
// Inicialización
// ======================================================

updateConnectionStatus()
await updatePendingCount()
setDefaultProcessMonth()