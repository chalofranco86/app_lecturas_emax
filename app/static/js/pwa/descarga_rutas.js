import {
    replaceRouteDownload,
    getRouteDownloadMetadata,
    countRouteInmuebles,
} from "../offline/db.js"

console.log(
    "Módulo de descarga de rutas cargado"
)

const form = document.getElementById(
    "route-download-form"
)

const periodInput = document.getElementById(
    "route-period"
)

const routeInput = document.getElementById(
    "route-number"
)

const withoutRouteInput =
    document.getElementById(
        "without-route"
    )

const downloadButton =
    document.getElementById(
        "download-route-button"
    )

const connectionMessage =
    document.getElementById(
        "route-connection-message"
    )

const progressContainer =
    document.getElementById(
        "route-download-progress"
    )

const progressText =
    document.getElementById(
        "route-progress-text"
    )

const resultMessage =
    document.getElementById(
        "route-download-message"
    )

const metadataContainer =
    document.getElementById(
        "route-download-metadata"
    )

const storedPeriod =
    document.getElementById(
        "stored-period"
    )

const storedCount =
    document.getElementById(
        "stored-count"
    )

const storedDate =
    document.getElementById(
        "stored-date"
    )


function normalizeRoute(value) {
    return String(value ?? "").trim()
}


function getSelection() {
    return {
        ruta: normalizeRoute(
            routeInput.value
        ),
        sin_ruta:
            withoutRouteInput.checked,
    }
}


function setResultMessage(
    message,
    type = "info"
) {
    resultMessage.textContent = message
    resultMessage.hidden = false

    resultMessage.className =
        `download-message message-${type}`
}


function hideResultMessage() {
    resultMessage.hidden = true
    resultMessage.textContent = ""
}


function setBusy(isBusy, message = "") {
    downloadButton.disabled =
        isBusy || !navigator.onLine

    periodInput.disabled = isBusy
    withoutRouteInput.disabled = isBusy

    routeInput.disabled =
        isBusy
        || withoutRouteInput.checked

    progressContainer.hidden = !isBusy

    if (message) {
        progressText.textContent = message
    }
}


function formatStoredDate(value) {
    if (!value) {
        return "—"
    }

    /*
     * Limita fracciones de segundo a milisegundos
     * para mantener compatibilidad entre navegadores.
     */
    const normalizedValue = String(value).replace(
        /(\.\d{3})\d+/,
        "$1"
    )

    const date = new Date(normalizedValue)

    if (Number.isNaN(date.getTime())) {
        return String(value)
    }

    return new Intl.DateTimeFormat(
        "es-GT",
        {
            dateStyle: "medium",
            timeStyle: "short",
        }
    ).format(date)
}


function updateConnectionState() {
    if (navigator.onLine) {
        connectionMessage.textContent =
            "Conexión disponible. Puedes descargar "
            + "o actualizar una ruta."

        connectionMessage.className =
            "connection-message message-success"
    } else {
        connectionMessage.textContent =
            "No hay conexión. Las rutas ya descargadas "
            + "continúan disponibles para captura, pero "
            + "no puedes actualizarlas hasta recuperar "
            + "la conexión."

        connectionMessage.className =
            "connection-message message-error"
    }

    downloadButton.disabled =
        !navigator.onLine
}


async function showStoredMetadata() {
    const selection = getSelection()

    if (
        !selection.sin_ruta
        && !selection.ruta
    ) {
        metadataContainer.hidden = true
        return
    }

    try {
        const metadata =
            await getRouteDownloadMetadata(
                selection
            )

        if (!metadata) {
            metadataContainer.hidden = true
            return
        }

        const actualCount =
            await countRouteInmuebles(
                selection
            )

        storedPeriod.textContent =
            metadata.periodo_proceso

        storedCount.textContent =
            String(actualCount)

        storedDate.textContent =
            formatStoredDate(
                metadata.descargado_en
                || metadata.almacenado_en
            )

        metadataContainer.hidden = false
    } catch (error) {
        console.error(
            "No se pudieron consultar los metadatos:",
            error
        )

        metadataContainer.hidden = true
    }
}


