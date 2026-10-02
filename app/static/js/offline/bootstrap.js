import {
    openDatabase,
    putOutboxItem,
    getAllOutboxItems,
    deleteOutboxItem,
    countPendingItems,
    updateOutboxItem,
    putInmueble,
    getInmuebleByCodigo,
} from "./db.js"

import { syncOutbox } from "./sync.js"

const offlineDatabase = {
    openDatabase,
    putOutboxItem,
    getAllOutboxItems,
    deleteOutboxItem,
    countPendingItems,
};


// Exposición temporal para pruebas desde la consola.
window.emaxOffline = {
    openDatabase,
    putOutboxItem,
    getAllOutboxItems,
    deleteOutboxItem,
    countPendingItems,
    updateOutboxItem,
    putInmueble,
    getInmuebleByCodigo,
    syncOutbox,
    attemptAutomaticSync,
}

window.addEventListener("online", () => {
    attemptAutomaticSync("connection-restored")
})

openDatabase()
    .then(async () => {
        console.log(
            "IndexedDB de EMAX inicializada correctamente"
        )

        if (navigator.onLine) {
            await attemptAutomaticSync("application-start")
        }
    })
    .catch(error => {
        console.error(
            "No se pudo inicializar IndexedDB:",
            error
        )
    })

async function attemptAutomaticSync(reason = "manual") {
    if (!navigator.onLine) {
        return {
            ok: false,
            code: "OFFLINE",
            message: "No hay conexión disponible",
        }
    }

    try {
        console.log(
            `Iniciando sincronización automática: ${reason}`
        )

        const result = await syncOutbox()

        console.log(
            "Resultado de sincronización:",
            result
        )

        window.dispatchEvent(
            new CustomEvent("emax:sync-complete", {
                detail: {
                    reason,
                    ...result,
                },
            })
        )

        return result
    } catch (error) {
        console.error(
            "Error durante la sincronización automática:",
            error
        )

        window.dispatchEvent(
            new CustomEvent("emax:sync-error", {
                detail: {
                    reason,
                    message: error.message,
                },
            })
        )

        return {
            ok: false,
            code: "SYNC_ERROR",
            message: error.message,
        }
    }
}

async function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) {
        console.warn(
            "Este navegador no admite Service Workers"
        )
        return null
    }

    try {
        const registration =
            await navigator.serviceWorker.register(
                "/service-worker.js",
                {
                    scope: "/",
                }
            )

        console.log(
            "Service Worker registrado:",
            registration.scope
        )

        return registration
    } catch (error) {
        console.error(
            "No se pudo registrar el Service Worker:",
            error
        )

        return null
    }
}


window.addEventListener("load", () => {
    registerServiceWorker()
})