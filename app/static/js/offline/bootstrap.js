import {
    openDatabase,
    putOutboxItem,
    getAllOutboxItems,
    deleteOutboxItem,
    countPendingItems,
    updateOutboxItem,
} from "./db.js";

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
    syncOutbox,
}


openDatabase()
    .then((database) => {
        console.info(
            "IndexedDB de EMAX inicializada correctamente",
        );

        database.close();
    })
    .catch((error) => {
        console.error(
            "No fue posible inicializar IndexedDB",
            error,
        );
    });