function updateRouteControls() {
    if (withoutRouteInput.checked) {
        routeInput.value = ""
        routeInput.disabled = true
    } else {
        routeInput.disabled = false
    }

    showStoredMetadata()
}


async function downloadRoute(event) {
    event.preventDefault()
    hideResultMessage()

    if (!navigator.onLine) {
        setResultMessage(
            "No puedes descargar una ruta sin conexión.",
            "error"
        )
        return
    }

    const periodoProceso =
        periodInput.value.trim()

    const selection = getSelection()

    if (
        !/^\d{4}-(0[1-9]|1[0-2])$/.test(
            periodoProceso
        )
    ) {
        setResultMessage(
            "Selecciona el periodo de proceso.",
            "error"
        )
        periodInput.focus()
        return
    }

    if (
        !selection.sin_ruta
        && !selection.ruta
    ) {
        setResultMessage(
            "Escribe una ruta o selecciona "
            + "“Sin ruta asignada”.",
            "error"
        )
        routeInput.focus()
        return
    }

    const parameters =
        new URLSearchParams({
            periodo_proceso:
                periodoProceso,
        })

    if (selection.sin_ruta) {
        parameters.set("sin_ruta", "1")
    } else {
        parameters.set(
            "ruta",
            selection.ruta
        )
    }

    setBusy(
        true,
        "Descargando información del servidor…"
    )

    try {
        const response = await fetch(
            `/api/v1/inmuebles/descarga-ruta?${parameters}`,
            {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    Accept: "application/json",
                },
            }
        )

        let body

        try {
            body = await response.json()
        } catch {
            throw new Error(
                "El servidor devolvió una respuesta inválida."
            )
        }

        if (!response.ok) {
            const apiMessage =
                body?.message
                || body?.error?.message

            if (response.status === 401) {
                throw new Error(
                    "Tu sesión venció. Inicia sesión "
                    + "nuevamente antes de descargar."
                )
            }

            throw new Error(
                apiMessage
                || `Error HTTP ${response.status}`
            )
        }

        if (
            !body?.ok
            || body.code
                !== "ROUTE_DOWNLOAD_READY"
        ) {
            throw new Error(
                body?.message
                || "La descarga no pudo prepararse."
            )
        }

        setBusy(
            true,
            "Guardando la ruta en el dispositivo…"
        )

        const metadata =
            await replaceRouteDownload(
                body.data
            )

        const actualCount =
            await countRouteInmuebles(
                selection
            )

        if (
            actualCount
            !== metadata.cantidad
        ) {
            throw new Error(
                "La cantidad almacenada no coincide "
                + "con la descarga recibida."
            )
        }

        setResultMessage(
            selection.sin_ruta
                ? `${actualCount} inmuebles sin ruta `
                    + "fueron almacenados correctamente."
                : `La ruta ${selection.ruta} fue `
                    + `actualizada con ${actualCount} `
                    + "inmuebles.",
            "success"
        )

        await showStoredMetadata()
    } catch (error) {
        console.error(
            "No se pudo descargar la ruta:",
            error
        )

        const message =
            !navigator.onLine
                ? "La conexión se perdió durante la "
                    + "descarga. La versión anterior "
                    + "continúa disponible."
                : error.message

        setResultMessage(
            message,
            "error"
        )
    } finally {
        setBusy(false)
        updateConnectionState()
    }
}


form.addEventListener(
    "submit",
    downloadRoute
)

withoutRouteInput.addEventListener(
    "change",
    updateRouteControls
)

routeInput.addEventListener(
    "change",
    showStoredMetadata
)

window.addEventListener(
    "online",
    () => {
        updateConnectionState()
        setResultMessage(
            "La conexión fue restaurada.",
            "success"
        )
    }
)

window.addEventListener(
    "offline",
    () => {
        updateConnectionState()
        setResultMessage(
            "Se perdió la conexión. La descarga "
            + "anterior permanece en el dispositivo.",
            "error"
        )
    }
)

updateRouteControls()
updateConnectionState()
showStoredMetadata()